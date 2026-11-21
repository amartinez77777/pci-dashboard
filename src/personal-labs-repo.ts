/** PCI Stage 10 local transactional repositories. Immutable book data is never written here. */
import {openPrivateDB,getRecord,listRecords,newRecord} from './storage.js';
import type {PrivateRecord,StoreName} from './types.js';
import {normalizeBelief,validateBelief,validateInventory,validateReflection,cleanText} from './personal-labs-model.js';
import type {BeliefInput,BeliefSnapshot,InventoryInput,ReflectionInput,EvidenceInput} from './personal-labs-model.js';

export interface LabRecords {beliefs:PrivateRecord[];revisions:PrivateRecord[];evidence:PrivateRecord[];experiments:PrivateRecord[];observations:PrivateRecord[];inventory:PrivateRecord[];reflections:PrivateRecord[]}
export const LAB_STORES:StoreName[]=['beliefs','belief_revisions','evidence_entries','experiments','observed_outcomes','identity_notes','reflection_notes','events','consents'];
export async function loadLabRecords():Promise<LabRecords>{
 const [beliefs,revisions,evidence,experiments,observations,inventory,reflections]=await Promise.all([
 listRecords('beliefs'),listRecords('belief_revisions'),listRecords('evidence_entries'),listRecords('experiments'),listRecords('observed_outcomes'),listRecords('identity_notes'),listRecords('reflection_notes')]);
 return {beliefs:byUpdated(beliefs),revisions:byUpdated(revisions),evidence:byUpdated(evidence),experiments:byUpdated(experiments),observations:byUpdated(observations),inventory:byUpdated(inventory),reflections:byUpdated(reflections)};
}
function byUpdated(rows:PrivateRecord[]):PrivateRecord[]{return rows.slice().sort((a,b)=>b.updated_at.localeCompare(a.updated_at))}
export function asBelief(rec:PrivateRecord):BeliefSnapshot{return rec.data as unknown as BeliefSnapshot}
export function inDomain(row:PrivateRecord,domain:string):boolean{return row.data.domain===domain}
function uuid():string {if(!globalThis.crypto?.randomUUID)throw Error('A secure context is required for private record IDs.');return globalThis.crypto.randomUUID()}
function tz():string{return Intl.DateTimeFormat().resolvedOptions().timeZone||'UTC'}
function eventRec(type:string,target_id:string,action_id:string,extras:Record<string,unknown>={}):PrivateRecord{
 const now=new Date().toISOString(),event_id=uuid();return newRecord('events',{
 event_id,idempotency_key:action_id,event_type:type,target_id,timestamp_iso:now,time_zone:tz(),session_id:'pci-stage10-local',
 schema_version:type==='experiment.planned'?'2.1.0':'2.0.0',privacy_mode:'device_local',payload:{origin:'PCI_STAGE10',...extras}
 });
}
function consentFor(sensitive:boolean,allowSensitive:boolean,scope:string):{record?:PrivateRecord;id?:string}{
 if(!sensitive)return {};
 if(!allowSensitive)throw Error('Explicit consent is required before saving sensitive personal information.');
 const record=newRecord('consents',{scope,purpose:'User-approved private browser storage',explicit:true,consent_at:new Date().toISOString()});
 return {record,id:record.id};
}
function safeRecord(store:StoreName,data:Record<string,unknown>,refs:string[],sensitive:boolean,consent_id?:string):PrivateRecord{
 return newRecord(store,data,refs,sensitive,consent_id);
}
/** Commit all records in one IndexedDB transaction; Promise only resolves after transaction completes. */
function atomicPut(records:PrivateRecord[]):Promise<void>{
 if(!records.length)return Promise.resolve();
 return openPrivateDB().then(db=>new Promise<void>((resolve,reject)=>{
  const tx=db.transaction([...new Set(records.map(r=>r.store))],'readwrite');
  tx.oncomplete=()=>resolve();tx.onabort=()=>reject(tx.error||Error('Atomic private write aborted.'));
  tx.onerror=()=>reject(tx.error||Error('Private write failed.'));
  for(const row of records)tx.objectStore(row.store).put(row);
 }));
}
function evidenceRows(belief_id:string,revision_id:string,input:BeliefInput,sensitive:boolean,consent_id?:string):PrivateRecord[]{
 const flat:[EvidenceInput,'supporting'|'counter'][]=[...input.evidence_for.map(x=>[x,'supporting'] as [EvidenceInput,'supporting']),...input.evidence_against.map(x=>[x,'counter'] as [EvidenceInput,'counter'])];
 return flat.map(([entry,kind])=>safeRecord('evidence_entries',{
  belief_id,revision_id,kind,observation:entry.observation,occurred_on:entry.occurred_on,interpretation_note:entry.interpretation_note||'',snapshot_only:true
 },[belief_id,...input.concept_ids],sensitive,consent_id));
}
function plannedExperiment(belief_id:string,revision_id:string,info:BeliefInput,sensitive:boolean,consent_id?:string):PrivateRecord|null{
 if(!info.small_action.trim())return null;
 return safeRecord('experiments',{
  belief_id,revision_id,kind:'user_planned',action:info.small_action,prediction:info.prediction,follow_up_date:info.follow_up_date,status:'planned',
  safety_note:'Optional small action. Pause or change it if unsafe or uncomfortable.'
 },[belief_id,...info.concept_ids],sensitive,consent_id);
}
/** Create a saved draft or new belief; full revision snapshot is created immediately. */
export async function createBelief(input:BeliefInput,opts:{status?:'active'|'draft';sensitive:boolean;consented:boolean}):Promise<PrivateRecord>{
 const status=opts.status||'active',errors=validateBelief(input,status);if(errors.length)throw Error(errors.join(' '));
 const clean=normalizeBelief(input),consent=consentFor(opts.sensitive,opts.consented,'belief reconstruction');
 const time=new Date().toISOString();const snap:BeliefSnapshot={...clean,status,revision_number:1,first_saved_at:time,latest_reviewed_at:null};
 const rec=safeRecord('beliefs',snap as unknown as Record<string,unknown>,clean.concept_ids,opts.sensitive,consent.id);
 const rev=safeRecord('belief_revisions',{belief_id:rec.id,revision_number:1,action:'created',before:null,after:snap,recorded_at:time},[rec.id,...clean.concept_ids],opts.sensitive,consent.id);
 const planned=status==='active'?plannedExperiment(rec.id,rev.id,clean,opts.sensitive,consent.id):null;
 const extras=planned?[eventRec('experiment.planned',planned.id,uuid(),{belief_id:rec.id})]:[];
 await atomicPut([...(consent.record?[consent.record]:[]),rec,rev,...evidenceRows(rec.id,rev.id,clean,opts.sensitive,consent.id),...(planned?[planned]:[]),eventRec('belief.created',rec.id,uuid(),{status}),...extras]);return rec;
}
/** Updates compare the expected updated_at inside one read/write transaction to prevent lost edits. */
export async function reviseBelief(belief_id:string,expected_updated_at:string,input:BeliefInput,opts:{status:'active'|'draft';sensitive:boolean;consented:boolean}):Promise<PrivateRecord>{
 const errors=validateBelief(input,opts.status);if(errors.length)throw Error(errors.join(' '));
 const clean=normalizeBelief(input);const existing=await getRecord('beliefs',belief_id);if(existing?.sensitive&&!opts.sensitive)throw Error('This record includes sensitive prior snapshots. Keep sensitive storage enabled or delete this record and its history.');const consent=consentFor(opts.sensitive,opts.consented,'belief revision');const db=await openPrivateDB();
 return new Promise<PrivateRecord>((resolve,reject)=>{
  const tx=db.transaction(LAB_STORES,'readwrite');let updated:PrivateRecord|undefined;
  tx.oncomplete=()=>updated?resolve(updated):reject(Error('Revision was not committed.'));
  tx.onerror=()=>reject(tx.error||Error('Revision failed.'));
  tx.onabort=()=>reject(tx.error||Error('Revision was canceled or conflicted.'));
  const get=tx.objectStore('beliefs').get(belief_id);
  get.onsuccess=()=>{
   const prior=get.result as PrivateRecord|undefined;
   if(!prior||prior.updated_at!==expected_updated_at){tx.abort();return}
   const revNumber=Number(prior.data.revision_number||0)+1,time=new Date().toISOString();
   const snap:BeliefSnapshot={...clean,status:opts.status,revision_number:revNumber,first_saved_at:String(prior.data.first_saved_at||prior.created_at),latest_reviewed_at:String(prior.data.latest_reviewed_at||'')||null};
   updated={...prior,data:snap as unknown as Record<string,unknown>,refs:clean.concept_ids,updated_at:time,sensitive:opts.sensitive,consent_id:opts.sensitive?consent.id:undefined};
   const rev=safeRecord('belief_revisions',{belief_id,revision_number:revNumber,action:'revised',before:prior.data,after:snap,recorded_at:time},[belief_id,...clean.concept_ids],opts.sensitive,consent.id);
   const oldAction=String(prior.data.small_action||''),oldPrediction=String(prior.data.prediction||'');
   const planned=opts.status==='active'&&(clean.small_action!==oldAction||clean.prediction!==oldPrediction)?plannedExperiment(belief_id,rev.id,clean,opts.sensitive,consent.id):null;
   const records=[...(consent.record?[consent.record]:[]),updated,rev,...evidenceRows(belief_id,rev.id,clean,opts.sensitive,consent.id),eventRec('belief.revised',belief_id,uuid(),{revision_number:revNumber}),...(planned?[planned,eventRec('experiment.planned',planned.id,uuid(),{belief_id})]:[])];
   for(const row of records)tx.objectStore(row.store).put(row);
  };
 });
}
/** Partial observations and journal reflections each retain prior dated snapshots on editing. */
export async function saveInventory(input:InventoryInput,opts:{existing?:PrivateRecord;sensitive:boolean;consented:boolean}):Promise<PrivateRecord>{
 const errors=validateInventory(input);if(errors.length)throw Error(errors.join(' '));
 if(opts.existing?.sensitive&&!opts.sensitive)throw Error('Earlier snapshots contain sensitive content; keep this record sensitive or delete its history.');const consent=consentFor(opts.sensitive,opts.consented,'self-image inventory');const old=opts.existing;
 const history=old?([...(Array.isArray(old.data.history)?old.data.history:[]),{at:old.updated_at,previous:{...old.data,history:undefined}}]):[];
 const data:Record<string,unknown>={domain:input.domain,self_description:cleanText(input.self_description),context:cleanText(input.context),observation:cleanText(input.observation),goal:cleanText(input.goal),concept_ids:input.concept_ids,history};
 const rec=old?{...old,data,refs:input.concept_ids,updated_at:new Date().toISOString(),sensitive:opts.sensitive,consent_id:opts.sensitive?consent.id:undefined}:safeRecord('identity_notes',data,input.concept_ids,opts.sensitive,consent.id);
 await atomicPut([...(consent.record?[consent.record]:[]),rec,eventRec('journal.saved',rec.id,uuid(),{kind:'self_image_inventory',edited:Boolean(old)})]);return rec;
}
export async function saveReflection(input:ReflectionInput,opts:{existing?:PrivateRecord;sensitive:boolean;consented:boolean}):Promise<PrivateRecord>{
 const errors=validateReflection(input);if(errors.length)throw Error(errors.join(' '));
 if(opts.existing?.sensitive&&!opts.sensitive)throw Error('Earlier snapshots contain sensitive content; keep this record sensitive or delete its history.');const consent=consentFor(opts.sensitive,opts.consented,'reflection');const old=opts.existing;
 const history=old?([...(Array.isArray(old.data.history)?old.data.history:[]),{at:old.updated_at,previous:{...old.data,history:undefined}}]):[];
 const data:Record<string,unknown>={domain:input.domain,prompt:cleanText(input.prompt),observation:cleanText(input.observation),interpretation:cleanText(input.interpretation),next_step:cleanText(input.next_step),belief_id:input.belief_id,concept_ids:input.concept_ids,history};
 const refs=[...(input.belief_id?[input.belief_id]:[]),...input.concept_ids];
 const rec=old?{...old,data,refs,updated_at:new Date().toISOString(),sensitive:opts.sensitive,consent_id:opts.sensitive?consent.id:undefined}:safeRecord('reflection_notes',data,refs,opts.sensitive,consent.id);
 await atomicPut([...(consent.record?[consent.record]:[]),rec,eventRec('journal.saved',rec.id,uuid(),{kind:'reflection',edited:Boolean(old)})]);return rec;
}
export async function recordOutcome(experiment_id:string,what_happened:string,opts:{sensitive:boolean;consented:boolean;reflection?:string}):Promise<PrivateRecord>{
 if(!cleanText(what_happened))throw Error('An observed result is required; it may be brief.');
 const current=await getRecord('experiments',experiment_id);if(!current)throw Error('Experiment does not exist.');
 const consent=consentFor(opts.sensitive,opts.consented,'experiment observation');const now=new Date().toISOString();
 const outcome=safeRecord('observed_outcomes',{experiment_id,belief_id:current.data.belief_id,observed_at:now,what_happened:cleanText(what_happened),reflection:cleanText(opts.reflection)},[experiment_id,String(current.data.belief_id)],opts.sensitive,consent.id);
 const revised={...current,updated_at:now,data:{...current.data,status:'observed',observed_outcome_id:outcome.id}};
 await atomicPut([...(consent.record?[consent.record]:[]),outcome,revised,eventRec('experiment.outcome_recorded',experiment_id,uuid(),{outcome_id:outcome.id})]);return outcome;
}
export async function removePersonalRecord(store:'identity_notes'|'reflection_notes',id:string):Promise<void>{
 const found=await getRecord(store,id);if(!found)return;const db=await openPrivateDB();
 return new Promise((resolve,reject)=>{const tx=db.transaction([store,'events'],'readwrite');tx.oncomplete=()=>resolve();tx.onabort=()=>reject(tx.error||Error('Deletion failed.'));tx.onerror=()=>reject(tx.error||Error('Deletion failed.'));tx.objectStore(store).delete(id);const get=tx.objectStore('events').getAll();get.onsuccess=()=>{for(const e of get.result as PrivateRecord[]){if(e.data.target_id===id)tx.objectStore('events').delete(e.id)}}});
}
/** Erase a belief, all its sensitive snapshots/evidence/experiments and associated minimal events. */
export async function deleteBeliefCascade(id:string):Promise<number>{
 const db=await openPrivateDB();const stores:StoreName[]=['beliefs','belief_revisions','evidence_entries','experiments','predicted_outcomes','observed_outcomes','reflection_notes','events'];
 return new Promise((resolve,reject)=>{let removed=0;const tx=db.transaction(stores,'readwrite');
  tx.oncomplete=()=>resolve(removed);tx.onerror=()=>reject(tx.error||Error('Cascade delete failed.'));tx.onabort=()=>reject(tx.error||Error('Cascade delete aborted.'));
  const all:Partial<Record<StoreName,PrivateRecord[]>>={};let remaining=stores.length;
  for(const store of stores){const req=tx.objectStore(store).getAll();req.onsuccess=()=>{
   all[store]=req.result as PrivateRecord[];remaining--;
   if(remaining!==0)return;
   // Determine the transitive targets BEFORE deleting event records, in one atomic transaction.
   const related=new Set([id]);
   for(const name of stores.filter(s=>s!=='events'&&s!=='reflection_notes'))for(const row of all[name]||[]){
    if(row.id===id||row.data.belief_id===id||row.refs.includes(id))related.add(row.id);
   }
   for(const name of stores)for(const row of all[name]||[]){
    if(name==='reflection_notes') {if(row.data.belief_id===id||row.refs.includes(id))tx.objectStore(name).put({...row,data:{...row.data,belief_id:null,source_belief_deleted:true},refs:row.refs.filter(ref=>ref!==id),updated_at:new Date().toISOString()});continue}
    const references=row.refs.some(x=>related.has(x));
    const isTarget=related.has(row.id)||related.has(String(row.data.belief_id||''))||related.has(String(row.data.target_id||''))||related.has(String(row.data.experiment_id||''))||references;
    if(isTarget){tx.objectStore(name).delete(row.id);removed++}
   }
  }};
 });
}
export function revisionFor(belief_id:string,revisions:PrivateRecord[]):PrivateRecord[]{return revisions.filter(r=>r.data.belief_id===belief_id).sort((a,b)=>Number(a.data.revision_number)-Number(b.data.revision_number))}
export function experimentFor(belief_id:string,experiments:PrivateRecord[]):PrivateRecord[]{return experiments.filter(r=>r.data.belief_id===belief_id)}
