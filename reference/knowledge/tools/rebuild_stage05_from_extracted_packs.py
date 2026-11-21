#!/usr/bin/env python3
"""PCI Stage 05 deterministic consolidation. Inputs are extracted earlier packs; no PDF redistribution."""
import argparse, os, json, copy, hashlib, glob, re, collections, pathlib, shutil, itertools, unicodedata
from datetime import date
P=pathlib.Path
j=lambda p:json.loads(P(p).read_text(encoding='utf-8'))
def write(p,obj):
 p=P(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,ensure_ascii=False,indent=2,sort_keys=False)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
def normalize(s):
 return re.sub(r'[^a-z0-9]+',' ',unicodedata.normalize('NFKD',str(s).lower()).encode('ascii','ignore').decode()).strip()
def words(s):return [x for x in normalize(s).split() if len(x)>2 and x not in STOP]
STOP=set('the and for this that with from are was were you your into their them they have has had when where after about while whose then than who how why can may will must not one all only same should without book chapter source claim author mechanism positive negative concept more own between what which under there been well important use uses using because example many each through some those these being during throughout its our its out any too also other into like rather does do did make making part within could over real said get gets getting take took taking much many always work works working'.split())

ap=argparse.ArgumentParser();ap.add_argument('--input',required=True);ap.add_argument('--out',required=True);ap.add_argument('--pdf',required=True);ap.add_argument('--archive-dir',required=True);a=ap.parse_args()
b=P(a.input);out=P(a.out);out.mkdir(parents=True,exist_ok=True)
assert sha(a.pdf)=='4dd7a311a21af58aa075176abb48fd60b348c70bb314a2ca09f66383922e7e9b'
packs=['p1','p2','p3','p4']
archive_names={'foundation':'PCI_FOUNDATION_v1(4).zip','p1':'PCI_RESEARCH_PART_01_CH01-04(4).zip','p2':'PCI_RESEARCH_PART_02_CH05-08(3).zip','p3':'PCI_RESEARCH_PART_03_CH09-12(2).zip','p4':'PCI_RESEARCH_PART_04_CH13-16(1).zip'}
archive_sums={k: {'original_filename':name,'sha256':sha(P(a.archive_dir)/name)} for k,name in archive_names.items()}
file_tags=['PCI_ANECDOTES','PCI_APPLICATIONS','PCI_AUTHOR_PRACTICES','PCI_CITATIONS','PCI_CLAIMS','PCI_CONCEPTS','PCI_EDUCATIONAL_EXERCISES','PCI_EVIDENCE_ASSESSMENTS','PCI_MECHANISMS','PCI_RELATIONSHIPS']
records={};origins={}; data_by_type={}
for tag in file_tags:
 merged=[]
 for pack in packs:
  filename=f'data/{tag}.json';rows=j(b/pack/filename)
  for r in rows:
   rid=r['id'];assert rid not in records,(rid,pack)
   records[rid]=r;origins[rid]={'stage':{'p1':'01','p2':'02','p3':'03','p4':'04'}[pack], 'package':archive_names[pack], 'package_sha256':archive_sums[pack]['sha256'], 'member':filename,'original_record_sha256':digest(r),'canonical_record_sha256':digest(r),'transformation':'none; original record retained byte-for-byte at JSON value level'}
  merged+=rows
 data_by_type[tag]=merged;write(out/'data'/f'{tag}.json',merged)
