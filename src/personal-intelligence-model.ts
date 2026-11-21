/** Checkpoint 4: transparent, local-only selectors. No psychological scoring or inferred associations. */
import type {PrivateRecord, StoreName} from './types.js';
import type {AcademyCurriculum,ProgramState} from './academy-model.js';
export const INTELLIGENCE_STORES:StoreName[]=['journal_entries','reflection_notes','identity_notes','beliefs','goals','rehearsals','rehearsal_sessions','practice_sessions','experiments','predicted_outcomes','observed_outcomes','scenario_progress','program_progress','quiz_attempts','review_ratings','bookmarks'];
export type PersonalSnapshot=Partial<Record<StoreName,PrivateRecord[]>>;
export type ArchiveKind='notes'|'beliefs'|'goals'|'scenes'|'rehearsals'|'conditioning'|'feedback'|'academy'|'scenarios';
export interface TimelineItem {key:string;kind:ArchiveKind;id:string;at:string;title:string;description:string;source:PrivateRecord;module:string;refs:string[];sensitive:boolean;tags:string[]}
export interface SummaryCounts {academyDays:number;academySkipped:number;rehearsals:number;conditioning:number;experiments:number;observed:number;scenarios:number;goals:number;beliefs:number;bookmarks:number;notes:number;reflections:number}
const rows=(s:PersonalSnapshot,k:StoreName):PrivateRecord[]=>s[k]||[];
const str=(v:unknown):string=>typeof v==='string'?v:'';
const validAt=(value:unknown):string=>typeof value==='string'&&!Number.isNaN(Date.parse(value))?value:'1970-01-01T00:00:00.000Z';
export function actualCounts(s:PersonalSnapshot):SummaryCounts {
 const academy=rows(s,'program_progress').filter(r=>r.data.academy_contract==='1.0.0').flatMap(r=>Array.isArray((r.data.state as ProgramState|undefined)?.history)?(r.data.state as ProgramState).history:[]);
 return {academyDays:academy.filter(h=>h.result==='completed').length,academySkipped:academy.filter(h=>h.result==='skipped').length,
  rehearsals:rows(s,'rehearsal_sessions').filter(r=>r.data.status==='completed').length,
  conditioning:rows(s,'practice_sessions').filter(r=>r.data.conditioning_contract_version==='1.0.0'&&r.data.status==='completed').length,
  experiments:rows(s,'experiments').filter(r=>r.data.feedback_contract_version==='1.0.0').length,
  observed:rows(s,'observed_outcomes').filter(r=>r.data.feedback_contract_version==='1.0.0').length,
  scenarios:rows(s,'scenario_progress').filter(r=>r.data.status==='completed').length,
  goals:rows(s,'goals').length,beliefs:rows(s,'beliefs').length,bookmarks:rows(s,'bookmarks').length,
  notes:rows(s,'journal_entries').length,reflections:rows(s,'reflection_notes').length};
}
export function latestAcademyRun(s:PersonalSnapshot):{record:PrivateRecord;state:ProgramState}|undefined {
 const a=rows(s,'program_progress').filter(r=>r.data.academy_contract==='1.0.0'&&r.data.state).sort((a,b)=>b.created_at.localeCompare(a.created_at));
 const record=a.find(r=>(r.data.state as ProgramState).status==='in_progress')||a.find(r=>(r.data.state as ProgramState).status==='paused')||a[0];
 return record?{record,state:record.data.state as ProgramState}:undefined;
}
export function recordTitle(r:PrivateRecord):string {
 const d=r.data;
 return str(d.title)||str(d.name)||str(d.belief_statement)||str(d.statement)||str(d.goal_behavior)||str(d.protocol_id)||str(d.scenario_id)||str(d.template_id)||str(d.text).slice(0,70)||`${r.store.replace(/_/g,' ')} entry`;
}
export function recordsTimeline(s:PersonalSnapshot,curriculum?:AcademyCurriculum|null):TimelineItem[] {
 const add=(r:PrivateRecord,kind:ArchiveKind,module:string,title:string,description='',at=r.updated_at):TimelineItem=>({key:`${r.store}:${r.id}:${at}`,id:r.id,kind,at:validAt(at),title,description,source:r,module,refs:r.refs||[],sensitive:r.sensitive,tags:Array.isArray(r.data.tags)?r.data.tags.filter((x):x is string=>typeof x==='string'):[]});
 const out:TimelineItem[]=[];
 for(const r of [...rows(s,'journal_entries'),...rows(s,'reflection_notes'),...rows(s,'identity_notes')])out.push(add(r,'notes','archive',recordTitle(r),str(r.data.text)||str(r.data.note)||str(r.data.reflection)));
 for(const r of rows(s,'beliefs'))out.push(add(r,'beliefs','beliefs',recordTitle(r),'Saved belief record'));
 for(const r of rows(s,'goals'))out.push(add(r,'goals','feedback',recordTitle(r),'User-authored goal'));
 for(const r of rows(s,'rehearsals'))out.push(add(r,'scenes','theater',recordTitle(r),'Private rehearsal scene, linked by saved IDs')); 
 for(const r of rows(s,'rehearsal_sessions'))out.push(add(r,'rehearsals','theater',`Rehearsal · ${str(r.data.template_id)||'template'}`,str(r.data.status),str(r.data.completed_at)||r.updated_at));
 for(const r of rows(s,'practice_sessions'))if(r.data.conditioning_contract_version==='1.0.0')out.push(add(r,'conditioning','conditioning',`Conditioning · ${str(r.data.protocol_id)}`,str(r.data.status),str(r.data.completed_at)||r.updated_at));
 for(const r of rows(s,'observed_outcomes'))out.push(add(r,'feedback','feedback','Feedback observation','Recorded outcome for an experiment'));
 for(const r of rows(s,'experiments'))if(r.data.feedback_contract_version==='1.0.0')out.push(add(r,'feedback','feedback','Feedback iteration',str(r.data.status)));
 for(const r of rows(s,'scenario_progress'))out.push(add(r,'scenarios','scenarios',`Scenario · ${str(r.data.scenario_id)}`,str(r.data.status)));
 for(const r of rows(s,'program_progress')){
  if(r.data.academy_contract!=='1.0.0')continue;
  const state=r.data.state as ProgramState|undefined;
  for(const log of state?.history||[]){const day=curriculum?.days.find(x=>x.id===log.day_id);const safe={...r,data:{...r.data,day_id:log.day_id,day_result:log.result}};
   out.push({...add(safe,'academy','academy',`${day?.title||log.day_id} · ${log.result}`,`Day ${log.day_number} · ${log.mode}`,log.at),id:`${r.id}@${log.day_id}`});}
 }
 return out.sort((a,b)=>b.at.localeCompare(a.at));
}
export function safeArchiveSearch(items:TimelineItem[],query:string,kind:'all'|ArchiveKind,includeSensitive=false):TimelineItem[] {
 const q=query.trim().toLocaleLowerCase();return items.filter(i=>(kind==='all'||i.kind===kind)&&(!i.sensitive||includeSensitive)&&(!q||[i.title,...i.tags].some(t=>t.toLocaleLowerCase().includes(q))));
}
export interface ExplicitLink{from_id:string;to_id:string;kind:'goal_experiment'|'scene_session'|'lesson_practice'|'belief_scene'|'goal_scene'|'experiment_outcome';reason:string;to_module:string}
export function explicitLinks(s:PersonalSnapshot,curriculum?:AcademyCurriculum|null):ExplicitLink[]{
 const links:ExplicitLink[]=[];
 const goals=new Set(rows(s,'goals').map(r=>r.id));const scenes=new Set(rows(s,'rehearsals').map(r=>r.id));
 for(const exp of rows(s,'experiments')){const id=str(exp.data.goal_id);if(id&&goals.has(id))links.push({from_id:id,to_id:exp.id,kind:'goal_experiment',reason:'Saved experiment explicitly refers to this goal ID.',to_module:'feedback'});}
 for(const obs of rows(s,'observed_outcomes')){const exp=str(obs.data.experiment_id);if(exp&&rows(s,'experiments').some(e=>e.id===exp))links.push({from_id:exp,to_id:obs.id,kind:'experiment_outcome',reason:'Observation explicitly references the experiment ID.',to_module:'feedback'});}
 const beliefs=new Set(rows(s,'beliefs').map(r=>r.id));
 for(const scene of rows(s,'rehearsals')){const belief=str(scene.data.belief_id),goal=str(scene.data.goal_id);if(belief&&beliefs.has(belief))links.push({from_id:belief,to_id:scene.id,kind:'belief_scene',reason:'User explicitly linked the saved scene to the belief ID.',to_module:'theater'});if(goal&&goals.has(goal))links.push({from_id:goal,to_id:scene.id,kind:'goal_scene',reason:'User explicitly linked the saved scene to the goal ID.',to_module:'theater'});}
 for(const session of rows(s,'rehearsal_sessions')){const id=str(session.data.scene_id)||str((session.data.player as any)?.scene_id);if(id&&scenes.has(id))links.push({from_id:id,to_id:session.id,kind:'scene_session',reason:'Rehearsal session was saved with this private scene ID.',to_module:'theater'});}
 if(curriculum)for(const day of curriculum.days){
  for(const session of rows(s,'practice_sessions')){
   const protocol=str(session.data.protocol_id);const associated=Array.isArray(session.refs)?session.refs:[];
   if(day.primary_activity_id&&associated.includes(day.primary_activity_id))links.push({from_id:day.id,to_id:session.id,kind:'lesson_practice',reason:`The authored day references ${day.primary_activity_id}, which is also attached to this saved practice.`,to_module:'conditioning'});
   // Do not infer a relationship from the same chapter or from similar prose.
   void protocol;
  }
  for(const session of rows(s,'rehearsal_sessions'))if(day.optional_rehearsal_id&&session.data.template_id===day.optional_rehearsal_id)links.push({from_id:day.id,to_id:session.id,kind:'lesson_practice',reason:'This authored day names the rehearsal template saved in this session.',to_module:'theater'});
 }
 return links;
}
export interface NextSuggestion{label:string;detail:string;route:string;reason:string}
export function deterministicNext(s:PersonalSnapshot):NextSuggestion{
 const run=latestAcademyRun(s);
 if(run?.state.status==='in_progress'&&run.state.day_number<=21)return {label:`Continue Academy Day ${run.state.day_number}`,detail:'Resume the next authored learning task.',route:'academy',reason:`Days 1–${run.state.history.length} were explicitly acknowledged in this saved course run.`};
 if(run?.state.status==='paused')return {label:'Resume your paused Academy course',detail:`Day ${run.state.day_number} is ready whenever you are.`,route:'academy',reason:'Your most recent course run is paused by your choice.'};
 const pending=rows(s,'experiments').filter(r=>r.data.feedback_contract_version==='1.0.0'&&!rows(s,'observed_outcomes').some(o=>o.data.experiment_id===r.id));
 if(pending.length)return {label:'Review a planned experiment',detail:'Record an observation only when you have one.',route:'feedback',reason:`${pending.length} explicit feedback iteration${pending.length===1?' has':'s have'} no saved observation.`};
 const latestScene=rows(s,'rehearsals').sort((a,b)=>b.updated_at.localeCompare(a.updated_at))[0];
 if(latestScene)return {label:'Practice a saved rehearsal scene',detail:'Choose a voluntary practice session.',route:'theater',reason:'A user-authored rehearsal scene is available in private storage.'};
 return {label:'Choose a small goal or belief',detail:'Start with a concrete action or question, then connect it to the book.',route:'feedback',reason:'No in-progress Academy course, pending feedback observation, or saved rehearsal scene was found.'};
}
