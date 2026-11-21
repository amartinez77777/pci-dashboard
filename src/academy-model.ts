/** PCI-created 21-day course: pure, deterministic decisions. No psychological scoring. */
export interface AcademySourceRef {source_id:string;pdf_page:number;printed_page?:number|null}
export interface AcademyDay {
 id:string;program_id:string;day_number:number;content_version:string;title:string;origin:string;chapter_id:string;
 primary_activity_id:string;optional_rehearsal_id:string|null;optional_scenario_id:string|null;
 verified_concept_ids:string[];source_refs:AcademySourceRef[];source_status:string;evidence_status:string;
 estimated_minutes:number;daily_task:string;reflection_prompt:string;
 short_session:{estimated_minutes:number;instructions:string;completion_equivalent:boolean};
 checkpoint?:{questions:string[];allow_goal_revision:boolean;allow_rest:boolean;requires_disclosure:boolean};
}
export interface AcademyCurriculum {id:string;origin:string;schema_version:string;advance_policy:Record<string,unknown>;checkpoint_days:number[];days:AcademyDay[]}
export type DayResult='completed'|'skipped';
export type DayMode='standard'|'short'|'skip';
export interface DayLog {day_id:string;day_number:number;result:DayResult;mode:DayMode;at:string;checkpoint_review?:string|null}
export interface ProgramState {program_id:'PCI-PROG-021';run_id:string;status:'in_progress'|'paused'|'completed'|'archived';day_number:number;history:DayLog[];started_at:string;finished_at:string|null;timezone:string}
export type ProgramAction={kind:'complete'|'skip'|'pause'|'resume';mode?:'standard'|'short';checkpoint_review?:string|null};
export const ACADEMY_CHECKPOINTS=[4,9,15,21];
export function validateAcademyCurriculum(p:AcademyCurriculum,knownIds:Set<string>):string[]{
 const errors:string[]=[];
 if(p.id!=='PCI-PROG-021'||p.origin!=='PCI_adaptation')errors.push('Program ID or adaptation origin changed');
 if(p.days.length!==21)errors.push('Expected 21 authored days');
 if(JSON.stringify(p.checkpoint_days)!==JSON.stringify(ACADEMY_CHECKPOINTS))errors.push('Checkpoint days changed');
 for(let i=0;i<p.days.length;i++){const d=p.days[i];if(d.id!==`PCI-DAY-${String(i+1).padStart(2,'0')}`||d.day_number!==i+1)errors.push(`Day order/ID incorrect at ${i+1}`);
  if(d.program_id!==p.id||d.origin!=='PCI_adaptation')errors.push(`Day provenance invalid ${d.id}`);
  for(const id of [d.chapter_id,d.primary_activity_id,...d.verified_concept_ids,...(d.optional_scenario_id?[d.optional_scenario_id]:[]),...(d.optional_rehearsal_id?[d.optional_rehearsal_id]:[])])if(!knownIds.has(id))errors.push(`Missing source reference ${id} on ${d.id}`);
  if(ACADEMY_CHECKPOINTS.includes(d.day_number)!==Boolean(d.checkpoint))errors.push(`Checkpoint mismatch ${d.id}`);
  if(!d.daily_task||!d.reflection_prompt||!d.short_session?.instructions)errors.push(`Missing instructional content ${d.id}`);
 }
 return errors;
}
export function newProgramState(runId:string,now:string,timezone:string):ProgramState {
 if(!runId||!Number.isFinite(Date.parse(now)))throw Error('Invalid program start');
 return {program_id:'PCI-PROG-021',run_id:runId,status:'in_progress',day_number:1,history:[],started_at:now,finished_at:null,timezone:timezone||'UTC'};
}
export function applyProgramAction(state:ProgramState,action:ProgramAction,at:string):ProgramState {
 if(!Number.isFinite(Date.parse(at)))throw Error('Invalid timestamp');
 if(state.status==='completed'||state.status==='archived')return state;
 if(action.kind==='pause')return state.status==='in_progress'?{...state,status:'paused'}:state;
 if(action.kind==='resume')return state.status==='paused'?{...state,status:'in_progress'}:state;
 if(state.status!=='in_progress')throw Error('Resume your course before advancing');
 const expected=state.history.length+1;if(state.day_number!==expected||expected<1||expected>21)throw Error('Corrupted course position');
 if(action.kind!=='complete'&&action.kind!=='skip')throw Error('Invalid course action');
 if(ACADEMY_CHECKPOINTS.includes(expected)&&action.checkpoint_review===undefined)throw Error('Review the checkpoint before advancing');
 const revisit=action.checkpoint_review;
 if(revisit!==undefined&&revisit!==null&&revisit!=='none'&&!state.history.some(h=>h.day_id===revisit))throw Error('Revisit choice must be an earlier finished day');
 const mode:DayMode=action.kind==='skip'?'skip':action.mode==='short'?'short':'standard';
 const entry:DayLog={day_id:`PCI-DAY-${String(expected).padStart(2,'0')}`,day_number:expected,result:action.kind==='skip'?'skipped':'completed',mode,at,
  ...(revisit!==undefined?{checkpoint_review:revisit}:{}),};
 return {...state,history:[...state.history,entry],day_number:Math.min(22,expected+1),status:expected===21?'completed':'in_progress',finished_at:expected===21?at:null};
}
export function currentDay(state:ProgramState|null):number {return state?state.day_number:1}
export function progressCounts(state:ProgramState|null){return {attempted:state?.history.filter(x=>x.result==='completed').length||0,skipped:state?.history.filter(x=>x.result==='skipped').length||0,acknowledged:state?.history.length||0}}
export type ReviewReason='quiz_incorrect'|'quiz_correct'|'checkpoint_selected'|'user_requested';
export interface ReviewItem {id:string;question_id:string;due_date:string;reason:ReviewReason;status:'active'|'snoozed'|'dismissed';last_rated_at:string}
export function localDate(at:string,zone:string):string {
 const d=new Date(at);if(!Number.isFinite(d.getTime()))throw Error('Invalid review timestamp');
 try{return new Intl.DateTimeFormat('en-CA',{timeZone:zone||'UTC',year:'numeric',month:'2-digit',day:'2-digit'}).format(d).replace(/(\d{2})\/(\d{2})\/(\d{4})/,'$3-$1-$2')}
 catch{return d.toISOString().slice(0,10)}
}
export function addCalendarDays(date:string,days:number):string {
 if(!/^\d{4}-\d{2}-\d{2}$/.test(date))throw Error('Invalid local date');const d=new Date(`${date}T12:00:00Z`);if(!Number.isFinite(d.getTime()))throw Error('Invalid date');d.setUTCDate(d.getUTCDate()+days);return d.toISOString().slice(0,10)
}
export function reviewDueDate(at:string,zone:string,reason:ReviewReason):string {
 const date=localDate(at,zone);return addCalendarDays(date,reason==='quiz_correct'?4:reason==='quiz_incorrect'?1:0);
}
export function isReviewDue(item:ReviewItem,at:string,zone:string):boolean{return item.status==='active'&&item.due_date<=localDate(at,zone)}
export function whyReview(reason:ReviewReason):string{return {quiz_incorrect:'A previous recall answer was incorrect. You can retry when ready.',quiz_correct:'A prior recall answer was correct. Revisit after 4 calendar days for practice.',checkpoint_selected:'You explicitly selected this topic at a course checkpoint.',user_requested:'You asked to revisit this topic.'}[reason]}
export interface AcademyQuestion {id:string;concept_id:string;chapter_id:string;prompt:string;choices:[string,string,string];correct_index:0|1|2;rationale:string;source_status:'book_assertion_only'}
/** Manually curated checks of what the book claims, NOT independent clinical or scientific proof. */
export const ACADEMY_QUESTIONS:AcademyQuestion[]=[
 {id:'PCI-ACA-Q01',concept_id:'PCI-C-CH01-001',chapter_id:'PCI-CH-01',prompt:'In the book, what does “self-image” primarily refer to?',choices:['A stable clinical diagnosis','A working picture of the person one believes oneself to be','A verified measurement of ability'],correct_index:1,rationale:'The chapter presents self-image as an interpreted working self-description. This is the author’s framework, not a diagnostic score.',source_status:'book_assertion_only'},
 {id:'PCI-ACA-Q02',concept_id:'PCI-C-CH02-001',chapter_id:'PCI-CH-02',prompt:'How should PCI explain the book’s “automatic success mechanism”?',choices:['As the book’s goal-seeking cybernetic analogy','As a newly isolated brain structure','As a guarantee that imagining an outcome causes success'],correct_index:0,rationale:'The cybernetic account is an analogy for goals and feedback, not a separately verified brain organ or guarantee.',source_status:'book_assertion_only'},
 {id:'PCI-ACA-Q03',concept_id:'PCI-C-CH03-001',chapter_id:'PCI-CH-03',prompt:'In the example about imagined rejection, what remains uncertain?',choices:['Whether a thought exists','Whether every stranger actually judges the person negatively','Whether the chapter contains a story'],correct_index:1,rationale:'The person’s interpretation of others’ views may differ from what anyone has directly observed.',source_status:'book_assertion_only'},
 {id:'PCI-ACA-Q04',concept_id:'PCI-C-CH04-001',chapter_id:'PCI-CH-04',prompt:'Which action best fits checking a restrictive belief?',choices:['Treat the belief as unchangeable','Declare the opposite belief proven','Compare the belief against specific observed counterexamples'],correct_index:2,rationale:'The chapter favors examining the premise against experience; a single counterexample need not prove universal change.',source_status:'book_assertion_only'},
 {id:'PCI-ACA-Q05',concept_id:'PCI-C-CH05-001',chapter_id:'PCI-CH-05',prompt:'What is the role of rational evaluation in this chapter?',choices:['To test and revise interpretations','To suppress every negative feeling','To guarantee future performance'],correct_index:0,rationale:'The author proposes examining interpretations instead of accepting them without question; feelings need not be suppressed.',source_status:'book_assertion_only'},
 {id:'PCI-ACA-Q06',concept_id:'PCI-C-CH06-001',chapter_id:'PCI-CH-06',prompt:'What distinction does the chapter draw about attention?',choices:['Planning is always harmful','Preparation and execution can call for different kinds of attention','One must stop learning physical skills'],correct_index:1,rationale:'The chapter distinguishes deliberate preparation from less intrusive monitoring during execution.',source_status:'book_assertion_only'},
 {id:'PCI-ACA-Q09',concept_id:'PCI-C-CH09-004',chapter_id:'PCI-CH-09',prompt:'After a setback, which statement reflects feedback rather than identity?',choices:['I will always fail','The result shows I am defective','This attempt did not work; I can inspect what changed'],correct_index:2,rationale:'The learning theme is to inspect specific outcomes and corrections without making a global identity judgment.',source_status:'book_assertion_only'},
 {id:'PCI-ACA-Q16',concept_id:'PCI-C-CH16-001',chapter_id:'PCI-CH-16',prompt:'What can an attributed personal success story establish by itself?',choices:['It illustrates the author’s argument, not causal efficacy','It independently proves every technique works','It provides a controlled experiment'],correct_index:0,rationale:'Anecdotes illustrate claims but cannot on their own establish controlled causal evidence.',source_status:'book_assertion_only'},
];
export function questionForDay(day:AcademyDay):AcademyQuestion|undefined{return ACADEMY_QUESTIONS.find(q=>day.verified_concept_ids.includes(q.concept_id))||ACADEMY_QUESTIONS.find(q=>q.chapter_id===day.chapter_id)}
export function gradeRecall(q:AcademyQuestion,index:number):{correct:boolean;rationale:string}{if(!Number.isInteger(index)||index<0||index>2)throw Error('Choose one answer');return {correct:index===q.correct_index,rationale:q.rationale}}
