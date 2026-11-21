/** Stage 12: educational guidance builder. It does NOT modify source templates or publish scenes. */
import type {RehearsalTemplate,SceneFields} from './theater-model.js';

export interface VisiblePhase { title:string; body:string; context:Array<{label:string;value:string}>; missing_scene:boolean }
const PHASE_FIELDS: Array<Array<[keyof SceneFields,string,string]>> = [
 [['title','Your private scene','This can be a fictional or low-stakes situation.'],['uncertainty','What is still uncertain','You cannot predict every response.']],
 [['setting','Setting','Choose a realistic, safe place or time.'],['sensory_detail','Optional setting cue','You may describe the scene in words instead.']],
 [['goal_behavior','Behavior to practice','Describe one observable action, not a personality trait.'],['cue','Starting cue','Choose a cue you can recognize without perfect imagery.']],
 [['obstacle','Possible obstacle','Allow for a practical difficulty without catastrophizing.'],['prepared_response','Possible response','Plan one flexible alternative you control.']],
 [['next_action','Real-world next action','Choose a small action; rehearsal alone is not physical practice.'],['uncertainty','Remaining uncertainty','Other people and circumstances remain outside your control.']]
];
const WRITTEN_ALTERNATIVES=[
 'Define your scope in 1 sentence. Write what you can control and what remains uncertain. It is fine to stop here.',
 'Describe the setting with factual details or a short checklist; no visualization or sensory imagination is required.',
 'Draft what you might actually say or do. A 1-sentence script or action checklist is enough.',
 'Write an obstacle on 1 line and a flexible response on the next. Compare the response with your real-world constraints.',
 'Record 1 optional next action and a way to notice what actually happens. No outcome is guaranteed.'
];
export function phaseVisibleContent(template:RehearsalTemplate,phaseIndex:number,mode:'standard'|'written'='standard',scene:SceneFields|null=null,missingScene=false):VisiblePhase {
 const phase=template.phases[phaseIndex];if(!phase)throw Error('Unknown rehearsal phase');
 const context=scene?PHASE_FIELDS[Math.min(phaseIndex,4)].map(([field,label,fallback])=>({label,value:scene[field]?.trim()||fallback})):[];
 const intro=phaseIndex===0?`${template.intro} Specific rehearsal setting: ${template.scene}.`:phaseIndex===1?template.scene:phaseIndex===4?(template.real_world_action_prompt||'Choose a safe real-world next action.') : '';
 // The original phase.guidance remains fully visible; written mode adds a stage-specific translation.
 const body=[`${template.title}: ${phase.guidance}`,intro,mode==='written'?WRITTEN_ALTERNATIVES[Math.min(phaseIndex,4)]:null].filter(Boolean).join(' ');
 return {title:phase.title,body,context,missing_scene:missingScene};
}