book=j(b/'foundation/PCI_BOOK.json');chapters=j(b/'p4/updates/PCI_CHAPTERS.json');coverage=j(b/'p4/updates/PCI_CHAPTER_COVERAGE.json');issues=j(b/'p4/updates/PCI_ISSUES.json')
sections=[]
for ch in chapters[:4]:sections+=ch['sections']
for pack,filename in [('p2','PCI_VERIFIED_SECTIONS_CH05-08.json'),('p3','PCI_VERIFIED_SECTIONS_CH09-12.json'),('p4','PCI_VERIFIED_SECTIONS_CH13-16.json')]: sections+=j(b/pack/filename)
for tag,rows,pack,member in [('book',[book],'foundation','PCI_BOOK.json'),('chapter',chapters,'p4','updates/PCI_CHAPTERS.json'),('section',sections,'mixed','sections'),('coverage',coverage,'p4','updates/PCI_CHAPTER_COVERAGE.json'),('issue',issues,'p4','updates/PCI_ISSUES.json')]:
 for r in rows:
  assert r['id'] not in records,r['id']
  records[r['id']]=r
  if tag=='section':
   if int(r['chapter_id'][-2:])<=4:p='foundation';mem='PCI_CHAPTERS.json (nested sections)'
   elif int(r['chapter_id'][-2:])<=8:p='p2';mem='PCI_VERIFIED_SECTIONS_CH05-08.json'
   elif int(r['chapter_id'][-2:])<=12:p='p3';mem='PCI_VERIFIED_SECTIONS_CH09-12.json'
   else:p='p4';mem='PCI_VERIFIED_SECTIONS_CH13-16.json'
  else:p=pack;mem=member
  origins[r['id']]={'stage':{'foundation':'01','p2':'02','p3':'03','p4':'04'}.get(p,'01'),'package':archive_names[p],'package_sha256':archive_sums[p]['sha256'],'member':mem,'original_record_sha256':digest(r),'canonical_record_sha256':digest(r),'transformation':'none; inherited original record'}
write(out/'data/PCI_BOOK.json',book);write(out/'data/PCI_CHAPTERS.json',chapters);write(out/'data/PCI_SECTIONS.json',sections);write(out/'data/PCI_CHAPTER_COVERAGE.json',coverage)
registry=j(b/'p4/updates/PCI_ID_REGISTRY.json')
assert set(registry)==set(records) and len(records)==1668

# Add issue records without mutating existing issue rows. These represent actual post-merge discovery.
issue_templates=[
 ('Cross-stage section representations differ','medium',None,11,'Section metadata mixes inline nested records, freeform label dictionaries, and section_id pointers. The canonical output preserves original chapters and supplies a normalized app section view; its normalization is not equivalent to fresh source verification.','Stage 06 consume normalized derived sections; Stage 05 keeps original source records.'),
 ('Chapter 5-12 subsection review statuses conflict with substantive coverage labels','high','PCI-CH-05',92,'Stage04 full-book coverage has sections_review_status NOT_REVIEWED_CANDIDATES for Chapters 05–12 despite substantive research dossiers. Subsection-boundary certainty and deep-coverage claims must not be conflated.','Recheck each titled subsection against PDF in Stage 07; preserve substantive dossier status with an explicit uncertainty.'),
 ('Source-page geometry cannot prove semantic claim accuracy','high','PCI-CH-01',13,'Earlier validators check page bounds and source IDs, not whether every source-based paraphrase is semantically exact. Stage05 manually checks a limited number of actual pages.','Perform targeted source-level audit for higher-stakes concepts; independently sample claims in Stage 07.'),
 ('Anecdotes and testimonials require external substantiation','high','PCI-CH-16',307,'Chapter16 experiences remain self-reported book narratives. They cannot be used as causal efficacy proof.','Mark testimonial provenance in every app presentation; retain external_not_assessed until reviewed.'),
 ('Aging, medical and recovery extrapolations require separate evidence review','high','PCI-CH-15',290,'Claims about aging, biological recovery, psychosomatic mechanisms, and longevity are not established by their presence in the PDF.','Prioritize independent systematic reviews and current medical guidance before writing prescriptive app copy.'),
 ('ESP claim and neuroimaging-review inference require separation','high','PCI-CH-02',45,'A 2026 review of ESP neuroimaging literature exists, but reviewing inconsistent studies is not proof that telepathy, precognition, or access to a universal mind is real.','Retain paranormal statements strictly as attributed book assertions and explicitly display an evidence caveat.'),
 ('External research references have incomplete bibliographic metadata','medium',None,11,'Stage01 has four URLs/DOIs whose destinations can be found, but the source records are provisional and do not consistently contain author list, date, or appraisal methodology.','Complete primary literature appraisal and contributor metadata before elevating evidence status.'),
 ('Original practices are distinct from optional PCI activities','high','PCI-CH-10',190,'The 70 book-practice records include contributor-attribution uncertainty and different durations; no standard 21-day schedule applies to all practices.','Stage06 use full-book practice index, preserve timing unknown and origin, and enforce opt-out/privacy protections.'),
]
issues_added=[];base=j(b/'p4/updates/PCI_ISSUES.json')[-1]
for n,(title,severity,ch,pg,detail,action) in enumerate(issue_templates,start=48):
 row=copy.deepcopy(base);rid=f'PCI-ISS-{n:03d}';row.update(id=rid,chapter_id=ch,title=title,content=detail,source_status='provisional',evidence_status='not_assessed',source_type='architectural_record',content_owner='PCI_editorial')
 row['revision']={'version':1,'schema_version':'1.0.0','recorded_at':'2026-11-20','change_note':'Stage05 additive issue record; inherited issues untouched'}
 row['source_refs']=([{'source_id':f'PCI-SRC-PDF-{pg:03d}','pdf_page':pg,'printed_page':pg-10,'edition_id':'PCI-ED-001','source_sha256':sha(a.pdf)}] if ch else [])
 row.update(severity=severity,status='open',description=detail,category='data_integrity_or_evidence',owner='PCI Stage06 / Stage07 QA',next_action=action,created_at='2026-11-20')
 if 'source_ref_id' in row:row['source_ref_id']=row['source_refs'][0]['source_id'] if row['source_refs'] else None
 issues_added.append(row);issues.append(row);records[rid]=row
 registry[rid]={'record_type':'issue','chapter_id':ch,'first_issued_stage':'05','immutable':True,'retired':False}
 origins[rid]={'stage':'05','package':'PCI_KNOWLEDGE_CANONICAL_v1.zip','member':'PCI_ISSUES.json','original_record_sha256':None,'canonical_record_sha256':digest(row),'transformation':'new additive Stage05 issue'}
