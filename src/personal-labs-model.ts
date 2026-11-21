/** PCI Stage 10: device-local reflections only. No latent trait inference or clinical rating. */
export const LAB_DOMAINS = [
  {id:'professional',label:'Professional performance'},
  {id:'communication',label:'Communication'},
  {id:'coaching',label:'Sports and coaching'},
  {id:'relationships',label:'Relationships'},
  {id:'confidence',label:'Confidence'},
  {id:'goals',label:'General goals'}
] as const;
export type Domain = typeof LAB_DOMAINS[number]['id'];
export type EvidenceKind = 'supporting'|'counter'|'context';
export interface EvidenceInput { id:string; kind:EvidenceKind; observation:string; occurred_on:string; interpretation_note?:string }
export interface BeliefInput {
 statement:string; domain:Domain; context:string; observed_facts:string;
 interpretation:string; evidence_for:EvidenceInput[]; evidence_against:EvidenceInput[];
 situational_barriers:string; alternative_explanations:string; working_hypothesis:string;
 small_action:string; prediction:string; follow_up_date:string; conviction:number|null;
 tags:string[]; concept_ids:string[];
}
export interface InventoryInput {domain:Domain;self_description:string;context:string;observation:string;goal:string;concept_ids:string[]}
export interface ReflectionInput {domain:Domain;prompt:string;observation:string;interpretation:string;next_step:string;belief_id:string|null;concept_ids:string[]}
export interface BeliefSnapshot extends BeliefInput {status:'active'|'draft'; revision_number:number; first_saved_at:string; latest_reviewed_at:string|null}
export interface RevisionComparison {changed:string[]; prior_rating:number|null; latest_rating:number|null; disclaimer:string}
export const MAX_FIELD=5000;
export const STARTER_BELIEF:BeliefInput={statement:'',domain:'confidence',context:'',observed_facts:'',interpretation:'',evidence_for:[],evidence_against:[],situational_barriers:'',alternative_explanations:'',working_hypothesis:'',small_action:'',prediction:'',follow_up_date:'',conviction:null,tags:[],concept_ids:[]};
/** Explicit matching only. Each ID exists in the Stage09 canonical index. No behavioral diagnosis. */
export const DOMAIN_CONCEPTS:Record<Domain,string[]>={
 professional:['PCI-C-CH01-001','PCI-C-CH04-001','PCI-C-CH13-001'],
 communication:['PCI-C-CH05-001','PCI-C-CH11-001','PCI-C-CH04-001'],
 coaching:['PCI-C-CH02-002','PCI-C-CH09-001','PCI-C-CH13-002'],
 relationships:['PCI-C-CH10-001','PCI-C-CH11-001','PCI-C-CH04-001'],
 confidence:['PCI-C-CH01-001','PCI-C-CH01-002','PCI-C-CH04-001'],
 goals:['PCI-C-CH02-002','PCI-C-CH05-003','PCI-C-CH14-003']
};
export function isDomain(s:unknown):s is Domain {return typeof s==='string'&&LAB_DOMAINS.some(x=>x.id===s)}
export function cleanText(value:unknown,max=MAX_FIELD):string {return String(value||'').trim().slice(0,max)}
export function cleanEvidence(rows:EvidenceInput[],kind:EvidenceKind):EvidenceInput[] {
 return rows.filter(r=>cleanText(r.observation).length>0).slice(0,20).map(r=>({id:r.id||'unspecified',kind,observation:cleanText(r.observation,1500),occurred_on:r.occurred_on||'',interpretation_note:cleanText(r.interpretation_note,1500)}));
}
export function normalizeBelief(input:BeliefInput):BeliefInput {
 const result={...input,statement:cleanText(input.statement,500),context:cleanText(input.context),observed_facts:cleanText(input.observed_facts),interpretation:cleanText(input.interpretation),situational_barriers:cleanText(input.situational_barriers),alternative_explanations:cleanText(input.alternative_explanations),working_hypothesis:cleanText(input.working_hypothesis),small_action:cleanText(input.small_action),prediction:cleanText(input.prediction),evidence_for:cleanEvidence(input.evidence_for,'supporting'),evidence_against:cleanEvidence(input.evidence_against,'counter'),tags:[...new Set(input.tags.filter(t=>t.length>0))].slice(0,12),concept_ids:[...new Set(input.concept_ids.filter(id=>/^PCI-C-CH\d{2}-\d+$/.test(id)))].slice(0,20)};
 if(!isDomain(result.domain))throw Error('Choose a valid reflection domain.');
 if(result.conviction!==null&&(!Number.isInteger(result.conviction)||result.conviction<0||result.conviction>100))throw Error('Conviction must be an optional self-rating from 0 to 100.');
 if(result.follow_up_date&&!/^\d{4}-\d{2}-\d{2}$/.test(result.follow_up_date))throw Error('Follow-up date must be YYYY-MM-DD.');
 return result;
}
export function validateBelief(input:BeliefInput,mode:'draft'|'active'):string[]{
 try {const b=normalizeBelief(input);const errors:string[]=[];if(!b.statement&&mode==='active')errors.push('Write a specific belief in your own words.');if(mode==='active'&&!b.context)errors.push('Add a situation where this belief appears.');if(mode==='active'&&!b.working_hypothesis)errors.push('Add a realistic, testable working hypothesis.');return errors;}catch(e){return [String(e)]}
}
export function validateInventory(input:InventoryInput):string[]{return [!isDomain(input.domain)?'Choose a domain.':'',!cleanText(input.self_description)?'Describe your current self-perception.':'',!cleanText(input.observation)?'Record 1 observation (not a diagnosis).':''].filter(Boolean)}
export function validateReflection(input:ReflectionInput):string[]{return [!isDomain(input.domain)?'Choose a domain.':'',!cleanText(input.observation)?'Write what you observed.':''].filter(Boolean)}
export function compareBeliefs(a:BeliefInput,b:BeliefInput):RevisionComparison {
 const fields=['statement','domain','context','observed_facts','interpretation','evidence_for','evidence_against','situational_barriers','alternative_explanations','working_hypothesis','small_action','prediction','follow_up_date','conviction'];
 return {changed:fields.filter(k=>JSON.stringify(a[k as keyof BeliefInput])!==JSON.stringify(b[k as keyof BeliefInput])),prior_rating:a.conviction,latest_rating:b.conviction,disclaimer:'Ratings are your own observations over time. A difference does not show treatment effectiveness or unconscious change.'};
}
export function recommendConcepts(domain:Domain,chosen:string[]=[]):{id:string;reason:string}[]{
 const choices=[...new Set([...chosen,...DOMAIN_CONCEPTS[domain]])];return choices.slice(0,5).map(id=>({id,reason:chosen.includes(id)?'You selected this source concept.':'Related to your selected area, not inferred from your personality.'}));
}
export function stage10EventType(action:'created'|'updated'|'reflected'|'experiment_planned'|'outcome_recorded'):'belief.created'|'belief.revised'|'journal.saved'|'experiment.planned'|'experiment.outcome_recorded'{return {created:'belief.created',updated:'belief.revised',reflected:'journal.saved',experiment_planned:'experiment.planned',outcome_recorded:'experiment.outcome_recorded'}[action] as any}
