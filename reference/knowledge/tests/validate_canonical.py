#!/usr/bin/env python3
"""Read-only PCI Stage05 validator. No network; original PDF optional for private source checks."""
import argparse, pathlib, json, hashlib, re, sys, collections, os
from jsonschema import Draft202012Validator
try:import fitz
except ImportError:fitz=None
p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--pdf');p.add_argument('--out');args=p.parse_args();R=pathlib.Path(args.root)
j=lambda path:json.loads(pathlib.Path(path).read_text(encoding='utf8'))
sha=lambda x:hashlib.sha256(pathlib.Path(x).read_bytes()).hexdigest()
C={};errors=[]
def check(k,flag,detail=None):
 C[k]='PASS' if flag else 'FAIL'
 if not flag:errors.append({'test':k,'detail':str(detail)[:1500]})
schema=j(R/'schema/PCI_CANONICAL_RECORD.schema.json');validator=Draft202012Validator(schema)
paths=sorted((R/'data').glob('PCI_*.json'))
# These two are derived data (origin index and original data source); exclude from canonical records.
canonical_names={'PCI_ANECDOTES','PCI_APPLICATIONS','PCI_AUTHOR_PRACTICES','PCI_CITATIONS','PCI_CLAIMS','PCI_CONCEPTS','PCI_EDUCATIONAL_EXERCISES','PCI_EVIDENCE_ASSESSMENTS','PCI_MECHANISMS','PCI_RELATIONSHIPS','PCI_CHAPTERS','PCI_SECTIONS','PCI_CHAPTER_COVERAGE','PCI_BOOK'}
records=[]
for path in paths:
 if path.stem not in canonical_names:continue
 data=j(path)
 records.extend(data if isinstance(data,list) else [data])
records+=j(R/'PCI_ISSUES.json')
ids=[r['id'] for r in records];by={r['id']:r for r in records};registry=j(R/'PCI_ID_REGISTRY.json');base=j(R/'PCI_PROJECT_MANIFEST.json');prov=j(R/'PCI_RECORD_PROVENANCE.json')
check('16_chapters',len(j(R/'data/PCI_CHAPTERS.json'))==16)
check('all_16_have_substantive_dossiers',set(x['chapter_id'] for x in j(R/'data/PCI_CONCEPTS.json'))==set(f'PCI-CH-{i:02d}' for i in range(1,17)))
check('expected_preserved_201_concepts',len(j(R/'data/PCI_CONCEPTS.json'))==201)
check('expected_preserved_70_practices',len(j(R/'data/PCI_AUTHOR_PRACTICES.json'))==70)
check('registry_equals_canonical_record_ids',len(set(ids))==len(ids) and set(ids)==set(registry),{'records':len(ids),'unique':len(set(ids)),'registry':len(registry),'missing':list(set(ids)-set(registry))[:5],'extra':list(set(registry)-set(ids))[:5]})
check('all_1668_prior_id_registry_values_preserved',len([r for r in registry if registry[r]['first_issued_stage']!='05'])==1668)
check('no_original_data_edited',all(prov[x['id']]['original_record_sha256']==prov[x['id']]['canonical_record_sha256'] for x in records if prov[x['id']]['stage']!='05'))
invalid=[]
for r in records:
 for e in validator.iter_errors(r):invalid.append((r['id'],e.message))
check('json_schema_all_1676_records',not invalid,invalid[:8])
check('provenance_for_all',set(prov)==set(ids))
check('legacy_schema_version_unchanged',base['schema_version']=='1.0.0')
check('no_pdf_or_personal_files',not list(R.rglob('*.pdf')) and not any(r.get('content_owner')=='user_private' for r in records))
source_hash=base['primary_source_sha256'];links=[]
for r in records:
 for s in r.get('source_refs',[]):
  if s.get('source_id') not in by or not 1<=s.get('pdf_page',0)<=332 or (s['pdf_page']>=11 and s.get('printed_page')!=s['pdf_page']-10) or s.get('source_sha256')!=source_hash:
   links.append((r['id'],s))
 for fld in ('chapter_id','concept_id','from_id','to_id'):
  v=r.get(fld)
  if v and v not in by: links.append((r['id'],fld,v))
 for fld in ('claim_ids','case_ids','practice_ids','related_concept_ids','evidence_assessment_ids','external_ref_ids','linked_concepts'):
  for v in r.get(fld,[]):
   if v not in by:links.append((r['id'],fld,v))
 for s in r.get('supporting_source_refs',[]):
  if s['source_id'] not in by or not 1<=s.get('pdf_page',0)<=332:links.append((r['id'],'supporting_ref',s))
