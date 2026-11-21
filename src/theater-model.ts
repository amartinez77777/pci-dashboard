/** PCI Stage11 · deterministic rehearsal player, no psychological scoring or hidden AI. */
export type TimingMode='full'|'short'|'custom'|'untimed';
export type SessionStatus='ready'|'running'|'paused'|'review'|'completed'|'stopped';
export interface RehearsalPhase{id:string;title:string;guidance:string;suggested_seconds:number;text_mode_equivalent?:string;manual_next_supported?:boolean;pause_after?:boolean}
export interface RehearsalTemplate{id:string;title:string;record_type:string;content_version:string;chapter_id:string;origin:string;intro:string;scene:string;real_world_action_prompt?:string;linked_concept_ids:string[];source_refs:Array<{source_id:string;pdf_page:number;printed_page?:number|null}>;phases:RehearsalPhase[];timing:{type:string;full_seconds:number;reduced_seconds:number;no_timer_supported:boolean;book_duration_claimed:boolean;auto_advance:boolean};safety?:Record<string,boolean>}
export interface SceneFields{title:string;setting:string;goal_behavior:string;obstacle:string;prepared_response:string;cue:string;sensory_detail:string;uncertainty:string;next_action:string;template_id:string;concept_id:string;belief_id:string;goal_id:string}
export const emptyScene:SceneFields={title:'',setting:'',goal_behavior:'',obstacle:'',prepared_response:'',cue:'',sensory_detail:'',uncertainty:'',next_action:'',template_id:'PCI-RH-001',concept_id:'',belief_id:'',goal_id:''};
export const SCENE_FIELDS:(keyof SceneFields)[]=['title','setting','goal_behavior','obstacle','prepared_response','cue','sensory_detail','uncertainty','next_action','template_id','concept_id','belief_id','goal_id'];
export function validateScene(scene:SceneFields,availableTemplates:string[]):string[]{let issues:string[]=[];if(!scene.title.trim())issues.push('Give the private scene a short title.');for(const field of SCENE_FIELDS)if(scene[field].length>(field==='title'?120:field.endsWith('_id')?80:600))issues.push(`${field} exceeds its limit.`);if(!availableTemplates.includes(scene.template_id))issues.push('The selected public template was not found.');return issues}
export function cleanScene(scene:SceneFields):SceneFields {const o={...scene};for(const f of SCENE_FIELDS)o[f]=scene[f].trim();return o}
export interface PlayerState{status:SessionStatus;template_id:string;template_version:string;scene_id:string|null;mode:TimingMode;custom_seconds:number|null;phase_index:number;phase_elapsed_ms:number;elapsed_ms:number;running_since_wall_ms:number|null;skipped_phase_ids:string[];started_at:string|null;finished_at:string|null;interrupted:boolean}
export function initialPlayer(template:RehearsalTemplate,mode:TimingMode='full',scene_id:string|null=null,custom_seconds:number|null=null):PlayerState{return {status:'ready',template_id:template.id,template_version:template.content_version,scene_id,mode,custom_seconds,phase_index:0,phase_elapsed_ms:0,elapsed_ms:0,running_since_wall_ms:null,skipped_phase_ids:[],started_at:null,finished_at:null,interrupted:false}}
export function phaseBudgets(t:RehearsalTemplate,p:PlayerState):number[]|null{if(p.mode==='untimed')return null;const total=p.mode==='full'?t.timing.full_seconds:p.mode==='short'?t.timing.reduced_seconds:p.custom_seconds||t.timing.full_seconds;if(!Number.isSafeInteger(total)||total<30||total>3600)throw Error('Optional session length must be between 30 and 3,600 seconds.');const weights=t.phases.map(x=>x.suggested_seconds);const weightSum=weights.reduce((a,b)=>a+b,0);if(weightSum<=0)throw Error('Invalid phase lengths.');const ms=total*1000;const scaled=weights.map(x=>Math.floor(ms*x/weightSum));scaled[scaled.length-1]+=ms-scaled.reduce((a,b)=>a+b,0);return scaled}
function effectiveDelta(p:PlayerState,now:number):number{return p.status==='running'&&p.running_since_wall_ms!==null?Math.max(0,now-p.running_since_wall_ms):0}
/** Wall-clock anchors, not interval tick counters, determine elapsed time after tab suspension. */
export function settleClock(p:PlayerState,t:RehearsalTemplate,now:number):PlayerState{
 if(p.status!=='running')return p;
 const delta=effectiveDelta(p,now);
 let index=p.phase_index, phaseMs=p.phase_elapsed_ms+delta;
 const budgets=phaseBudgets(t,p);
 // All inherited Stage 11 templates specify manual advancement. A suggested duration
 // is a cue, not permission to advance or conclude a session.
 if(!budgets || !t.timing.auto_advance)
  return {...p,phase_elapsed_ms:phaseMs,elapsed_ms:p.elapsed_ms+delta,running_since_wall_ms:now};
 // For genuinely auto-enabled future templates, individual pause_after flags still win.
 while(index<budgets.length-1 && phaseMs>=budgets[index] && !t.phases[index].pause_after){
  phaseMs-=budgets[index]; index++;
 }
 if(index===budgets.length-1 && phaseMs>=budgets[index] && !t.phases[index].pause_after)
  return {...p,status:'review',running_since_wall_ms:null,elapsed_ms:p.elapsed_ms+delta,phase_index:index,phase_elapsed_ms:budgets[index]};
 return {...p,phase_index:index,phase_elapsed_ms:phaseMs,elapsed_ms:p.elapsed_ms+delta,running_since_wall_ms:now};
}
export function startPlayer(p:PlayerState,now:number):PlayerState{if(p.status==='completed'||p.status==='stopped')throw Error('This session is closed.');if(p.status==='review')return p;if(p.status==='running')return p;return {...p,status:'running',running_since_wall_ms:now,started_at:p.started_at||new Date(now).toISOString(),interrupted:false}}
export function pausePlayer(p:PlayerState,t:RehearsalTemplate,now:number):PlayerState{const v=settleClock(p,t,now);return v.status==='running'?{...v,status:'paused',running_since_wall_ms:null}:v}
export function stepPlayer(p:PlayerState,t:RehearsalTemplate,now:number,direction:'next'|'previous',skip=false):PlayerState{let v=settleClock(p,t,now);if(v.status==='completed'||v.status==='stopped')return v;const newIndex=Math.max(0,Math.min(t.phases.length-1,v.phase_index+(direction==='next'?1:-1)));const skipped=skip?[...new Set([...v.skipped_phase_ids,t.phases[v.phase_index].id])]:v.skipped_phase_ids;return {...v,phase_index:newIndex,phase_elapsed_ms:0,skipped_phase_ids:skipped,status:direction==='next'&&v.phase_index===t.phases.length-1?'review':v.status==='review'?'paused':v.status,running_since_wall_ms:v.status==='running'?now:null}}
export function resetPlayer(p:PlayerState,t:RehearsalTemplate):PlayerState{return initialPlayer(t,p.mode,p.scene_id,p.custom_seconds)}
export function finishPlayer(p:PlayerState,t:RehearsalTemplate,now:number):PlayerState{const v=settleClock(p,t,now);if(v.status==='stopped')throw Error('Stopped sessions cannot be completed.');if(v.status==='completed')return v;return {...v,status:'completed',running_since_wall_ms:null,finished_at:new Date(now).toISOString()}}
export function stopPlayer(p:PlayerState,t:RehearsalTemplate,now:number):PlayerState{const v=settleClock(p,t,now);if(v.status==='completed')return v;return {...v,status:'stopped',running_since_wall_ms:null,finished_at:new Date(now).toISOString()}}
export function interruptOnLoad(p:PlayerState):PlayerState{return p.status==='running'?{...p,status:'paused',running_since_wall_ms:null,interrupted:true}:p}
export function formatElapsed(ms:number):string{const seconds=Math.floor(Math.max(0,ms)/1000);return `${Math.floor(seconds/60).toString().padStart(2,'0')}:${(seconds%60).toString().padStart(2,'0')}`}
export function validateTemplate(t:RehearsalTemplate):string[]{const issues:string[]=[];if(!t.id||!t.phases.length||!t.title)issues.push('Missing template identity or phases.');if(t.origin!=='PCI_adaptation')issues.push('This player only accepts reviewed PCI adaptations; book prescriptions appear as source links.');if(t.timing.book_duration_claimed||t.timing.type!=='optional_app_design')issues.push('App timing cannot be attributed to book.');if(t.phases.some(x=>!x.id||!x.guidance||x.suggested_seconds<1))issues.push('Missing or invalid phase.');if(t.timing.full_seconds!==t.phases.reduce((x,y)=>x+y.suggested_seconds,0))issues.push('The phase durations do not equal the declared full time.');return issues}
