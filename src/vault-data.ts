import {fetchJson,chapterNumber,getConcepts,getActivities,lookupConcept} from './data.js';
import type {Concept,Chapter,Activity,SourceRef} from './types.js';
import type {VaultSearchRow,VaultGraphEdge} from './vault-search.js';
export interface FullRecord {id:string;title:string;chapter_id?:string;content?:string;source_status?:string;evidence_status?:string;source_refs?:SourceRef[];[key:string]:any}
export interface ChapterResearch {chapter:Chapter;concepts:Concept[];author_practices:FullRecord[];educational_exercises:FullRecord[];applications:FullRecord[];anecdotes:FullRecord[];claims:FullRecord[];evidence_assessments:FullRecord[];activity_links:Array<{id:string;title:string;concept_ids:string[];origin:string;estimated_minutes:number;source_refs:SourceRef[]}>}
export const getVaultSearch=()=>fetchJson<VaultSearchRow[]>('data/vault/search-index.json');
export const getVaultGraph=()=>fetchJson<VaultGraphEdge[]>('data/vault/graph.json');
export const getVaultTopics=()=>fetchJson<{definitions:Record<string,{tags:string[];description:string}>;record_ids:Record<string,string[]>}>('data/vault/topics.json');
export const getVaultCitations=()=>fetchJson<Array<{id:string;pdf_page:number;printed_page:number|null;source_status:string}>>('data/vault/citations.json');
export function getChapterResearch(num:number):Promise<ChapterResearch>{if(!Number.isInteger(num)||num<1||num>16)return Promise.reject(new Error('Chapter outside the source edition'));return fetchJson<ChapterResearch>(`data/vault/chapters/${String(num).padStart(2,'0')}.json`)}
export async function lookupVaultRecord(id:string):Promise<{record:FullRecord|null;kind:string;chapter:ChapterResearch|null}>{
 const match=/^PCI-(?:C|AP|EDU|APP|ACT)-CH(\d{2})-\d+$/.exec(id);if(!match)return {record:null,kind:'unknown',chapter:null};
 const num=Number(match[1]);if(num<1||num>16)return {record:null,kind:'unknown',chapter:null};
 const ch=await getChapterResearch(num);const groups:Record<string,FullRecord[]>={concept:ch.concepts,author_practice:ch.author_practices,educational_exercise:ch.educational_exercises,application:ch.applications};
 if(id.startsWith('PCI-ACT-')){const activity=(await getActivities(num)).find(x=>x.id===id);return {record:(activity as FullRecord|null)||null,kind:'activity',chapter:ch}}
 for(const [kind,rows] of Object.entries(groups)){const record=rows.find(x=>x.id===id);if(record)return {record,kind,chapter:ch}}
 return {record:null,kind:'unknown',chapter:ch};
}
export function relatedActivityLinks(conceptId:string,ch:ChapterResearch):Array<{id:string;title:string;concept_ids:string[];origin:string;estimated_minutes:number;source_refs:SourceRef[]}>{return ch.activity_links.filter(a=>a.concept_ids.includes(conceptId))}
