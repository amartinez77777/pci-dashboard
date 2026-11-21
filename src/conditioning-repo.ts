/** Local-only conditioning repository. Reuses existing pci-private-v1/v2 stores. */
import {newRecord,getRecord,listRecords} from './storage.js';
import {saveLearningTransaction} from './learning-events.js';
import {startConditioning,conditioningTransition,getConditioningProtocol,type ConditioningAction,type ConditioningState,type ConditioningMode,type ConditioningProtocol} from './conditioning-model.js';
import type {PrivateRecord,StoreName} from './types.js';
const CONTRACT='1.0.0';
function valid(record:PrivateRecord):boolean{const d=record.data;return record.store==='practice_sessions'&&d.conditioning_contract_version===CONTRACT&&typeof d.protocol_id==='string'&&!!getConditioningProtocol(String(d.protocol_id))&&typeof d.state==='object'&&d.state!==null&&Number.isInteger((d.state as ConditioningState).step_index)}
export async function listConditioningHistory():Promise<PrivateRecord[]>{return (await listRecords('practice_sessions')).filter(valid).sort((a,b)=>b.updated_at.localeCompare(a.updated_at))}
export async function createConditioningSession(protocol:ConditioningProtocol,mode:ConditioningMode,at=Date.now()):Promise<PrivateRecord>{if(getConditioningProtocol(protocol.id)!==protocol)throw Error('Unknown protocol');const state=startConditioning(protocol,mode,at);const record=newRecord('practice_sessions',{conditioning_contract_version:CONTRACT,protocol_id:protocol.id,protocol_version:'1.0.0',source_origin:protocol.origin,state,status:state.status,started_at:state.started_at,completed_at:null},[protocol.id,protocol.concept_id,protocol.activity_id]);await saveLearningTransaction([record],[],{type:'practice.started',target_id:record.id,key:`practice.started:${record.id}`,ids:{protocol_id:protocol.id,origin:'PCI_adaptation'}});return record}
export interface ConditioningWriteOptions{sensitive?:boolean;consented?:boolean}
export async function saveConditioningAction(id:string,action:ConditioningAction,at=Date.now(),opts:ConditioningWriteOptions={}):Promise<PrivateRecord>{
 const old=await getRecord('practice_sessions',id);if(!old||!valid(old))throw Error('Practice not found or incompatible');
 const protocol=getConditioningProtocol(String(old.data.protocol_id))!;
 const current=old.data.state as ConditioningState;
 if(current.status==='completed')return old;
 const state=conditioningTransition(current,protocol,action,at);
 const sensitive=Boolean(old.sensitive||opts.sensitive);
 const consentNeeded=sensitive&&!old.consent_id;
 if(consentNeeded&&!opts.consented)throw Error('Confirm local storage consent for sensitive writing.');
 const consent=consentNeeded?newRecord('consents',{scope:'practice_sessions',purpose:'optional sensitive conditioning reflection stored only on device',explicit:true},[]):null;
 const rec:PrivateRecord={...old,updated_at:new Date(at).toISOString(),sensitive,consent_id:old.consent_id||consent?.id,data:{...old.data,state,status:state.status,completed_at:state.completed_at}};
 const evt=state.status==='completed'?{type:'practice.completed',target_id:rec.id,key:`practice.completed:${rec.id}`,ids:{protocol_id:protocol.id,origin:'PCI_adaptation',visited_count:state.visited_step_ids.length,skipped_count:state.skipped_step_ids.length,elapsed_ms:state.elapsed_ms}}:undefined;
 await saveLearningTransaction([...(consent?[consent]:[]),rec],[],evt);
 return rec;
}
export async function rateConditioningSession(sessionId:string,rating:number|null):Promise<PrivateRecord|undefined>{if(rating!==null&&(!Number.isInteger(rating)||rating<1||rating>5))throw Error('Usefulness must be 1–5');const session=await getRecord('practice_sessions',sessionId);if(!session||!valid(session)||session.data.status!=='completed')throw Error('Only completed practices can be reviewed');const old=(await listRecords('review_ratings')).find(r=>r.data.conditioning_session_id===sessionId);if(rating===null){if(old)await saveLearningTransaction([],[{store:'review_ratings',id:old.id}]);return undefined;}const rec=old?{...old,updated_at:new Date().toISOString(),data:{...old.data,usefulness:rating}}:newRecord('review_ratings',{conditioning_contract_version:CONTRACT,conditioning_session_id:sessionId,protocol_id:session.data.protocol_id,usefulness:rating,rating_type:'self_reported_usefulness_not_effectiveness'},[sessionId,String(session.data.protocol_id)]);await saveLearningTransaction([rec]);return rec}
export async function listConditioningRatings():Promise<PrivateRecord[]>{return (await listRecords('review_ratings')).filter(r=>r.data.conditioning_contract_version===CONTRACT&&r.data.conditioning_session_id)}
export async function deleteConditioningSession(id:string):Promise<void>{const rec=await getRecord('practice_sessions',id);if(!rec||!valid(rec))throw Error('Practice no longer exists');const [events,ratings]=await Promise.all([listRecords('events'),listConditioningRatings()]);const deletes:Array<{store:StoreName;id:string}>=[{store:'practice_sessions',id},...events.filter(e=>e.data.target_id===id).map(e=>({store:'events' as StoreName,id:e.id})),...ratings.filter(e=>e.data.conditioning_session_id===id).map(e=>({store:'review_ratings' as StoreName,id:e.id}))];await saveLearningTransaction([],deletes)}
