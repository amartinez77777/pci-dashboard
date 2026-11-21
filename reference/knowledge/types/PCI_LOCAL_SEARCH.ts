import type { PCISearchDocument } from './PCI_KNOWLEDGE_TYPES';
/* Deterministic local-only search; index is generated at build time, no network or AI dependencies. */
export function searchPCI(q:string, docs:PCISearchDocument[], inverted:Record<string,string[]>, limit=20):PCISearchDocument[] {
 const tokens=Array.from(new Set((q.toLowerCase().normalize('NFKD').replace(/[^a-z0-9]+/g,' ').trim().match(/[a-z0-9]+/g)||[]).filter(w=>w.length>2)));
 const counts=new Map<string,number>();
 for (const term of tokens) for (const id of (inverted[term]||[])) counts.set(id,(counts.get(id)||0)+1);
 const byID=new Map(docs.map(d=>[d.id,d] as const));
 return [...counts].sort((a,b)=>b[1]-a[1]||a[0].localeCompare(b[0])).slice(0,limit).map(([id])=>byID.get(id)).filter((x):x is PCISearchDocument=>Boolean(x));
}