write(out/'PCI_ISSUES.json',issues);write(out/'audits/PCI_STAGE05_NEW_ISSUES.json',issues_added)
write(out/'PCI_ID_REGISTRY.json',registry);write(out/'PCI_RECORD_PROVENANCE.json',origins)
write(out/'PCI_SOURCE_MANIFEST.json',j(b/'p4/updates/PCI_SOURCE_MANIFEST.json'))
write(out/'PCI_ORIGINAL_ARCHIVE_FINGERPRINTS.json',{'source_pdf':{'sha256':sha(a.pdf),'pdf_page_count':332,'redistributed_in_public_pack':False},'original_archives':archive_sums})
write(out/'PCI_FULL_BOOK_INGESTION_COVERAGE.json',j(b/'p4/PCI_FULL_BOOK_INGESTION_COVERAGE.json'))

# Normalize section view for application use; never flatten or change the original section records.
normalized=[]
for s in sections:
 refs=s.get('source_refs',[])
 normalized.append({'id':s['id'],'chapter_id':s['chapter_id'],'title':s['title'],'pdf_start':s.get('pdf_start_page',s.get('pdf_page',refs[0]['pdf_page'] if refs else None)),'pdf_end':s.get('pdf_end_page',s.get('pdf_start_page',s.get('pdf_page',refs[0]['pdf_page'] if refs else None))),'source_status':s.get('source_status','provisional'),'origin_id':s['id'],'original_record_sha256':digest(s)})
write(out/'indexes/PCI_SECTIONS_APP_VIEW.json',normalized)

# Derived themes do not replace chapter-specific records or count as source-supported causal assertions.
themes={
 'self_image':('self image self concept identity self esteem self acceptance self consistency internal narrative', ['self-image','identity','self-concept']),
 'goals_feedback':('goal target direction feedback steering servo guidance correction course mechanism', ['goal-setting','feedback','course correction']),
 'imagery_rehearsal':('imagination visualize picture rehearsal mental practice image imagining winning feeling', ['visualization','mental rehearsal','winning feeling']),
 'belief_reconstruction':('belief rational evidence inferiority thought dehypnotize truth false interpretation reassessment', ['beliefs','rational evaluation']),
 'relaxation_stress':('relaxation calm rest stress tension tranquilizer pressure worry crisis fear', ['relaxation','stress management']),
 'failure_response':('failure rejection mistakes setback self criticism negative feedback frustration', ['mistakes','setbacks']),
 'self_expression':('expression personality authenticity inhibition real self courage', ['personality','self-expression']),
 'interpersonal_wounds':('forgiveness scars resentment hostility interpersonal criticism conflict healing', ['emotional scars','relationships']),
 'habits_happiness':('habit happiness satisfaction joy emotions motivation optimism practice', ['habits','happiness']),
 'health_aging':('aging life years vitality longevity disease illness physical health placebo', ['aging','health']),
 'source_cases':('case anecdote testimonial success story biographical patient client', ['case study','testimony'])}
