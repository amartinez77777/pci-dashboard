import type {PrivateRecord,StoreName} from './types.js';
// v2 exactly follows Stage 07 PCI_INDEXEDDB_CONTRACT.json. Never store book records here.
export const DB_NAME='pci-private-v1';
export const DB_VERSION=2;
export const STORES:StoreName[]=['journal_entries','identity_notes','belief_tests','rehearsals','goal_metrics','quiz_attempts','profile_preferences','goals','beliefs','belief_revisions','evidence_entries','reflection_notes','rehearsal_sessions','activity_events','review_ratings','practice_sessions','scenario_progress','experiments','predicted_outcomes','observed_outcomes','bookmarks','backups','events','program_progress','consents'];
let openPromise:Promise<IDBDatabase>|null=null;
export function openPrivateDB():Promise<IDBDatabase>{
 if(typeof indexedDB==='undefined')return Promise.reject(new Error('IndexedDB unavailable. Your entries will not be saved.'));
 if(openPromise)return openPromise;
 openPromise=new Promise((resolve,reject)=>{
  const request=indexedDB.open(DB_NAME,DB_VERSION);
  request.onupgradeneeded=()=>{const db=request.result;const tx=request.transaction!;for(const store of STORES){const os=db.objectStoreNames.contains(store)?tx.objectStore(store):db.createObjectStore(store,{keyPath:'id'});for(const key of ['created_at','updated_at']) if(!os.indexNames.contains(key))os.createIndex(key,key,{unique:false});if(store==='events'&&!os.indexNames.contains('data.idempotency_key'))os.createIndex('data.idempotency_key','data.idempotency_key',{unique:false});}};
  request.onsuccess=()=>{const db=request.result;db.onversionchange=()=>{db.close();openPromise=null};resolve(db)};
  request.onerror=()=>{openPromise=null;reject(request.error || new Error('Storage cannot be opened'))};
  request.onblocked=()=>{openPromise=null;reject(new Error('Another PCI tab is blocking the database upgrade. Close other tabs and reload.'))};
 });return openPromise;
}
function transactionResult<T>(store:StoreName,mode:IDBTransactionMode,fn:(os:IDBObjectStore,ok:(value:T)=>void,fail:(e:unknown)=>void)=>void):Promise<T>{
 return openPrivateDB().then(db=>new Promise<T>((resolve,reject)=>{let value:T;let hasValue=false;const tx=db.transaction(store,mode);const ok=(v:T)=>{value=v;hasValue=true};const fail=(e:unknown)=>{try{tx.abort()}catch{}reject(e)};tx.oncomplete=()=>{if(hasValue)resolve(value);else reject(new Error('Transaction produced no result'))};tx.onerror=()=>reject(tx.error||new Error('Database transaction failed'));tx.onabort=()=>reject(tx.error||new Error('Database transaction aborted'));try{fn(tx.objectStore(store),ok,fail)}catch(e){fail(e)}}));
}
export async function listRecords(store:StoreName):Promise<PrivateRecord[]>{return transactionResult(store,'readonly',(os,ok)=>{const req=os.getAll();req.onsuccess=()=>ok(req.result as PrivateRecord[])})}
export async function getRecord(store:StoreName,id:string):Promise<PrivateRecord|undefined>{return transactionResult(store,'readonly',(os,ok)=>{const req=os.get(id);req.onsuccess=()=>ok(req.result as PrivateRecord|undefined)})}
export async function putRecord(record:PrivateRecord):Promise<PrivateRecord>{if(!STORES.includes(record.store))throw new Error('Unknown private store');if(record.sensitive&&!record.consent_id)throw new Error('Sensitive records require recorded consent');return transactionResult(record.store,'readwrite',(os,ok)=>{const req=os.put(record);req.onsuccess=()=>ok(record)})}
export async function deleteRecord(store:StoreName,id:string):Promise<void>{return transactionResult(store,'readwrite',(os,ok)=>{const req=os.delete(id);req.onsuccess=()=>ok(undefined)})}
export function newRecord(store:StoreName,data:Record<string,unknown>,refs:string[]=[],sensitive=false,consent_id?:string):PrivateRecord{if(!globalThis.crypto?.randomUUID)throw new Error('Secure context required for new private IDs');const now=new Date().toISOString();return {id:crypto.randomUUID(),store,created_at:now,updated_at:now,owner:'user',privacy_mode:'device_local',schema_version:'2.0.0',data,refs:[...new Set(refs)],sensitive,...(consent_id?{consent_id}:{})}}
export async function exportPrivate(includeSensitive=false):Promise<Record<string,unknown>> {
 const records:Record<string,PrivateRecord[]>={};const included:StoreName[]=[];
 for(const store of STORES){const arr=(await listRecords(store)).filter(x=>includeSensitive || !x.sensitive);if(arr.length){records[store]=arr;included.push(store)}}
 return {format:'PCI_PRIVATE_EXPORT',version:2,created_at:new Date().toISOString(),schema_version:'2.0.0',source_app:'PSYCHO-CYBERNETICS-INTELLIGENCE',metadata:{time_zone:Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC',included_stores:included,sensitive_data_warning:'Unencrypted unless user explicitly encrypts the file',export_mode:includeSensitive?'all':'redacted',source_content_versions:{knowledge:'1.0.0',activity:'1.0.0',personalization:'1.0.0'}},records};
}
/** Basic import guard for the existing v2 envelope. This deliberately does NOT
 * rewrite application-specific data bodies or IDs: older valid records stay readable.
 * It rejects malformed envelopes before the importer opens a write transaction.
 */
export const MAX_BACKUP_BYTES=10_000_000;
const UUID_STYLE=/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
const ISO_TIME=/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,3})?Z$/;
function isTime(value:unknown):boolean{return typeof value==='string'&&ISO_TIME.test(value)&&Number.isFinite(Date.parse(value))}
export function validateExport(bundle:unknown):bundle is {records:Record<string,PrivateRecord[]>} {
 if(!bundle||typeof bundle!=='object'||Array.isArray(bundle))return false;
 const x=bundle as Record<string,any>;
 if(x.format!=='PCI_PRIVATE_EXPORT'||x.version!==2||x.schema_version!=='2.0.0'||x.source_app!=='PSYCHO-CYBERNETICS-INTELLIGENCE'||!x.records||typeof x.records!=='object'||Array.isArray(x.records))return false;
 let count=0;
 const seen=new Set<string>();
 for(const [store,arr] of Object.entries(x.records)){
  if(!STORES.includes(store as StoreName)||!Array.isArray(arr))return false;
  count+=arr.length;if(count>50_000)return false;
  for(const rec of arr){
   if(!rec||typeof rec!=='object'||Array.isArray(rec)||rec.store!==store||rec.owner!=='user'||rec.privacy_mode!=='device_local'||rec.schema_version!=='2.0.0'||typeof rec.id!=='string'||!UUID_STYLE.test(rec.id)||!isTime(rec.created_at)||!isTime(rec.updated_at)||!Array.isArray(rec.refs)||rec.refs.length>500||rec.refs.some((ref:unknown)=>typeof ref!=='string'||ref.length>256)||!rec.data||typeof rec.data!=='object'||Array.isArray(rec.data)||typeof rec.sensitive!=='boolean'||(rec.sensitive&&(!rec.consent_id||typeof rec.consent_id!=='string'||!UUID_STYLE.test(rec.consent_id))))return false;
   const key=store+'|'+rec.id;if(seen.has(key))return false;seen.add(key);
  }
 }
 return true;
}
export async function importPrivate(bundle:unknown):Promise<{imported:number;skipped:number}>{
 let serialized:string;try{serialized=JSON.stringify(bundle)}catch{throw new Error('Backup is not serializable JSON')}
 if(!serialized||new TextEncoder().encode(serialized).length>MAX_BACKUP_BYTES)throw new Error('Backup exceeds 10 MB import limit');
 if(!validateExport(bundle))throw new Error('Invalid or incompatible PCI v2 export');const db=await openPrivateDB();const all=Object.entries(bundle.records).flatMap(([store,rows])=>rows.map(row=>({...row,store:store as StoreName})));if(!all.length)return {imported:0,skipped:0};const names=[...new Set(all.map(r=>r.store))];return new Promise((resolve,reject)=>{const tx=db.transaction(names,'readwrite');let imported=0,skipped=0;tx.oncomplete=()=>resolve({imported,skipped});tx.onerror=()=>reject(tx.error||new Error('Import failed; no partial changes committed'));tx.onabort=()=>reject(tx.error||new Error('Import aborted'));for(const rec of all){const os=tx.objectStore(rec.store);const req=os.get(rec.id);req.onsuccess=()=>{if(req.result){skipped++}else{const put=os.add(rec);put.onsuccess=()=>{imported++}}}}})}
