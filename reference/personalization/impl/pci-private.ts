/* PCI private-data helpers. Pure migration functions can run in Node tests. */
import type {PrivateRecordV2,PrivateBackupV2,ModuleEventV2} from '../types/PCI_PERSONALIZATION_TYPES.js';
const baseStores=['journal_entries','identity_notes','belief_tests','rehearsals','goal_metrics','quiz_attempts'] as const;
export const STORE_NAMES=[...baseStores,'profile_preferences','goals','beliefs','belief_revisions','evidence_entries','reflection_notes','rehearsal_sessions','activity_events','review_ratings','practice_sessions','scenario_progress','experiments','predicted_outcomes','observed_outcomes','bookmarks','backups','events','program_progress','consents'] as const;
const uuid=/^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
function hash32(s:string,seed:number):number {let h=seed>>>0;for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,0x01000193)>>>0;}return h>>>0;}
/** Deterministic, namespaced UUID-style ID for legacy migration; NOT a security primitive. */
export function legacyImportId(store:string,oldId:string):string {const x=`PCI-legacy-v1\u001f${store}\u001f${oldId}`;let hex=[0x811c9dc5,0x9e3779b9,0x85ebca6b,0xc2b2ae35].map(s=>hash32(x,s).toString(16).padStart(8,'0')).join('');hex=hex.slice(0,12)+'5'+hex.slice(13,16)+'a'+hex.slice(17);return `${hex.slice(0,8)}-${hex.slice(8,12)}-${hex.slice(12,16)}-${hex.slice(16,20)}-${hex.slice(20)}`;}
export interface V1Backup {format:'PCI_PRIVATE_EXPORT';version:1;created_at:string;schema_version:string;source_app:'PSYCHO-CYBERNETICS-INTELLIGENCE';records:Record<string,Record<string,unknown>[]>;}
/** V1 data is never auto-imported. Caller must present plaintext warning and obtain consent. */
export function migrateV1Backup(v1:V1Backup,consentId:string,timeZone:string):PrivateBackupV2{
 if(v1.format!=='PCI_PRIVATE_EXPORT'||v1.version!==1||v1.source_app!=='PSYCHO-CYBERNETICS-INTELLIGENCE')throw new Error('invalid legacy export');
 if(!uuid.test(consentId))throw new Error('explicit consent UUID required');
 if(!timeZone)throw new Error('timeZone required');
 const records:Record<string,PrivateRecordV2[]>={};
 for(const [store,items] of Object.entries(v1.records)){
  if(!(baseStores as readonly string[]).includes(store))throw new Error('unknown legacy store '+store);
  if(!Array.isArray(items))throw new Error('invalid legacy store array');
  records[store]=items.map((data,index)=>{const legacyId=String(data.id??`legacy-position-${index}`);return {id:legacyImportId(store,legacyId),store,created_at:v1.created_at,updated_at:v1.created_at,owner:'user',privacy_mode:'device_local',schema_version:'2.0.0',data:{...data,legacy_original_id:legacyId},refs:[],sensitive:true,consent_id:consentId,legacy_id:legacyId,migrated_from_v1:true};});
 }
 return {format:'PCI_PRIVATE_EXPORT',version:2,created_at:v1.created_at,schema_version:'2.0.0',source_app:'PSYCHO-CYBERNETICS-INTELLIGENCE',metadata:{time_zone:timeZone,included_stores:Object.keys(records),sensitive_data_warning:'Unencrypted unless user explicitly encrypts the file',export_mode:'selected_stores'},records,checksum_sha256:null};
}
export function dryRunImport(value:unknown):{status:'VALID'|'REJECT';total:number;duplicates:string[];stores:string[];errors:string[]}{
 const errors:string[]=[];const duplicate:string[]=[];const seen=new Set<string>();let count=0;let stores:string[]=[];
 if(!value||typeof value!=='object')return {status:'REJECT',total:0,duplicates:[],stores:[],errors:['backup not an object']};
 const b=value as Partial<PrivateBackupV2>;
 if(b.version!==2||b.format!=='PCI_PRIVATE_EXPORT'||b.schema_version!=='2.0.0')errors.push('unsupported export version');
 if(!b.records||typeof b.records!=='object')errors.push('missing records');
 else {stores=Object.keys(b.records);for(const [store,items] of Object.entries(b.records)){
  if(!(STORE_NAMES as readonly string[]).includes(store)){errors.push('unknown store '+store);continue;}
  if(!Array.isArray(items)){errors.push('invalid array for '+store);continue;}
  for(const r of items){count++;if(!r||!uuid.test(r.id)||r.store!==store||r.privacy_mode!=='device_local'||r.owner!=='user'||r.schema_version!=='2.0.0')errors.push('invalid record in '+store);
   if(r.sensitive&&!uuid.test(r.consent_id??''))errors.push('sensitive record missing consent_id');
   const k=store+'|'+r.id;if(seen.has(k))duplicate.push(k);seen.add(k);
  }
 }}
 if(duplicate.length)errors.push('duplicate stable IDs in export');
 return {status:errors.length?'REJECT':'VALID',total:count,duplicates:duplicate,stores,errors};
}

