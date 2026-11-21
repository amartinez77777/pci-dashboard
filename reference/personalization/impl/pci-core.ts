/* PCI Stage 07. Pure, deterministic, nonclinical algorithms. No network or hidden inference. */
export type ReviewRating = 0 | 1 | 2 | 3;
export type ReasonCode = 'COLD_START'|'GOAL_MATCH'|'INTEREST_MATCH'|'DUE_REVIEW'|'NEW_CONTENT'|'DIFFICULTY_MATCH'|'RECENTLY_DONE'|'SKIPPED_RECENTLY'|'RETURNING_AFTER_BREAK'|'USER_OVERRIDE'|'SHORT_SESSION'|'NO_PREFERENCE_MATCH';
export type EventType = 'belief.created'|'belief.revised'|'goal.created'|'goal.updated'|'rehearsal.completed'|'scenario.completed'|'activity.completed'|'activity.skipped'|'exercise.reviewed'|'review.undone'|'experiment.outcome_recorded'|'journal.saved'|'program.day_completed'|'program.day_skipped'|'program.paused'|'program.resumed'|'bookmark.saved';
export interface CatalogItem {id:string;kind:'activity'|'scenario'|'rehearsal';chapter_id:string;title:string;concept_ids:string[];prerequisite_ids:string[];tags:string[];estimated_minutes:number;sensitive:boolean;source_status:string;evidence_status:string;origin:'PCI_adaptation';}
export interface Goal {id:string;status:'active'|'paused'|'retired'|'achieved';priority:number;tags:string[];content_ids?:string[];}
export interface History {contentId:string;kind:'completed'|'skipped';date:string;sessionId:string;}
export interface DueReview {conceptId:string; dueLocalDate:string;}
export interface UserPreferences {interests:string[];difficultyTopics:string[];allowSensitive:boolean;maxMinutes?:number;intensity:'gentle'|'standard'|'extended';}
export interface RecommendationContext {asOfLocalDate:string;goals:Goal[];history:History[];dueReviews:DueReview[];prefs:UserPreferences;completedPrerequisiteIds:string[];excludedContentIds:string[];manuallyPinnedIds:string[];}
export interface Reason {code:ReasonCode;points:number;explanation:string;}
export interface Recommendation {contentId:string;title:string;score:number;reasons:Reason[];reason_codes:ReasonCode[];explanation:string;source_status:string;evidence_status:string;not_a_diagnosis:true;}
export function isValidLocalDate(day:string):boolean { if(!/^\d{4}-\d{2}-\d{2}$/.test(day))return false; const parsed = new Date(`${day}T12:00:00.000Z`);return Number.isFinite(parsed.getTime()) && parsed.toISOString().slice(0,10)===day; }
export function addCivilDays(day:string, n:number):string {if(!isValidLocalDate(day)||!Number.isInteger(n))throw new Error('invalid date/day shift');const d=new Date(`${day}T12:00:00.000Z`); d.setUTCDate(d.getUTCDate()+n);return d.toISOString().slice(0,10);}
export function daysBetween(a:string,b:string):number {if(!isValidLocalDate(a)||!isValidLocalDate(b))throw new Error('invalid civil date');return Math.round((Date.parse(`${b}T12:00:00Z`)-Date.parse(`${a}T12:00:00Z`))/86400000);}
export function toLocalDate(timestampISO:string,timeZone:string):string {const d=new Date(timestampISO);if(!Number.isFinite(d.getTime()))throw new Error('invalid timestamp');const p=new Intl.DateTimeFormat('en-US',{timeZone,year:'numeric',month:'2-digit',day:'2-digit'}).formatToParts(d);const get=(n:string)=>p.find(x=>x.type===n)?.value;return `${get('year')}-${get('month')}-${get('day')}`;}
export function recommend(catalog:CatalogItem[], ctx:RecommendationContext, limit=5):Recommendation[]{
 if(!isValidLocalDate(ctx.asOfLocalDate))throw new Error('invalid asOfLocalDate');
 if(limit<1||!Number.isInteger(limit))throw new Error('invalid recommendation limit');
 const unique = new Set<string>();for(const c of catalog){if(unique.has(c.id))throw new Error('duplicate content ID');unique.add(c.id);}
 const activeGoals=ctx.goals.filter(x=>x.status==='active').sort((a,b)=>a.id.localeCompare(b.id));
 const history=[...ctx.history].sort((a,b)=>b.date.localeCompare(a.date)||a.contentId.localeCompare(b.contentId));
 const cold=activeGoals.length===0&&history.length===0&&ctx.prefs.interests.length===0;
 const lastDate=history.length?history[0].date:null;const dormant=!!lastDate && daysBetween(lastDate,ctx.asOfLocalDate)>=30;
 const completed=new Set([...ctx.completedPrerequisiteIds,...history.filter(h=>h.kind==='completed').map(h=>h.contentId)]);
 const exclude=new Set(ctx.excludedContentIds);const pinned=new Set(ctx.manuallyPinnedIds);
 const dueSet=new Set(ctx.dueReviews.filter(r=>r.dueLocalDate<=ctx.asOfLocalDate).map(r=>r.conceptId));
 return catalog.filter(x=>!exclude.has(x.id)&&(!x.sensitive||ctx.prefs.allowSensitive)&&x.prerequisite_ids.every(id=>completed.has(id))&&(!ctx.prefs.maxMinutes||x.estimated_minutes<=ctx.prefs.maxMinutes||pinned.has(x.id))).map(x=>{
  const reasons:Reason[]=[];const add=(code:ReasonCode,points:number,explanation:string)=>{reasons.push({code,points,explanation});};
  if(cold){add('COLD_START',x.id==='PCI-ACT-CH01-001'?40:x.chapter_id==='PCI-CH-01'?16:0,'No preferences or history yet: start with a foundational, optional exercise.');}
  const matches=activeGoals.filter(g=>x.tags.some(t=>g.tags.includes(t))||g.content_ids?.includes(x.id));
  if(matches.length){const high=Math.max(...matches.map(g=>g.priority));add('GOAL_MATCH',12+Math.min(5,high)*4,'You selected a related goal; this is not an inferred trait.');}
  if(x.tags.some(t=>ctx.prefs.interests.includes(t)))add('INTEREST_MATCH',12,'Matches a topic you explicitly chose.');
  if(x.tags.some(t=>ctx.prefs.difficultyTopics.includes(t)))add('DIFFICULTY_MATCH',8,'You reported wanting more practice in this topic.');
  if(x.concept_ids.some(id=>dueSet.has(id)))add('DUE_REVIEW',25,'A linked concept is due for optional review on your local calendar.');
  const prior=history.find(h=>h.contentId===x.id);
  if(!prior)add('NEW_CONTENT',cold?1:10,'Not yet recorded as completed or skipped.');
  else if(daysBetween(prior.date,ctx.asOfLocalDate)<=2) add(prior.kind==='skipped'?'SKIPPED_RECENTLY':'RECENTLY_DONE',prior.kind==='skipped'?-18:-14,'Recently visited; it can be selected manually instead.');
  if(dormant)add('RETURNING_AFTER_BREAK',x.chapter_id==='PCI-CH-01'?15:5,'A short restart after a gap is available without catch-up pressure.');
  if(ctx.prefs.maxMinutes && x.estimated_minutes<=Math.min(5,ctx.prefs.maxMinutes))add('SHORT_SESSION',5,'Fits your explicitly selected short-session limit.');
  if(pinned.has(x.id))add('USER_OVERRIDE',100,'You manually selected this item.');
  if(!reasons.some(r=>r.points>0))add('NO_PREFERENCE_MATCH',0,'Available as an optional activity; no personal inference was made.');
  return {contentId:x.id,title:x.title,score:reasons.reduce((a,b)=>a+b.points,0),reasons,reason_codes:reasons.map(r=>r.code),explanation:reasons.filter(r=>r.points>0).map(r=>r.explanation).join(' '),source_status:x.source_status,evidence_status:x.evidence_status,not_a_diagnosis:true as const};
 }).sort((a,b)=>b.score-a.score||a.contentId.localeCompare(b.contentId)).slice(0,limit);
}
export interface ReviewState {conceptId:string;intervalDays:number;repetitions:number;easeFactor:number;dueLocalDate:string;lastReviewedLocalDate:string|null;}
export function scheduleReview(previous:ReviewState|null,conceptId:string,rating:ReviewRating,reviewedLocalDate:string):ReviewState {
 if(!isValidLocalDate(reviewedLocalDate)|| !([0,1,2,3] as number[]).includes(rating))throw new Error('bad review input');
 if(previous&&previous.conceptId!==conceptId)throw new Error('review ID mismatch');
 const prev=previous??{conceptId,intervalDays:0,repetitions:0,easeFactor:2.5,dueLocalDate:reviewedLocalDate,lastReviewedLocalDate:null};
 const ease=Math.max(1.3,Math.min(3,Math.round((prev.easeFactor+(rating===0?-.2:rating===1?-.1:rating===2?0:.1))*100)/100));
 let n=prev.intervalDays, reps=prev.repetitions;
 if(rating===0){n=1;reps=0;}
 else if(rating===1){n=prev.repetitions===0?2:Math.max(2,Math.ceil(prev.intervalDays*1.2));reps+=1;}
 else if(rating===2){n=prev.repetitions===0?1:prev.repetitions===1?3:Math.max(1,Math.ceil(prev.intervalDays*ease));reps+=1;}
 else {n=prev.repetitions===0?3:prev.repetitions===1?6:Math.max(3,Math.ceil(prev.intervalDays*ease*1.3));reps+=1;}
 return {conceptId,intervalDays:Math.min(365,n),repetitions:reps,easeFactor:ease,dueLocalDate:addCivilDays(reviewedLocalDate,Math.min(365,n)),lastReviewedLocalDate:reviewedLocalDate};
}
export interface ReviewEvent {eventId:string;conceptId:string;timestampISO:string;timeZone:string;rating?:ReviewRating;kind:'exercise.reviewed'|'review.undone';undoEventId?:string;}
export function replayReviews(events:ReviewEvent[]):Record<string,ReviewState>{
 const undone=new Set(events.filter(e=>e.kind==='review.undone'&&e.undoEventId).map(e=>e.undoEventId!));
 const states:Record<string,ReviewState>={};const seen=new Set<string>();
 for(const e of [...events].sort((a,b)=>a.timestampISO.localeCompare(b.timestampISO)||a.eventId.localeCompare(b.eventId))){
  if(seen.has(e.eventId))continue;seen.add(e.eventId);
  if(e.kind==='exercise.reviewed'&&!undone.has(e.eventId)&&e.rating!==undefined){states[e.conceptId]=scheduleReview(states[e.conceptId]??null,e.conceptId,e.rating,toLocalDate(e.timestampISO,e.timeZone));}
 }
 return states;
}
export interface EventRecord {event_id:string;idempotency_key:string;event_type:EventType;target_id:string;timestamp_iso:string;time_zone:string;session_id:string;payload:Record<string,unknown>;}
export interface Metrics {hasData:boolean;totalEvents:number;completedActivitySessions:number;completedRehearsalSessions:number;scenarioSessionsExplored:number;programDaysCompleted:number;observedExperimentOutcomes:number;completedActivityIds:string[];lastActivityISO:string|null;}
export function aggregateMetrics(events:EventRecord[]):Metrics{
 const byKey=new Set<string>();const activity=new Set<string>(),rehearsal=new Set<string>(),scenario=new Set<string>(),days=new Set<string>(),outcomes=new Set<string>();let last:string|null=null;
 const sorted=[...events].sort((a,b)=>a.timestamp_iso.localeCompare(b.timestamp_iso)||a.event_id.localeCompare(b.event_id));
 const completedIds=new Set<string>();
 for(const e of sorted){const key=e.idempotency_key||e.event_id;if(byKey.has(key))continue;byKey.add(key);
  if(e.event_type==='activity.completed'){activity.add(e.session_id+'|'+e.target_id);completedIds.add(e.target_id);last=e.timestamp_iso;}
  if(e.event_type==='rehearsal.completed')rehearsal.add(e.session_id+'|'+e.target_id);
  if(e.event_type==='scenario.completed')scenario.add(e.session_id+'|'+e.target_id);
  if(e.event_type==='program.day_completed')days.add(e.target_id);
  if(e.event_type==='experiment.outcome_recorded')outcomes.add(e.session_id+'|'+e.target_id);
 }
 return {hasData:byKey.size>0,totalEvents:byKey.size,completedActivitySessions:activity.size,completedRehearsalSessions:rehearsal.size,scenarioSessionsExplored:scenario.size,programDaysCompleted:days.size,observedExperimentOutcomes:outcomes.size,completedActivityIds:[...completedIds].sort(),lastActivityISO:last};
}
export type ProgramAction='complete'|'skip'|'pause'|'resume'|'restart'|'stop';
export interface ProgramProgress {programId:'PCI-PROG-021';nextDayNumber:number;status:'active'|'paused'|'completed'|'stopped';daysCompleted:string[];daysSkipped:string[];revision:number;}
export function newProgramProgress():ProgramProgress{return {programId:'PCI-PROG-021',nextDayNumber:1,status:'active',daysCompleted:[],daysSkipped:[],revision:0};}
export function advanceProgram(state:ProgramProgress,action:ProgramAction):ProgramProgress{
 const p:ProgramProgress={...state,daysCompleted:[...state.daysCompleted],daysSkipped:[...state.daysSkipped],revision:state.revision+1};
 if(action==='restart')return {...newProgramProgress(),revision:p.revision};
 if(action==='stop'){p.status='stopped';return p;}
 if(action==='pause'){if(state.status==='active')p.status='paused';return p;}
 if(action==='resume'){if(state.status==='paused')p.status='active';return p;}
 if(state.status!=='active')throw new Error('cannot complete or skip inactive program');
 if(state.nextDayNumber>21)throw new Error('all days already resolved');
 const day=`PCI-DAY-${String(state.nextDayNumber).padStart(2,'0')}`;
 if(action==='complete')p.daysCompleted.push(day);else if(action==='skip')p.daysSkipped.push(day);else throw new Error('unknown program action');
 p.nextDayNumber+=1;p.status=p.nextDayNumber>21?'completed':'active';return p;
}
export type JourneyState='not_started'|'preferences_optional'|'choose_goal'|'choose_activity'|'doing_activity'|'review_optional'|'resting'|'returning';
const allowed:Record<JourneyState,JourneyState[]>={not_started:['preferences_optional','choose_goal'],preferences_optional:['choose_goal','choose_activity'],choose_goal:['choose_activity','resting'],choose_activity:['doing_activity','resting','review_optional'],doing_activity:['review_optional','resting'],review_optional:['choose_activity','resting','returning'],resting:['returning','choose_activity'],returning:['choose_activity','resting','review_optional']};
export function transitionJourney(from:JourneyState,to:JourneyState):JourneyState{if(!allowed[from].includes(to))throw new Error(`invalid journey transition ${from}=>${to}`);return to;}
/** Objective comprehension items: check an explicit answer key, never free-text meaning. */
export interface ObjectiveItem {id:string;correctOptionId:string;rationale:string;maxPoints:1;}
export function gradeObjective(items:ObjectiveItem[],responses:Record<string,string>):{metric_kind:'objective_knowledge_accuracy';correct:number;attempted:number;total:number;fraction:number|null;feedback:{id:string;status:'correct'|'incorrect'|'not_attempted';rationale:string}[]}{
 const ids=new Set<string>();let correct=0,attempted=0;
 const feedback=items.map(item=>{if(ids.has(item.id))throw new Error('duplicate objective item');ids.add(item.id);
  const answer=responses[item.id];const status:'correct'|'incorrect'|'not_attempted'=!answer?'not_attempted':answer===item.correctOptionId?'correct':'incorrect';
  if(status==='correct')correct++;if(status!=='not_attempted')attempted++;
  return {id:item.id,status,rationale:item.rationale};
 });
 return {metric_kind:'objective_knowledge_accuracy',correct,attempted,total:items.length,fraction:attempted?correct/attempted:null,feedback};
}
/** User makes every rating choice explicitly; there is no automated inference from prose. */
export interface RubricCriterion {id:string;prompt:string;anchors:{0:string;1:string;2:string};}
export function selfRateArtifact(criteria:RubricCriterion[],userRatings:Record<string,0|1|2>):{kind:'self_reported_artifact_review';ratedCount:number;pointsOnAnsweredCriteria:number;maxOnAnsweredCriteria:number;unratedIds:string[];disclaimer:string}{
 const unratedIds:string[]=[];let points=0,count=0;
 for(const c of criteria){const v=userRatings[c.id];if(v===undefined){unratedIds.push(c.id);continue;}if(v!==0&&v!==1&&v!==2)throw new Error('rating outside anchors');count++;points+=v;}
 return {kind:'self_reported_artifact_review',ratedCount:count,pointsOnAnsweredCriteria:points,maxOnAnsweredCriteria:count*2,unratedIds,disclaimer:'Self-reported completion of observable steps; not personality, mental health, unconscious change, or clinical efficacy.'};
}
