import type {Chapter,Concept,ConceptIndex,Activity,Scenario,Rehearsal,Curriculum} from './types.js';
// All records are immutable, source-owned assets. No private data is imported here.
const inflight = new Map<string,Promise<unknown>>();
export async function fetchJson<T>(path:string):Promise<T> {
  if (!/^data\/[a-z0-9/_-]+\.json$/i.test(path)) throw new Error('Unsupported public data path');
  if(!inflight.has(path)) {
    inflight.set(path,fetch(`./${path}`,{cache:'force-cache'}).then(async r=>{if(!r.ok) throw new Error(`Knowledge file unavailable (${r.status}): ${path}`); return r.json()}).catch(err=>{inflight.delete(path);throw err}));
  }
  return await inflight.get(path) as T;
}
export function chapterNumber(id:string):number|null {const m=/^PCI-CH-(\d{2})$/.exec(id);if(!m)return null;const n=Number(m[1]);return n>=1&&n<=16?n:null}
export function sectionPath(kind:'concepts'|'activities'|'relationships'|'scenarios',n:number):string {if(!Number.isInteger(n)||n<1||n>16) throw new Error('Chapter out of range');return `data/${kind}/${String(n).padStart(2,'0')}.json`}
export const getChapters=()=>fetchJson<Chapter[]>('data/chapter-index.json');
export const getConceptIndex=()=>fetchJson<ConceptIndex[]>('data/concept-index.json');
export const getConcepts=(n:number)=>fetchJson<Concept[]>(sectionPath('concepts',n));
export const getActivities=(n:number)=>fetchJson<Activity[]>(sectionPath('activities',n));
export const getScenarios=(n:number)=>fetchJson<Scenario[]>(sectionPath('scenarios',n));
export const getRelationships=(n:number)=>fetchJson<Record<string,unknown>[]>(sectionPath('relationships',n));
export const getRehearsals=()=>fetchJson<Rehearsal[]>('data/rehearsals.json');
export const getCurriculum=()=>fetchJson<Curriculum>('data/curriculum.json');
export async function lookupConcept(id:string):Promise<Concept|null> {const m=/^PCI-C-CH(\d{2})-\d+$/.exec(id);if(!m)return null;const n=Number(m[1]);if(n<1||n>16)return null;return (await getConcepts(n)).find(x=>x.id===id) || null}
export async function lookupActivity(id:string):Promise<Activity|null> {const m=/^PCI-ACT-CH(\d{2})-\d+$/.exec(id);if(!m)return null;const n=Number(m[1]);if(n<1||n>16)return null;return (await getActivities(n)).find(x=>x.id===id) || null}
export async function searchConceptIndex(q:string,chapter?:number):Promise<ConceptIndex[]> {const rows=await getConceptIndex();const words=q.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);return rows.filter(c=>(!chapter||chapterNumber(c.chapter_id)===chapter) && words.every(w=>(c.title+' '+c.description+' '+c.id).toLocaleLowerCase().includes(w))).slice(0,100)}