/** Explicit export only. Defaults to excluding sensitive entries, never to publishing them. */
export function buildPrivateBackup(records:Record<string,PrivateRecordV2[]>,timeZone:string,createdAt:string,includeSensitive=false):PrivateBackupV2{
 if(!timeZone||!Number.isFinite(new Date(createdAt).getTime()))throw new Error('valid timezone and timestamp required');
 const safe:Record<string,PrivateRecordV2[]>={};
 for(const [store,items] of Object.entries(records)){
  if(!(STORE_NAMES as readonly string[]).includes(store))throw new Error('unknown store');
  safe[store]=items.filter(r=>includeSensitive||!r.sensitive).map(r=>structuredClone(r));
 }
 return {format:'PCI_PRIVATE_EXPORT',version:2,created_at:createdAt,schema_version:'2.0.0',source_app:'PSYCHO-CYBERNETICS-INTELLIGENCE',metadata:{time_zone:timeZone,included_stores:Object.keys(safe),sensitive_data_warning:'Unencrypted unless user explicitly encrypts the file',export_mode:includeSensitive?'selected_stores':'redacted'},records:safe,checksum_sha256:null};
}
/** Optional corruption detection only, not encryption or authenticity proof. */
export async function checksumPrivateBackup(backup:PrivateBackupV2):Promise<string>{
 if(!globalThis.crypto?.subtle)throw new Error('secure-context crypto unavailable');
 const copy={...backup,checksum_sha256:null};
 const data=new TextEncoder().encode(JSON.stringify(copy));
 const digest=await globalThis.crypto.subtle.digest('SHA-256',data);
 return Array.from(new Uint8Array(digest)).map(x=>x.toString(16).padStart(2,'0')).join('');
}
export async function verifyPrivateBackupChecksum(backup:PrivateBackupV2):Promise<boolean>{
 return !backup.checksum_sha256 || backup.checksum_sha256===await checksumPrivateBackup(backup);
}
/** Validates an existing consent record before a sensitive write. */
export function putPrivateRecord(db:IDBDatabase,record:PrivateRecordV2):Promise<void>{
 if(!(STORE_NAMES as readonly string[]).includes(record.store))return Promise.reject(new Error('invalid store'));
 const names=record.sensitive?[record.store,'consents']:[record.store];
 return new Promise((resolve,reject)=>{
  const tx=db.transaction([...new Set(names)],'readwrite');
  const write=()=>tx.objectStore(record.store).put(record);
  if(record.sensitive){
   if(!record.consent_id){tx.abort();reject(new Error('sensitive record needs explicit consent'));return;}
   const req=tx.objectStore('consents').get(record.consent_id);
   req.onsuccess=()=>{const c=req.result as PrivateRecordV2<{granted:boolean;purpose:string}>|undefined;
    if(!c || c.store!=='consents'||c.data.granted!==true){tx.abort();return;}
    write();
   };
  }else write();
  tx.oncomplete=()=>resolve();tx.onerror=()=>reject(tx.error??new Error('record write failed'));
  tx.onabort=()=>reject(tx.error??new Error('consent absent or record write aborted'));
 });
}

