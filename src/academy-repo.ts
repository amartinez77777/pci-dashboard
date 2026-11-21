/** Local-only Academy repository, no additional stores/migrations. */
import {openPrivateDB,newRecord,listRecords,getRecord} from './storage.js';
import {saveLearningTransaction} from './learning-events.js';
import type {PrivateRecord} from './types.js';
import {newProgramState,applyProgramAction,gradeRecall,reviewDueDate,ACADEMY_QUESTIONS,type ProgramState,type ProgramAction,type AcademyQuestion,type ReviewReason} from './academy-model.js';
const VERSION='1.0.0';
export function isAcademyRun(r:PrivateRecord):boolean{return r.store==='program_progress'&&r.data.academy_contract===VERSION&&r.data.program_id==='PCI-PROG-021'&&typeof r.data.state==='object'&&r.data.state!==null}
export async function listAcademyRuns():Promise<PrivateRecord[]>{return (await listRecords('program_progress')).filter(isAcademyRun).sort((a,b)=>b.created_at.localeCompare(a.created_at))}
export async function createAcademyRun(zone='UTC'):Promise<PrivateRecord>{const rec=newRecord('program_progress',{},['PCI-PROG-021']);const state=newProgramState(rec.id,rec.created_at,zone);rec.data={academy_contract:VERSION,program_id:'PCI-PROG-021',state};await saveLearningTransaction([rec]);return rec}
/** Updates and event idempotence are in the SAME transaction. Rapid taps cannot advance twice for a single expected day. */
export async function updateAcademyRun(id:string,expectedDay:number,action:ProgramAction):Promise<PrivateRecord>{
 const db=await openPrivateDB();return new Promise((resolve,reject)=>{const tx=db.transaction(['program_progress','events','review_ratings'],'readwrite');let result:PrivateRecord|undefined;
 tx.oncomplete=()=>{if(result)resolve(result);else reject(Error('Course save did not finish'))};tx.onerror=()=>reject(tx.error||Error('Course transaction failed'));tx.onabort=()=>reject(tx.error||Error('Course transaction cancelled'));
 const req=tx.objectStore('program_progress').get(id);
 req.onsuccess=()=>{const old=req.result as PrivateRecord|undefined;if(!old||!isAcademyRun(old)){tx.abort();return}const state=old.data.state as ProgramState;
  // Stale duplicate event: return latest state, not a second advancement.
  if(action.kind==='complete'||action.kind==='skip'){
   if(state.day_number!==expectedDay){result=old;return}
  }
  try{const timestamp=new Date().toISOString();const updated=applyProgramAction(state,action,timestamp);if(updated===state){result=old;return}
   result={...old,updated_at:timestamp,data:{...old.data,state:updated}};tx.objectStore('program_progress').put(result);
   if(action.kind==='complete'||action.kind==='skip'){
    const dayId=`PCI-DAY-${String(expectedDay).padStart(2,'0')}`,key=`program.${action.kind}:${id}:${dayId}`;
    const e=newRecord('events',{event_type:action.kind==='skip'?'program.day_skipped':'program.day_completed',event_version:'2.1.0',target_id:dayId,program_run_id:id,idempotency_key:key,mode:action.kind==='skip'?'skip':action.mode==='short'?'short':'standard',timestamp_iso:timestamp},[id,dayId]);
    // Each day can be acknowledged only once within the run; history count is the authoritative gate.
    tx.objectStore('events').add(e);
    const selected=action.checkpoint_review;
    if(selected&&selected!=='none'){
     const review=newRecord('review_ratings',{academy_review:true,program_run_id:id,question_id:null,target_day_id:selected,reason:'checkpoint_selected' as ReviewReason,status:'active',due_date:reviewDueDate(timestamp,updated.timezone,'checkpoint_selected'),last_rated_at:timestamp},[id,selected]);tx.objectStore('review_ratings').add(review);
    }
   }
  }catch{tx.abort()}
 };
 });
}
export async function listAcademyQuizzes():Promise<PrivateRecord[]>{return (await listRecords('quiz_attempts')).filter(r=>r.data.academy_quiz===true).sort((a,b)=>b.created_at.localeCompare(a.created_at))}
export async function listAcademyReviews():Promise<PrivateRecord[]>{return (await listRecords('review_ratings')).filter(r=>r.data.academy_review===true).sort((a,b)=>String(a.data.due_date).localeCompare(String(b.data.due_date)))}
export async function submitAcademyQuiz(q:AcademyQuestion,choice:number,runId:string,dayId:string,zone:string):Promise<{correct:boolean;rationale:string}>{
 if(!ACADEMY_QUESTIONS.some(item=>item.id===q.id))throw Error('Unknown recall question');const grade=gradeRecall(q,choice);const at=new Date().toISOString();
 const quiz=newRecord('quiz_attempts',{academy_quiz:true,question_id:q.id,concept_id:q.concept_id,program_run_id:runId,day_id:dayId,chosen_index:choice,correct:grade.correct,attempted_at:at},[q.concept_id,dayId]);
 const existing=(await listAcademyReviews()).find(r=>r.data.question_id===q.id&&r.data.program_run_id===runId);
 const reason:ReviewReason=grade.correct?'quiz_correct':'quiz_incorrect';const review=existing?{...existing,updated_at:at,data:{...existing.data,reason,status:'active',last_rated_at:at,due_date:reviewDueDate(at,zone,reason)}}:newRecord('review_ratings',{academy_review:true,program_run_id:runId,question_id:q.id,target_day_id:dayId,reason,status:'active',due_date:reviewDueDate(at,zone,reason),last_rated_at:at},[q.concept_id,dayId]);
 await saveLearningTransaction([quiz,review],[],{type:'quiz.attempted',target_id:q.id,key:`quiz.attempted:${quiz.id}`,ids:{run_id:runId,correct:grade.correct}});
 return grade;
}
export async function updateAcademyReview(id:string,action:'snooze'|'dismiss'|'revisit',zone:string):Promise<PrivateRecord>{const old=await getRecord('review_ratings',id);if(!old||old.data.academy_review!==true)throw Error('Review entry unavailable');const now=new Date().toISOString();const due=reviewDueDate(now,zone,action==='snooze'?'quiz_incorrect':'user_requested');const updated:PrivateRecord={...old,updated_at:now,data:{...old.data,status:action==='dismiss'?'dismissed':'active',due_date:action==='snooze'?due:reviewDueDate(now,zone,'user_requested'),reason:action==='revisit'?'user_requested':old.data.reason,last_rated_at:now}};await saveLearningTransaction([updated]);return updated}
