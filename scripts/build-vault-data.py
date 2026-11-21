"""Deterministically derive Stage 09 public, source-safe read models from preserved Stage 05/06 research.
No source record is edited; these are navigational projections, not factual corrections.
"""
import json,re,unicodedata,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'reference/knowledge/data'; OUT=ROOT/'public/data/vault'; OUT.mkdir(parents=True,exist_ok=True)
CATEGORIES={'concepts':'PCI_CONCEPTS','author_practices':'PCI_AUTHOR_PRACTICES','educational_exercises':'PCI_EDUCATIONAL_EXERCISES','applications':'PCI_APPLICATIONS','anecdotes':'PCI_ANECDOTES','claims':'PCI_CLAIMS','evidence_assessments':'PCI_EVIDENCE_ASSESSMENTS','citations':'PCI_CITATIONS','relationships':'PCI_RELATIONSHIPS'}
arrays={name:json.loads((SRC/(fn+'.json')).read_text()) for name,fn in CATEGORIES.items()}
chapters=json.loads((ROOT/'public/data/chapter-index.json').read_text()); activities={c['id']:json.loads((ROOT/f"public/data/activities/{c['index_position']:02d}.json").read_text()) for c in chapters}
search=[]; refs={c['id'] for c in arrays['concepts']}; citation_ids={x['id'] for x in arrays['citations']}
THEMES=json.loads((ROOT/'reference/knowledge/indexes/PCI_THEME_INDEX.json').read_text())
THEME_IDS=THEMES.get('record_ids',{}); THEME_DEFS=THEMES['definitions'];
def theme_keys(rec):
    return sorted([k for k,v in THEME_IDS.items() if isinstance(v,list) and rec['id'] in v]) or []
def norm(s):
    return re.sub(r'\s+',' ',re.sub(r'[^\w\s]',' ',unicodedata.normalize('NFKD',str(s)).encode('ascii','ignore').decode().lower())).strip()
for chapter in chapters:
    n=chapter['index_position']; cid=chapter['id']
    dataset={'chapter':chapter}
    for group in ['concepts','author_practices','educational_exercises','applications','anecdotes','claims','evidence_assessments']:
        dataset[group]=[r for r in arrays[group] if r.get('chapter_id')==cid]
    dataset['activity_links']=[{'id':a['id'],'title':a['title'],'concept_ids':a['concept_ids'],'source_refs':a['source_refs'],'origin':a['origin'],'estimated_minutes':a['estimated_minutes']} for a in activities[cid]]
    path=OUT/'chapters'/f'{n:02}.json';path.parent.mkdir(exist_ok=True,parents=True);path.write_text(json.dumps(dataset,ensure_ascii=False,separators=(',',':'))+'\n')
for kind in ['concepts','author_practices','educational_exercises','applications']:
 for r in arrays[kind]:
    title=r['title']; description=(r.get('thesis') or r.get('content') or '')[:400]
    terms=r.get('terms',{})
    synonyms=[]
    if isinstance(terms,dict):
        for t in [terms.get('primary'),terms.get('definition')]:
            if isinstance(t,str) and t!=title:synonyms.append(t[:100])
    tags=r.get('tags',[])
    themes=theme_keys(r)
    hay=' '.join(str(r.get(k) or '') for k in ('content','thesis','author_mechanism','application','conditions_and_limits','common_misreading','alternative_explanation','timing_as_printed_or_paraphrased'))
    # searchable is a **paraphrased** original research projection; no full copyrighted PDF content.
    search.append({'id':r['id'],'chapter_id':r.get('chapter_id'),'title':title,'summary':description,'kind': {'concepts':'concept','author_practices':'author_practice','educational_exercises':'educational_exercise','applications':'application'}[kind],
       'evidence_status':r.get('evidence_status','not_assessed'),'source_status':r.get('source_status','provisional'),
       'origin':r.get('exercise_origin') or ('book' if kind=='author_practices' else 'PCI_adaptation' if kind in ('educational_exercises','applications') else 'book_claim'),
       'synonyms':synonyms,'tags':tags if isinstance(tags,list) else [],'themes':themes,'search_prose':hay[:1200],
       'source_refs':r.get('source_refs',[])[:2]})
(OUT/'search-index.json').write_text(json.dumps(search,ensure_ascii=False,separators=(',',':'))+'\n')
edges=[];excluded=[]
for r in arrays['relationships']:
    if r.get('from_id') not in refs or r.get('to_id') not in refs or not r.get('rationale'):
        excluded.append({'id':r['id'],'reason':'unresolved_endpoint_or_missing_rationale'});continue
    edges.append({k:r.get(k) for k in ['id','from_id','to_id','chapter_id','relationship_type','rationale','source_status','evidence_status','confidence','supporting_source_refs','source_refs']})
(OUT/'graph.json').write_text(json.dumps(edges,ensure_ascii=False,separators=(',',':'))+'\n')
(OUT/'citations.json').write_text(json.dumps([{k:x.get(k) for k in ['id','pdf_page','printed_page','source_status','edition_id']} for x in arrays['citations']],ensure_ascii=False,separators=(',',':'))+'\n')
(OUT/'topics.json').write_text(json.dumps({'definitions':THEME_DEFS,'record_ids':THEME_IDS,'methodology':'Source-index lexical/topic navigation. Classification is not empirical evidence.'},ensure_ascii=False,separators=(',',':'))+'\n')
report={'version':'1.0.0','research_data_version':'1.0.0','source_hash':'4dd7a311a21af58aa075176abb48fd60b348c70bb314a2ca09f66383922e7e9b','total_search_entries':len(search),'concepts':len(arrays['concepts']),'author_practices':len(arrays['author_practices']),'educational_exercises':len(arrays['educational_exercises']),'applications':len(arrays['applications']),'graph_edges_included':len(edges),'graph_edges_excluded':excluded,'source_citations':len(citation_ids),'chapter_data':{c['id']:{k:len([x for x in arrays[k] if x.get('chapter_id')==c['id']]) for k in ['concepts','author_practices','educational_exercises','applications','anecdotes','claims','evidence_assessments']} for c in chapters}}
(ROOT/'audit/PCI_STAGE09_DATA_PROJECTION.json').write_text(json.dumps(report,indent=2)+'\n')
print('Generated:',report['total_search_entries'],'search rows,',len(edges),'edges;',len(excluded),'excluded; chapter packs:',len(chapters))