THEME_TERMS={k:set(words(q)) for k,(q,_) in themes.items()}
def tag_record(r):
 searchable=r.get('title','')+' '+r.get('content','')[:600]
 if r['type']=='concept':searchable+=' '+r.get('thesis','')+' '+ ' '.join(map(str,r.get('terms',[]) if isinstance(r.get('terms'),list) else []))
 toks=set(words(searchable))
 tag_scores={name:len(toks & keys) for name,keys in THEME_TERMS.items()}
 # Only conservative lexical matches; thematic tags are navigation heuristics, not source interpretation.
 tags=[k for k,v in sorted(tag_scores.items(),key=lambda x:(-x[1],x[0])) if v>=2][:5]
 return tags

search_docs=[];bychapter=collections.defaultdict(list);tagmap=collections.defaultdict(list);index_docs={}
for rid,r in sorted(records.items()):
 if r['type'] not in ('chapter','concept','claim','mechanism','author_practice','anecdote','application','exercise','citation','evidence_assessment','relationship','section'):continue
 chapter=r.get('chapter_id')
 alt=(r.get('terms') or []) if isinstance(r.get('terms'),list) else []
 if r['type']=='concept':
  alias=' '.join(map(str,alt))
 else: alias=''
 tags=tag_record(r)
 doc={'id':rid,'type':r['type'],'title':r.get('title',''),'chapter_id':chapter,'pdf_pages':sorted({x['pdf_page'] for x in r.get('source_refs',[]) if x.get('pdf_page')}),'source_status':r.get('source_status','provisional'),'evidence_status':r.get('evidence_status','not_assessed'),'themes':tags,'search_terms':normalize(r.get('title','')+' '+alias),'destination_id':rid,'preview':r.get('content','')[:220],'source_pack':origins[rid]['stage']}
 search_docs.append(doc);index_docs[rid]=doc
 if chapter:bychapter[chapter].append(rid)
 for t in tags:tagmap[t].append(rid)
write(out/'indexes/PCI_SEARCH_DOCUMENTS.json',search_docs)
post=collections.defaultdict(list)
for d in search_docs:
 r=records[d['id']];blob=' '.join([r.get('title',''),r.get('content','')[:350],r.get('thesis','')[:350],r.get('substantive_paraphrase','')[:300] if r['type']=='concept' else '', ' '.join(d['themes']), ' '.join(map(str,r.get('terms',[]))) if isinstance(r.get('terms'),list) else ''])
 for term in sorted(set(words(blob))):post[term].append(d['id'])
write(out/'indexes/PCI_SEARCH_INVERTED.json',{term:ids for term,ids in sorted(post.items()) if len(ids)<=1600})
write(out/'indexes/PCI_THEME_INDEX.json',{'definitions':{k:{'tags':syn,'description':q,'classification_method':'derived_lexical_assistance_not_scientific_evidence'} for k,(q,syn) in themes.items()},'record_ids':{k:v for k,v in tagmap.items()}})
write(out/'indexes/PCI_CHAPTER_TO_RECORDS.json',dict(bychapter))

# High-precision within-book index links, with declared editorial / source basis.
concepts=data_by_type['PCI_CONCEPTS']; practices=data_by_type['PCI_AUTHOR_PRACTICES'];claims=data_by_type['PCI_CLAIMS']; exercises=data_by_type['PCI_EDUCATIONAL_EXERCISES']; apps=data_by_type['PCI_APPLICATIONS'];examples=data_by_type['PCI_ANECDOTES']
def refs_pages(r):return {x.get('pdf_page') for x in r.get('source_refs',[])}
def tags_intersect(a,b):return sorted(set(index_docs[a['id']]['themes'])&set(index_docs[b['id']]['themes']))
cp=collections.defaultdict(list);pc=collections.defaultdict(list);pa=collections.defaultdict(list);ch_ex=collections.defaultdict(list)
for ex in exercises: ch_ex[ex['chapter_id']].append(ex['id'])
for app in apps:
 if app.get('concept_id') in records:pa[app['concept_id']].append({'id':app['id'],'basis':'explicit_concept_id'})