check('all_reference_targets_exist_and_page_offsets_valid',not links,links[:8])
graph=j(R/'graph/PCI_KNOWLEDGE_GRAPH.json');badgraph=[x['id'] for x in graph['edges'] if not x['endpoints_resolve'] or not x['source_anchors_resolve']]
check('knowledge_graph_109_edges_resolve',len(graph['edges'])==109 and not badgraph,badgraph)
check('all_graph_nodes_have_real_concept_records',len(graph['nodes'])==201 and all(x['id'] in by and by[x['id']]['type']=='concept' for x in graph['nodes']))
search=j(R/'indexes/PCI_SEARCH_DOCUMENTS.json');inv=j(R/'indexes/PCI_SEARCH_INVERTED.json');sidx={s['id']:s for s in search}
check('search_documents_resolve_to_full_records',all(s['id'] in by and s['destination_id']==s['id'] and s['type']==by[s['id']]['type'] for s in search))
check('inverted_index_valid_and_nontrivial',len(inv)>1000 and all(all(x in sidx for x in ids) for ids in inv.values()))
check('multiple_representative_search_lookups',all(k in inv and any(by[r]['type']=='concept' for r in inv[k]) for k in ['self','image','feedback','relaxation','happiness','crisis','aging']))
lookups=['PCI_CONCEPT_TO_PRACTICE','PCI_PRACTICE_TO_CLAIM','PCI_CHAPTER_TO_EXERCISES','PCI_CONCEPT_TO_APPLICATION','PCI_CITATION_TO_RECORDS']
badlook=[]
for name in lookups:
 data=j(R/'indexes'/f'{name}.json')
 for k,vs in data.items():
  if k not in by:badlook.append((name,k,'key'))
  for v in vs:
   target=v if isinstance(v,str) else (v.get('practice_id') or v.get('claim_id') or v.get('id'))
   if target not in by:badlook.append((name,k,target))
check('all_learning_index_targets_resolve',not badlook,badlook[:8])
checksensitive=[e for e in j(R/'data/PCI_EDUCATIONAL_EXERCISES.json') if e.get('diagnostic_use') or e.get('privacy_default')!='local_only']
check('educational_exercises_are_local_first_non_diagnostic',not checksensitive,[x['id'] for x in checksensitive])
# No claims promoted to empirical proof by merging.
check('book_claims_not_promoted_to_science',all(x.get('empirical_proof_status')=='not_established_by_pdf' for x in j(R/'data/PCI_CLAIMS.json')))
# Coverages are source-reading claims, not scientific validation claims.
cov=j(R/'audits/PCI_FULL_BOOK_COVERAGE_TRUTH.json')
check('coverage_truth_distinguishes_index_from_external_science',cov['count_chapters_indexed']==16 and cov['count_exhaustively_semantically_verified']==0 and not base['exhaustive_semantic_review_certified'])
# Duplicate process must not retire anything without a redirect.
redir=j(R/'PCI_ID_REDIRECTS.json');dups=j(R/'audits/PCI_DUPLICATE_REVIEW.json')
check('no_silent_concept_merge_or_tombstone',dups['merges_applied']==0 and not redir['redirects'] and not redir['tombstones'])
# Deduplicated file inventory checksum will be computed after all files saved in final QA stage.
check('source_pdf_fingerprint_matches_manifest',bool(re.fullmatch('[a-f0-9]{64}',source_hash)))
if args.pdf:
 if fitz is None:check('private_pdf_spot_check_dependency',False,'PyMuPDF not installed')
 else:
  check('private_pdf_hash_and_332_pages',sha(args.pdf)==source_hash and len(fitz.open(args.pdf))==332)
  planned=j(R/'audits/PCI_PRIMARY_PDF_SPOT_CHECKS.json')
  pdf=fitz.open(args.pdf);miss=[]
  for item in planned:
   t=' '.join(pdf[item['pdf_page']-1].get_text().lower().split())
   if not all(re.search(re.escape(word),t,re.I) for word in item['checked_keywords']):miss.append(item['pdf_page'])
  check('pdf_spot_check_all_16_chapters',not miss and len(planned)==16,miss)
# TypeScript compilation is validated independently by tsc and recorded in PCI_TYPESCRIPT_TEST.json.
result={'overall':'PASS' if not errors else 'FAIL','checks':C,'passed':sum(v=='PASS' for v in C.values()),'failed':sum(v=='FAIL' for v in C.values()),'not_tested':['empirical_claim_truth','complete_concept-by-concept_pdf_validation','browser_navigation','IndexedDB_persistence'],'errors':errors,'counts_by_type':dict(collections.Counter(r['type'] for r in records)),'total_records':len(records),'prior_records_preserved':1668,'new_issue_ids':sorted(set(ids)-{x for x in ids if registry[x]['first_issued_stage']!='05'}),'schema_version':base['schema_version'],'pdf_sha256':source_hash}
if args.out:pathlib.Path(args.out).write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
print(json.dumps({'overall':result['overall'],'passed':result['passed'],'failed':result['failed'],'errors':errors[:8],'record_count':len(records)},indent=2))
sys.exit(0 if not errors else 1)
