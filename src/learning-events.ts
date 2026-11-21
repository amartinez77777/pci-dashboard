/** Shared transaction/event helper for Stage 12. No user-authored prose is ever copied into analytics events. */
import {openPrivateDB,newRecord} from './storage.js';
import type {PrivateRecord,StoreName} from './types.js';
export interface LearningEvent {type:string;target_id:string;key:string;ids?:Record<string,string|number|boolean>}
export async function saveLearningTransaction(records:PrivateRecord[],deleted:Array<{store:StoreName;id:string}>=[],evt?:LearningEvent):Promise<void>{
 const db=await openPrivateDB();const keys=[...new Set<StoreName>([...records.map(r=>r.store),...deleted.map(r=>r.store),...(evt?['events' as StoreName]:[])])];
 if(!keys.length)return;
 return new Promise((resolve,reject)=>{
  const tx=db.transaction(keys,'readwrite');tx.oncomplete=()=>resolve();tx.onerror=()=>reject(tx.error||Error('Write failed'));tx.onabort=()=>reject(tx.error||Error('Write aborted'));
  try{
   for(const r of records){if(r.sensitive&&!r.consent_id)throw Error('Sensitive data requires consent');tx.objectStore(r.store).put(r)}
   for(const d of deleted)tx.objectStore(d.store).delete(d.id);
   if(evt){const event=newRecord('events',{event_type:evt.type,event_version:'2.1.0',target_id:evt.target_id,idempotency_key:evt.key,timestamp_iso:new Date().toISOString(),...(evt.ids||{})},[evt.target_id]);const store=tx.objectStore('events');const all=store.getAll();all.onsuccess=()=>{if(!(all.result as PrivateRecord[]).some(r=>r.data.idempotency_key===evt.key))store.add(event)};}
  }catch(e){try{tx.abort()}catch{} reject(e)}
 });
}