for pr in practices:
 pcands=[c for c in concepts if c['chapter_id']==pr['chapter_id']]
 ranked=[]
 for c in pcands:
  common=tags_intersect(pr,c)
  p1=refs_pages(pr);p2=refs_pages(c)
  mindist=min((abs(i-j) for i in p1 for j in p2),default=99)
  shared=len(set(words(pr['title']+' '+pr.get('content','')[:220]))&set(words(c['title']+' '+c.get('thesis','')[:180])))
  ranking=round(4/(1+mindist)+2*len(common)+1.5*min(shared,4),3)
  ranked.append((ranking,c,common,mindist,shared))
 for score,c,common,mindist,shared in sorted(ranked,key=lambda x:(-x[0],x[1]['id']))[:2]:
  if score<0.35:continue
  cp[c['id']].append({'practice_id':pr['id'],'basis':'same_chapter_plus_page_proximity_and_title_overlap','pdf_page_distance':mindist,'shared_topic_tags':common,'shared_title_terms':shared,'navigation_score_not_evidence':score,'interpretation_status':'editorial_navigation_heuristic_not_author_asserted'})
 claim_candidates=[]
 for cl in claims:
  if cl['chapter_id']!=pr['chapter_id']:continue
  mindist=min((abs(i-j) for i in refs_pages(pr) for j in refs_pages(cl)),default=99)
  shared=len(set(words(pr['title']))&set(words(cl['title'])))
  ranking=4/(1+mindist)+shared
  claim_candidates.append((ranking,cl,mindist,shared))
 for score,cl,mindist,shared in sorted(claim_candidates,key=lambda x:(-x[0],x[1]['id']))[:1]:
  pc[pr['id']].append({'claim_id':cl['id'],'basis':'same_chapter_best_source_page_proximity','pdf_page_distance':mindist,'title_term_overlap':shared,'navigation_score_not_evidence':round(score,3),'interpretation_status':'editorial_navigation_candidate_not_author_asserted'})
write(out/'indexes/PCI_CONCEPT_TO_PRACTICE.json',dict(cp))
write(out/'indexes/PCI_PRACTICE_TO_CLAIM.json',dict(pc))
write(out/'indexes/PCI_CONCEPT_TO_APPLICATION.json',dict(pa))
write(out/'indexes/PCI_CHAPTER_TO_EXERCISES.json',dict(ch_ex))
source_citation=collections.defaultdict(list)
for r in records.values():
 for ref in r.get('source_refs',[]):source_citation[ref['source_id']].append(r['id'])
write(out/'indexes/PCI_CITATION_TO_RECORDS.json',dict(source_citation))
scenario_candidates=j(b/'p3/PCI_SCENARIO_CANDIDATES_09-12.json')
quiz_candidates=j(b/'p3/PCI_COMPREHENSION_ITEMS_09-12.json')
for sc in scenario_candidates:assert sc['linked_concept_id'] in records and sc['source_ref']['source_id'] in records
write(out/'learning/PCI_SCENARIO_CANDIDATES_UNREGISTERED.json',scenario_candidates)
write(out/'learning/PCI_COMPREHENSION_CANDIDATES_UNREGISTERED.json',quiz_candidates)
write(out/'indexes/PCI_SCENARIO_TO_SOURCE.json',{x['candidate_key']:{'concept_id':x['linked_concept_id'],'citation_id':x['source_ref']['source_id'],'chapter_id':x['chapter_id'],'canonical_id_issued':False} for x in scenario_candidates})
practice_orig=j(b/'p4/PCI_FULL_BOOK_AUTHOR_PRACTICE_INDEX.json');assert len(practice_orig)==70
write(out/'data/PCI_AUTHOR_PRACTICE_ORIGIN_INDEX.json',practice_orig)

