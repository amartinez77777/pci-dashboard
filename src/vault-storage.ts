/** Private Knowledge Vault state uses the existing Stage07 IndexedDB v2 stores.
 * No personal records enter public assets. All writes are transaction-bound.
 */
import {openPrivateDB,newRecord,listRecords,DB_VERSION,DB_NAME} from './storage.js';
import type {PrivateRecord,StoreName} from './types.js';
export type KnowledgeAction='bookmark'|'study_plan'|'review';
export interface KnowledgeState {bookmarked:Set<string>;studying:Set<string>;reviewed:Set<string>}
export async function readKnowledgeState():Promise<KnowledgeState>{
 const [b,p,r]=await Promise.all([listRecords('bookmarks'),listRecords('program_progress'),listRecords('review_ratings')]);
 return {bookmarked:new Set(b.filter(x=>(x.data.kind==='knowledge_bookmark'||x.data.kind==='concept_bookmark')).map(x=>String(x.data.target_id))),
 studying:new Set(p.filter(x=>x.data.kind==='manual_study_plan').map(x=>String(x.data.target_id))),
 reviewed:new Set(r.filter(x=>x.data.kind==='manual_concept_review').map(x=>String(x.data.target_id)))};
}
export function knowledgeTargets(rows:PrivateRecord[],targetId:string,kind:string):PrivateRecord[]{return rows.filter(r=>r.data.target_id===targetId&&r.data.kind===kind)}
function persistTransaction<T>(stores:StoreName[],step:(tx:IDBTransaction,done:(value:T)=>void)=>void):Promise<T>{
 return openPrivateDB().then(db=>new Promise<T>((resolve,reject)=>{
  const tx=db.transaction(stores,'readwrite');let result:T;let assigned=false;
  tx.oncomplete=()=>assigned?resolve(result):reject(new Error('Study action did not finish'));
  tx.onerror=()=>reject(tx.error||new Error('Local update failed'));
  tx.onabort=()=>reject(tx.error||new Error('Local update rolled back'));
  try{step(tx,(value)=>{result=value;assigned=true})}catch(err){try{tx.abort()}catch{}reject(err)}
 }));
}
/** Toggle a bookmark or study plan atomically; bookmark.saved follows the Stage07 v2 event envelope.
 * No invented bookmark.removed event type is emitted on deletion.
 */
export async function toggleKnowledgeTarget(action:'bookmark'|'study_plan',targetId:string):Promise<boolean>{
 if(!/^PCI-(?:C|AP|EDU|APP|ACT)-CH\d{2}-\d+$/.test(targetId))throw new Error('Invalid knowledge target ID');
 const store:StoreName=action==='bookmark'?'bookmarks':'program_progress';
 const kind=action==='bookmark'?'knowledge_bookmark':'manual_study_plan';
 const stores:StoreName[]=action==='bookmark'?[store,'events']:[store];
 return persistTransaction<boolean>(stores,(tx,done)=>{
  const os=tx.objectStore(store);const request=os.getAll();
  request.onsuccess=()=>{
   const existing=(request.result as PrivateRecord[]).filter(r=>r.data.target_id===targetId&&(r.data.kind===kind||(action==='bookmark'&&r.data.kind==='concept_bookmark')));
   if(existing.length){for(const rec of existing)os.delete(rec.id);done(false);return}
   const record=newRecord(store,{kind,target_id:targetId,added_at:new Date().toISOString(),source:'knowledge_vault_manual'},[targetId]);
   os.add(record);done(true);
   if(action==='bookmark'){
    const payload={event_id:crypto.randomUUID(),idempotency_key:`bookmark.saved:${record.id}`,event_type:'bookmark.saved',target_id:targetId,timestamp_iso:new Date().toISOString(),time_zone:Intl.DateTimeFormat().resolvedOptions().timeZone||'UTC',session_id:'knowledge-vault',schema_version:'2.0.0',privacy_mode:'device_local',payload:{source:'manual_click',not_assessment:true}};
    tx.objectStore('events').add(newRecord('events',payload,[targetId]));
   }
  };
 });
}
/** A review is an explicit voluntary acknowledgement, never a mastery or performance claim.
 * Stage07 accepts exercise.reviewed with scope=concept_reading in payload; downstream
 * assessments must not treat this as an answer score.
 */
export async function markConceptReviewed(targetId:string):Promise<void>{
 if(!/^PCI-C-CH\d{2}-\d+$/.test(targetId))throw new Error('Not a canonical concept ID');
 const ts=new Date().toISOString(),localDay=new Intl.DateTimeFormat('en-CA',{year:'numeric',month:'2-digit',day:'2-digit',timeZone:Intl.DateTimeFormat().resolvedOptions().timeZone||'UTC'}).format(new Date());
 return persistTransaction<void>(['review_ratings','events'],(tx,done)=>{
  const os=tx.objectStore('review_ratings');const request=os.getAll();
  request.onsuccess=()=>{
   const prev=knowledgeTargets(request.result as PrivateRecord[],targetId,'manual_concept_review').find(r=>r.data.local_day===localDay);
   if(prev){done();return}
   os.add(newRecord('review_ratings',{kind:'manual_concept_review',target_id:targetId,local_day:localDay,completed_at:ts,performance_inference:'none',mastery_claim:false},[targetId]));
   const key=`exercise.reviewed:concept_reading:${targetId}:${localDay}`;
   const evIndex=tx.objectStore('events').index('data.idempotency_key');const lookup=evIndex.get(key);
   lookup.onsuccess=()=>{
    if(lookup.result)return;
    const event={event_id:crypto.randomUUID(),idempotency_key:key,event_type:'exercise.reviewed',target_id:targetId,timestamp_iso:ts,time_zone:Intl.DateTimeFormat().resolvedOptions().timeZone||'UTC',session_id:'knowledge-vault',schema_version:'2.0.0',privacy_mode:'device_local',payload:{scope:'concept_reading',completed_manually:true,knowledge_mastery_not_inferred:true}};
    tx.objectStore('events').add(newRecord('events',event,[targetId]));
   };
   done();
  };
 });
}
export const KNOWLEDGE_STORAGE_CONTRACT={database:DB_NAME,db_version:DB_VERSION,stores:['bookmarks','program_progress','review_ratings','events'],no_public_personal_data:true};
