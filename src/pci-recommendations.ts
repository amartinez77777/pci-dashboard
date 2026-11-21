/** PCI v1.1: local-only, deterministic, explainable next actions.
 * Inputs are existing version-2 private records; NO extra store, model, API or hidden scoring.
 * Ranked by declared editorial priority (not a measurement of a person's psychology).
 */
import type {PrivateRecord} from './types.js';
import type {PersonalSnapshot} from './personal-intelligence-model.js';
import {latestAcademyRun} from './personal-intelligence-model.js';
import {ACADEMY_QUESTIONS} from './academy-model.js';

export type ReasonCode = 'RESUME_LESSON'|'PAUSED_LESSON'|'REVIEW_DUE'|'REVIEW_REQUESTED'|'PRACTICE_UNFINISHED'|'REHEARSAL_UNFINISHED'|'OBSERVATION_PENDING'|'GOAL_NEXT_ACTION'|'BELIEF_TO_REHEARSAL'|'REHEARSAL_FOLLOW_UP'|'LEARNING_TO_PRACTICE'|'START_WITH_GOAL'|'EXPLORE_SOURCE';
export interface PersonalRecommendation {
 id:string;title:string;detail:string;why:string;reason_code:ReasonCode;route:string;
 source_id?:string;source_store?:string;priority:number;origin:'local_record'|'PCI_educational_suggestion';
}
const priRows=(s:PersonalSnapshot,k:keyof PersonalSnapshot):PrivateRecord[]=>s[k]||[];
const priStr=(v:unknown):string=>typeof v==='string'?v:'';
const priSafeDate=(v:unknown):string=>typeof v==='string'&&/^\d{4}-\d{2}-\d{2}/.test(v)?v.slice(0,10):'';
const priDated=(r:PrivateRecord)=>priStr(r.updated_at)||priStr(r.created_at);
const priOrdered=(a:PrivateRecord,b:PrivateRecord)=>priDated(b).localeCompare(priDated(a))||a.id.localeCompare(b.id);
const priRec=(reason_code:ReasonCode,title:string,detail:string,why:string,route:string,priority:number,source?:PrivateRecord):PersonalRecommendation=>({id:`${reason_code}:${source?.id||'starter'}`,reason_code,title,detail,why,route,priority,origin:source?'local_record':'PCI_educational_suggestion',...(source?{source_id:source.id,source_store:source.store}:{})});
export function personalRecommendations(s:PersonalSnapshot,nowISO=new Date().toISOString()):PersonalRecommendation[]{
 const result:PersonalRecommendation[]=[];
 const run=latestAcademyRun(s);
 if(run&&run.state.status==='in_progress'&&run.state.day_number>=1&&run.state.day_number<=21)
  result.push(priRec('RESUME_LESSON',`Continue Day ${run.state.day_number}`,`Open the current authored Academy lesson. Your progress advances only by explicit action.`,`Your saved course is in progress on Day ${run.state.day_number}.`,`academy/day/${run.state.day_number}`,92,run.record));
 if(run?.state.status==='paused')result.push(priRec('PAUSED_LESSON','Resume your paused course',`Day ${run.state.day_number} is saved without a missed-day penalty.`,'The latest Academy run was explicitly paused.','academy',88,run.record));
 const runId=run?.record.id;
 const due=priRows(s,'review_ratings').filter(r=>r.data.academy_review===true&&r.data.status!=='dismissed'&&(!runId||r.data.program_run_id===runId)&&priSafeDate(r.data.due_date)!==''&&priSafeDate(r.data.due_date)<=nowISO.slice(0,10)).sort(priOrdered);
 if(due[0]){
  const review=due[0],questionId=priStr(review.data.question_id),question=ACADEMY_QUESTIONS.find(q=>q.id===questionId);
  const target=question?.concept_id||priStr(review.data.target_day_id);
  const why=review.data.reason==='quiz_incorrect'?'A recorded comprehension answer did not match the authored answer.':review.data.reason==='checkpoint_selected'?'You selected this day at an Academy checkpoint.':'A saved review item reached its local due date.';
  result.push(priRec('REVIEW_DUE',question?'Revisit a source concept':'Revisit your selected Academy day',`Review ${target||'a saved course item'}; you can snooze or dismiss it.`,why,'academy/review',98,review));
 }
 const unfinished=priRows(s,'practice_sessions').filter(r=>r.data.conditioning_contract_version==='1.0.0'&&r.data.status!=='completed').sort(priOrdered);
 if(unfinished[0])result.push(priRec('PRACTICE_UNFINISHED','Resume an unfinished conditioning practice','Your saved steps are ready; nothing is counted as completed yet.','A user-created conditioning session is unfinished.',`conditioning/${encodeURIComponent(unfinished[0].id)}`,89,unfinished[0]));
 const rehearsals=priRows(s,'rehearsal_sessions').filter(r=>r.data.status!=='completed'&&r.data.status!=='stopped').sort(priOrdered);
 if(rehearsals[0])result.push(priRec('REHEARSAL_UNFINISHED','Continue a saved rehearsal','Open the Theater session history and resume if appropriate.','A saved rehearsal session is not yet complete.',`theater/history/${encodeURIComponent(rehearsals[0].id)}`,87,rehearsals[0]));
 const observed=new Set(priRows(s,'observed_outcomes').map(x=>priStr(x.data.experiment_id)).filter(Boolean));
 const goals=new Map(priRows(s,'goals').map(x=>[x.id,x]));
 const experiments=priRows(s,'experiments').filter(r=>r.data.feedback_contract_version==='1.0.0'&&!observed.has(r.id)).sort(priOrdered);
 if(experiments[0]){
  const goalId=priStr(experiments[0].data.goal_id),goal=goals.get(goalId);
  result.push(priRec('OBSERVATION_PENDING','Complete a feedback observation','Record what actually happened only after trying the action. A missing outcome is not a failure.','A saved prediction has no matching observed-outcome record.',goal?`feedback/${goalId}/${experiments[0].id}`:'feedback',95,experiments[0]));
 }
 const goalRows=priRows(s,'goals').sort(priOrdered);
 if(goalRows.length){const goal=goalRows[0];result.push(priRec('GOAL_NEXT_ACTION','Choose a next action for a saved goal',goal.sensitive?'Open your private goal without showing details here.':'Review the action you chose and decide whether to rehearse or observe it.','You explicitly saved a goal. This is a PCI-designed next step, not a source-book relationship.',`feedback/${goal.id}`,67,goal));}
 const beliefs=priRows(s,'beliefs').sort(priOrdered);
 if(beliefs.length)result.push(priRec('BELIEF_TO_REHEARSAL','Practice a response related to a saved belief','Create a private scene and link it by the existing belief ID.','You saved a belief. Rehearsal is optional, not an inferred treatment.',`theater/belief/${beliefs[0].id}`,68,beliefs[0]));
 const scenes=priRows(s,'rehearsals').sort(priOrdered),completed=priRows(s,'rehearsal_sessions').filter(r=>r.data.status==='completed').sort(priOrdered);
 if(completed[0]){
  const sceneId=priStr(completed[0].data.scene_id)||priStr((completed[0].data.player as Record<string,unknown>|undefined)?.scene_id);
  const scene=scenes.find(x=>x.id===sceneId);
  const goalId=scene?priStr(scene.data.goal_id):'';
  const goal=goals.get(goalId);
  const relatedExperiment=goalId&&priRows(s,'experiments').some(x=>x.data.goal_id===goalId&&priDated(x)>=priDated(completed[0]));
  if(!relatedExperiment)result.push(priRec('REHEARSAL_FOLLOW_UP','Take rehearsal into real-world feedback','If useful, record a predicted action and later a real observation. Rehearsal itself is not an outcome.',goal?'The completed session explicitly links to a saved scene and goal; no later iteration was found.':'A rehearsal was completed. Any Feedback Lab connection is optional and not yet recorded.',goal?`feedback/${goal.id}`:'feedback',61,completed[0]));
 }
 if(run?.state.history?.length){const latest=run.state.history[run.state.history.length-1];if(latest?.day_id)
  result.push(priRec('LEARNING_TO_PRACTICE','Connect a lesson to a practical exercise','Open the lesson’s existing source and practice links; opening them does not mark completion.',`Your course history explicitly contains ${latest.day_id}.`,`academy/day/${latest.day_number}`,57,run.record));}
 if(!result.length){result.push(priRec('START_WITH_GOAL','Choose one small goal','Save a voluntary goal or start with a book concept. No personal insights are assumed.','No course, goal, belief or learning history is stored here.','feedback',60));result.push(priRec('EXPLORE_SOURCE','Browse the 16-chapter Knowledge Vault','Explore attributed book claims and their limitations without creating personal records.','The source library is available without onboarding.','knowledge',45));}
 return result.sort((a,b)=>b.priority-a.priority||a.id.localeCompare(b.id));
}
export function recommendationFor(s:PersonalSnapshot,nowISO?:string):PersonalRecommendation{return personalRecommendations(s,nowISO)[0]}