# Duplicate candidates are explicitly reviewed as distinct by source scope; no auto-merge.
review_pairs=[('PCI-C-CH01-004','PCI-C-CH05-008','overlapping_but_distinct','The early account frames self-consistency as a general identity filter; Chapter 5 develops conflicting convictions as a reasoning task.'),('PCI-C-CH01-008','PCI-C-CH05-009','overlapping_but_distinct','Both address goals, but the first concerns identity-dependent acceptance of targets and the later one goal-setting priorities.'),('PCI-C-CH02-005','PCI-C-CH11-002','overlapping_but_distinct','Chapter 2 advocates corrective feedback; Chapter 11 qualifies it with the danger of oversensitivity and inhibition.'),('PCI-C-CH01-007','PCI-C-CH03-011','overlapping_but_distinct','Realistic self-acceptance and spiritual/religious framing are adjacent but not identical arguments.'),('PCI-C-CH12-004','PCI-C-CH13-004','overlapping_but_distinct','Chapter12 emphasizes deliberate nonreaction; Chapter13 applies arousal to high-pressure performance.'),('PCI-C-CH01-002','PCI-C-CH09-004','overlapping_but_distinct','Snap-back loops and failed-expectation signals share explanatory vocabulary but different practical chapters.'),('PCI-C-CH08-005','PCI-C-CH11-002','overlapping_but_distinct','Chapter8 calls for truthful feedback without global shame while Chapter11 warns against excessive error monitoring.'),('PCI-C-CH01-001','PCI-C-CH10-004','overlapping_but_distinct','General self-image is a baseline, while putty/plaster discusses its revisability in emotional recovery.'),('PCI-C-CH02-005','PCI-C-CH08-005','overlapping_but_distinct','Goal correction is mechanistic metaphor; truthful negative feedback is an ethical/practical use case.'),('PCI-C-CH08-003','PCI-C-CH14-001','overlapping_but_distinct','Direction in a success profile and goal-guided winning feeling are separate pedagogical framings.'),('PCI-C-CH01-001','PCI-C-CH14-005','overlapping_but_distinct','A general self-description is distinct from confidence after a loss.'),('PCI-C-CH01-008','PCI-C-CH10-004','overlapping_but_distinct','Goals filtered by self-image and adaptable emotional image address different causal claims.'),('PCI-C-CH10-004','PCI-C-CH14-005','overlapping_but_distinct','Both involve changeable self-image but differ on interpersonal injury and performance persistence.')]
dup_review=[]
for u,v,cls,why in review_pairs:
 assert u in records and v in records
 dup_review.append({'a_id':u,'b_id':v,'classification':cls,'rationale':why,'a_source_refs':records[u].get('source_refs',[]),'b_source_refs':records[v].get('source_refs',[]),'source_status':'research_record_comparison_not_exhaustive_pdf_side_by_side','action':'retain_both_ids','redirect':None,'review_level':'editorial_comparison_of_inherited_dossiers'})
write(out/'audits/PCI_DUPLICATE_REVIEW.json',{'scope':'Cross-chapter concept pairs surfaced by title/thesis similarity plus editorial comparison','reviewed_pairs':dup_review,'confirmed_same_concept_merges':0,'merges_applied':0,'all_201_concepts_preserved':True,'limitations':'Candidate-based review cannot prove no remaining semantic duplicates.'})
write(out/'PCI_ID_REDIRECTS.json',{'schema_version':'1.0.0','redirects':{},'tombstones':{},'no_duplicate_id_retired':True,'policy':'Never delete; redirects require explicit audited same-concept decision and preserve original identifiers.'})

# Graph audit preserves the original 109 edges without inventing citations.
rel=data_by_type['PCI_RELATIONSHIPS'];ga=[]
for e in rel:
 supports=e.get('supporting_source_refs',[])
 pagesok=len(supports)>=2 and all(s['source_id'] in records for s in supports)
 hasends=e['from_id'] in records and e['to_id'] in records
 edge={'id':e['id'],'from_id':e['from_id'],'to_id':e['to_id'],'relationship_type':e['relationship_type'],'confidence':e.get('confidence'),'source_status':e.get('source_status'),'source_anchors':supports,'rationale':e.get('rationale',e.get('content')),'endpoints_resolve':hasends,'source_anchors_resolve':pagesok,'empirical_validation':'not_established_by_graph','original_record_sha256':origins[e['id']]['original_record_sha256']}
 ga.append(edge)
write(out/'graph/PCI_KNOWLEDGE_GRAPH.json',{'nodes':[{'id':c['id'],'chapter_id':c['chapter_id'],'title':c['title'],'themes':index_docs[c['id']]['themes']} for c in concepts],'edges':ga,'derived_editorial_edge_count':0,'limitations':'All edges preserve inherited research authoring; no decorative edges added.'})
write(out/'audits/PCI_GRAPH_QUALITY_AUDIT.json',{'total_edges':len(ga),'unresolved_edges':[g['id'] for g in ga if not g['endpoints_resolve'] or not g['source_anchors_resolve']],'types':dict(collections.Counter(g['relationship_type'] for g in ga)),'cross_chapter':sum(records[g['from_id']].get('chapter_id')!=records[g['to_id']].get('chapter_id') for g in ga),'conclusion':'Graph references validated structurally only. Semantic relationship interpretation remains reviewable.'})

