/** Pure, deterministic and explainable search over original research paraphrases.
 * No external service, semantic AI, psychological relevance claims or unsafe markup.
 */
export type VaultKind='concept'|'author_practice'|'educational_exercise'|'application';
export interface VaultSearchRow {id:string;chapter_id:string;title:string;summary:string;kind:VaultKind;source_status:string;evidence_status:string;origin:string;synonyms:string[];tags:string[];themes:string[];search_prose:string;source_refs:Array<{source_id:string;pdf_page:number;printed_page?:number|null}>}
export interface VaultFilters {chapter?:number;kind?:string;evidence?:string;origin?:string;topic?:string}
export interface VaultSearchHit {row:VaultSearchRow;match_score:number;match_reasons:string[]}
export function normalized(input:string):string {return input.normalize('NFKD').replace(/[\u0300-\u036f]/g,'').toLowerCase().replace(/[^a-z0-9]+/g,' ').trim().replace(/\s+/g,' ')}
export function parseSearchQuery(query:string):{phrases:string[];terms:string[]} {
 const phrases:string[]=[],terms:string[]=[];for(const m of query.slice(0,240).matchAll(/"([^"]+)"|(\S+)/g)){
  const clean=normalized(m[1]||m[2]||'');if(!clean)continue;
  if(m[1])phrases.push(clean);else terms.push(...clean.split(' '));
 }
 return {phrases:phrases.slice(0,8),terms:terms.slice(0,12)};
}
export function searchVault(rows:VaultSearchRow[],query:string,filters:VaultFilters={}):VaultSearchHit[]{
 const {phrases,terms}=parseSearchQuery(query);
 return rows.flatMap(row=>{
  if(filters.chapter && !row.chapter_id.endsWith('-'+String(filters.chapter).padStart(2,'0')))return [];
  if(filters.kind && row.kind!==filters.kind)return [];
  if(filters.evidence && row.evidence_status!==filters.evidence)return [];
  if(filters.origin && row.origin!==filters.origin)return [];
  if(filters.topic && !row.themes.includes(filters.topic))return [];
  const title=normalized(row.title),syn=normalized(row.synonyms.join(' ')),tag=normalized(row.tags.join(' ')),theme=normalized(row.themes.join(' ')),sum=normalized(row.summary),prose=normalized(row.search_prose),id=normalized(row.id);
  const weighted=[{s:title,w:12,why:'Title'},{s:syn,w:7,why:'Alternate terms'},{s:tag,w:5,why:'Topic tags'},{s:theme,w:4,why:'Topic classification'},{s:sum,w:3,why:'Summary'},{s:prose,w:1,why:'Research prose'},{s:id,w:6,why:'Record ID'}];
  let score=0;const why=new Set<string>();
  for(const word of [...phrases,...terms]){
   let best=0,bestWhy='';for(const field of weighted){if(field.s.includes(word) && field.w>best){best=field.w;bestWhy=field.why}}
   if(!best)return [];score+=best;if(bestWhy)why.add(bestWhy);
  }
  if(terms.length||phrases.length){if(title===normalized(query))score+=20;}
  return [{row,match_score:score,match_reasons:[...why]}];
 }).sort((a,b)=>b.match_score-a.match_score||a.row.chapter_id.localeCompare(b.row.chapter_id)||a.row.title.localeCompare(b.row.title)||a.row.id.localeCompare(b.row.id));
}
export interface VaultGraphEdge{id:string;from_id:string;to_id:string;chapter_id:string;relationship_type:string;rationale:string;source_status:string;evidence_status:string;confidence?:string;supporting_source_refs:Array<{source_id:string;pdf_page:number;printed_page?:number|null}>;source_refs:Array<{source_id:string;pdf_page:number;printed_page?:number|null}>}
export function neighborhood(edges:VaultGraphEdge[],center:string,type=''):VaultGraphEdge[]{return edges.filter(e=>(e.from_id===center||e.to_id===center)&&(!type||e.relationship_type===type)).sort((a,b)=>a.id.localeCompare(b.id))}
export function validateGraph(edges:VaultGraphEdge[],ids:Set<string>):string[]{return edges.flatMap(e=>(!ids.has(e.from_id)||!ids.has(e.to_id)||!e.rationale.trim()||!e.supporting_source_refs?.length)?[e.id]:[])}
export function getCitationLabel(ref:{pdf_page:number;printed_page?:number|null}):string{return `PDF p. ${ref.pdf_page}${ref.printed_page==null?'':` · printed p. ${ref.printed_page}`}`}