/** Browser-only adapter. There is deliberately no background upload or analytics. */
export function openPrivateDB():Promise<IDBDatabase>{
 if(typeof indexedDB==='undefined')return Promise.reject(new Error('IndexedDB unavailable: do not pretend to save'));
 return new Promise((resolve,reject)=>{
  const request=indexedDB.open('pci-private-v1',2);
  request.onupgradeneeded=()=>{const db=request.result;
   for(const s of STORE_NAMES){if(!db.objectStoreNames.contains(s))db.createObjectStore(s,{keyPath:'id'});}
   const tx=request.transaction!;const ev=tx.objectStore('events');
   if(!ev.indexNames.contains('idempotency_key'))ev.createIndex('idempotency_key','data.idempotency_key',{unique:true});
  };
  request.onsuccess=()=>resolve(request.result);request.onerror=()=>reject(request.error??new Error('open failed'));
  request.onblocked=()=>reject(new Error('Close other tabs to allow database migration'));
 });
}
export function appendEventOnce(db:IDBDatabase,record:PrivateRecordV2<ModuleEventV2>):Promise<'inserted'|'duplicate'>{
 if(record.store!=='events'||!record.data.idempotency_key) return Promise.reject(new Error('event record required'));
 return new Promise((resolve,reject)=>{
  const tx=db.transaction('events','readwrite');const store=tx.objectStore('events');const idx=store.index('idempotency_key');const check=idx.get(record.data.idempotency_key);
  let dup=false;
  check.onsuccess=()=>{if(check.result){dup=true;return;}store.add(record);};
  tx.oncomplete=()=>resolve(dup?'duplicate':'inserted');tx.onerror=()=>reject(tx.error??new Error('event append failed'));tx.onabort=()=>reject(tx.error??new Error('event append aborted'));
 });
}
/** All records in one atomic transaction; UI must call dryRunImport and ask consent before this. */
export async function importBackupAtomic(db:IDBDatabase,backup:PrivateBackupV2):Promise<number>{
 const result=dryRunImport(backup);if(result.status!=='VALID')throw new Error(result.errors.join('; '));
 if(!(await verifyPrivateBackupChecksum(backup)))throw new Error('backup checksum mismatch');
 if(result.stores.length===0)return 0;
 const sensitive=Object.values(backup.records).flat().filter(r=>r.sensitive);
 const stores=[...new Set([...result.stores,...(sensitive.length?['consents']:[])])];
 return new Promise((resolve,reject)=>{const tx=db.transaction(stores,'readwrite');
  const consentMap=new Map((backup.records['consents']??[]).map(c=>[c.id,c]));
  let pending=sensitive.length;let allowed=true;let wrote=false;
  const writeAll=()=>{if(!allowed||pending!==0||wrote)return;wrote=true;
    for(const [store,items] of Object.entries(backup.records))for(const r of items)tx.objectStore(store).put(r);
  };
  if(!pending)writeAll();
  for(const r of sensitive){
   const inBackup=consentMap.get(r.consent_id??'');
   if(inBackup&&inBackup.store==='consents'&&(inBackup.data as {granted?:boolean}).granted===true){pending--;writeAll();continue;}
   const req=tx.objectStore('consents').get(r.consent_id!);
   req.onsuccess=()=>{const c=req.result as PrivateRecordV2<{granted?:boolean}>|undefined;
    if(!c||c.data.granted!==true){allowed=false;tx.abort();return;}
    pending--;writeAll();};
  }
  tx.oncomplete=()=>resolve(result.total);tx.onerror=()=>reject(tx.error??new Error('import failed'));tx.onabort=()=>reject(tx.error??new Error('import aborted: consent or integrity failure'));
 });
}