# Derived full-book quality matrix differs from earlier subjective completion statuses.
book_cov=j(b/'p4/PCI_FULL_BOOK_INGESTION_COVERAGE.json')
reviewed=[]
for ch in book_cov['chapters']:
 n=int(ch['chapter_id'][-2:]);notes=[]
 if 5<=n<=12:notes.append('Prior coverage source says sections_review_status=NOT_REVIEWED_CANDIDATES; subsection precision not independently certified here.')
 if ch.get('uncertainty_notes'):notes+=ch['uncertainty_notes']
 reviewed.append({'chapter_id':ch['chapter_id'],'title':ch['chapter_title'],'pdf_start':ch['pdf_start'],'pdf_end':ch['pdf_end'],'index_state':'indexed','reported_prior_coverage_state':ch['coverage_state'],'dataset_has_substantive_dossiers':bool(ch['concept_records']),'source_page_reported_as_read_count':ch['pages_read_count'],'source_pages_total':ch['pdf_end']-ch['pdf_start']+1,'Stage05_external_science_review':'not_assessed_book_wide','Stage05_exhaustive_semantic_coverage':'not_certified','sections_analyzed_prior':ch['sections_analyzed'],'documented_gaps_and_uncertainties':notes})
write(out/'audits/PCI_FULL_BOOK_COVERAGE_TRUTH.json',{'chapters':reviewed,'count_chapters_indexed':16,'count_with_substantive_dossiers':16,'count_exhaustively_semantically_verified':0,'claim_count_independently_validated':0,'definition':'Substantive dossier presence != exhaustive passage analysis and != scientific corroboration.'})

# Make search examples deterministic and safe.
def query(text_,limit=8):
 toks=list(dict.fromkeys(words(text_)));scores=collections.Counter()
 for t in toks:
  for id in post.get(t,[]):scores[id]+=1
 return [{'id':rid,'score':score,'title':index_docs[rid]['title']} for rid,score in sorted(scores.items(),key=lambda x:(-x[1],x[0]))[:limit]]
queries=['self image beliefs','mental imagery rehearsal','feedback mistakes','emotional scars forgiveness','relaxation pressure','winning feeling','aging longevity','automatic success mechanism','rational thinking','crisis performance']
write(out/'tests/PCI_SEARCH_SMOKE_TEST_FIXTURES.json',[{'query':q,'results':query(q),'result_ids_resolve':all(r['id'] in records for r in query(q))} for q in queries])

# Copy original schemas and local privacy contracts; no replacement of canonical schema.
(out/'schema').mkdir(parents=True,exist_ok=True)
for filename in ['PCI_CANONICAL_RECORD.schema.json','PCI_PRIVATE_EXPORT.schema.json','PCI_STORAGE_MIGRATIONS.json','PCI_VOCABULARIES.json']:
 shutil.copy2(b/'foundation/schema'/filename,out/'schema'/filename)

manifest={'project':'PSYCHO-CYBERNETICS-INTELLIGENCE','stage':'05','schema_version':'1.0.0','research_data_version':'1.3.0','canonical_pack_version':'1.0.0','edition_id':'PCI-ED-001','primary_source_sha256':sha(a.pdf),'pdf_page_count':332,'inherited_registrations':1668,'new_issue_registrations':len(issues_added),'total_registrations':len(registry),'data_record_counts':{tag:len(items) for tag,items in data_by_type.items()},'complete_book_indexed_chapters':16,'chapters_with_substantive_dossiers':16,'exhaustive_semantic_review_certified':False,'external_empirical_validation':'partial_select_references_only','all_prior_records_preserved':True,'previous_ids_retained':True,'redirects':0,'public_build_pdf_included':False,'public_build_personal_data_included':False,'original_archives_sha256':archive_sums,'ten_modules_preserved':j(b/'p4/updates/PCI_PROJECT_MANIFEST.json')['modules'],'known_data_quality_gates':['subsection_completeness_uncertain','source_semantics_spot_checked_not_exhaustive','medical_paranormal_claims_are_not_proven','some_external_source_records_are_provisional']}
write(out/'PCI_PROJECT_MANIFEST.json',manifest)

# Basic app-ready interface templates; the source of truth is the v1 JSON schema and full documents.
TS='''/* PCI Stage05 types. Source statuses describe the text, never therapeutic efficacy. */
export type ClaimStatus = 'verified_in_pdf' | 'provisional' | 'not_located' | 'incomplete';
export type EvidenceStatus = 'book_assertion_only' | 'corroborated_external' | 'disputed' | 'not_assessed';
export type RelationshipType = 'supports'|'qualifies'|'contradicts'|'complements'|'requires'|'alternative_explanation'|'ethical_tension';
export type CoverageState = 'indexed'|'substantive'|'partial'|'unprocessed';
export type ExerciseOrigin = 'book'|'updated_edition_editor'|'PCI_adaptation'|'uncertain';
export type RecordType = 'book'|'chapter'|'section'|'coverage'|'issue'|'concept'|'claim'|'mechanism'|'author_practice'|'anecdote'|'evidence_assessment'|'application'|'exercise'|'citation'|'relationship';
export interface SourcePage { source_id: string; pdf_page: number; printed_page: number|null; edition_id: string; source_sha256: string; }
export interface CanonicalRecord { id:string; type: RecordType; chapter_id:string|null; title:string; content:string; source_type:string; source_status:ClaimStatus; evidence_status:EvidenceStatus; source_refs:SourcePage[]; content_owner:string; provenance: Record<string,unknown>; revision:Record<string,unknown>; [key:string]:unknown; }
export interface PCIConcept extends CanonicalRecord {type:'concept'; thesis:string; substantive_paraphrase:string; claim_ids?: string[]; case_ids?:string[]; practice_ids?:string[]; }
export interface PCIClaim extends CanonicalRecord {type:'claim'; concept_id?:string; empirical_proof_status?:string; }
export interface PCIAuthorPractice extends CanonicalRecord {type:'author_practice'; instructions:string[]; timing_as_printed_or_paraphrased:string; frequency_per_week?:number|null; program_days?:number|null; }
export interface PCIRelationship extends CanonicalRecord {type:'relationship';from_id:string;to_id:string;relationship_type:RelationshipType;supporting_source_refs:SourcePage[];rationale:string;}
export interface PCISearchDocument {id:string; type:RecordType; title:string; chapter_id:string|null; pdf_pages:number[];source_status:ClaimStatus;evidence_status:EvidenceStatus;themes:string[];search_terms:string;destination_id:string;preview:string;source_pack:string;}
export type PCITable<T extends CanonicalRecord = CanonicalRecord> = T[];
export interface PCIUserDataExport {format_version:string; exported_at:string; app_schema_version:string; private_entries:unknown[];}
/* Do not store private journals inside public canonical JSON. Persist private state in IndexedDB and encrypted/local versioned export. */
'''
(out/'types').mkdir(parents=True,exist_ok=True);(out/'types/PCI_KNOWLEDGE_TYPES.ts').write_text(TS)
TS2='''import type { PCISearchDocument } from './PCI_KNOWLEDGE_TYPES';
/* Deterministic local-only search; index is generated at build time, no network or AI dependencies. */
export function searchPCI(q:string, docs:PCISearchDocument[], inverted:Record<string,string[]>, limit=20):PCISearchDocument[] {
 const tokens=Array.from(new Set((q.toLowerCase().normalize('NFKD').replace(/[^a-z0-9]+/g,' ').trim().match(/[a-z0-9]+/g)||[]).filter(w=>w.length>2)));
 const counts=new Map<string,number>();
 for (const term of tokens) for (const id of (inverted[term]||[])) counts.set(id,(counts.get(id)||0)+1);
 const byID=new Map(docs.map(d=>[d.id,d] as const));
 return [...counts].sort((a,b)=>b[1]-a[1]||a[0].localeCompare(b[0])).slice(0,limit).map(([id])=>byID.get(id)).filter((x):x is PCISearchDocument=>Boolean(x));
}
'''
(out/'types/PCI_LOCAL_SEARCH.ts').write_text(TS2)
print(json.dumps({'inherited':1668,'new_issues':len(issues_added),'records':len(records),'all_registry':len(registry),'concepts':len(concepts),'graph_edges':len(rel),'search_documents':len(search_docs),'tokens':len(post),'coverage_chapters':len(book_cov['chapters']),'new_issues_ids':[x['id'] for x in issues_added]},indent=2))
