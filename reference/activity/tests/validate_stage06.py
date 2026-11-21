#!/usr/bin/env python3
"""PCI Stage 06 independent structural/content/reference/graph validator.
Requires jsonschema 4.x. Tests are data/logic validation, NOT clinical validation or browser testing.
"""
import argparse,json,re,hashlib,sys,collections,itertools,traceback,os
from pathlib import Path
from jsonschema import Draft202012Validator,FormatChecker
from run_content import activity_run,scenario_run

def load(p):return json.loads(Path(p).read_text(encoding='utf8'))
def main():
 args=argparse.ArgumentParser();args.add_argument('--root',default='.');args.add_argument('--canonical-dir',required=True);args.add_argument('--out');a=args.parse_args()
 r=Path(a.root);c=Path(a.canonical_dir);checks=[]
 def check(label,cond,detail=''):
  checks.append({'check':label,'status':'PASS' if cond else 'FAIL','detail':str(detail)[:900]});return cond
 dat={n:load(r/'data'/f'PCI_{n}.json') for n in ['EXECUTABLE_ACTIVITIES','BRANCHING_SCENARIOS','REHEARSAL_TEMPLATES','AUTHOR_PRACTICE_LOOKUP','FEEDBACK_PATTERNS','REVIEW_RUBRICS','FEEDBACK_CYCLES']}
 ac=dat['EXECUTABLE_ACTIVITIES'];sc=dat['BRANCHING_SCENARIOS'];rh=dat['REHEARSAL_TEMPLATES'];prac=dat['AUTHOR_PRACTICE_LOOKUP'];fb=dat['FEEDBACK_PATTERNS'];rub=dat['REVIEW_RUBRICS'];cyc=dat['FEEDBACK_CYCLES']
 orig=load(c/'PCI_ID_REGISTRY.json');reg=load(r/'PCI_ID_REGISTRY.json');man=load(r/'PCI_PROJECT_MANIFEST.json');issues=load(r/'PCI_ISSUES.json')
 con={x['id']:x for x in load(c/'data/PCI_CONCEPTS.json')};src={x['id']:x for x in load(c/'data/PCI_CITATIONS.json')};edu={x['id']:x for x in load(c/'data/PCI_EDUCATIONAL_EXERCISES.json')};authors={x['id']:x for x in load(c/'data/PCI_AUTHOR_PRACTICES.json')};ch={x['id']:x for x in load(c/'data/PCI_CHAPTERS.json')};cl={x['id']:x for x in load(c/'data/PCI_CLAIMS.json')}
 check('Canonical previous registry and IDs preserved verbatim',all(id in reg and reg[id]==v for id,v in orig.items()),f'{len(orig)} previous IDs')
 check('Exactly 32 activities and 2 per chapter',len(ac)==32 and all(sum(x['chapter_id']==id for x in ac)==2 for id in ch))
 check('16 multi-step scenarios',len(sc)==16 and all(sum(x['chapter_id']==id for x in sc)==1 for id in ch))
 check('At least 12 rehearsals',len(rh)>=12)
 check('Book practice preservation',len(prac)==len(authors)==70 and all(x['practice_id'] in authors for x in prac))
 all_objs=ac+sc+rh+fb+rub+cyc+issues[len(load(c/'PCI_ISSUES.json')):]
 ids=[x['id'] for x in all_objs]
 check('New IDs unique, in registry and not inherited',len(set(ids))==len(ids) and all(x not in orig and x in reg for x in ids),f'new {len(ids)}, registry delta {len(reg)-len(orig)}')
 check('Every new ID in registry actually represented',set(reg)-set(orig)==set(ids))
 check('No legacy research record mutated',all(x['adapted_from_educational_id'] in edu for x in ac) and all(orig[id]==reg[id] for id in orig))
 schema_match=[('ACTIVITY',ac),('SCENARIO',sc),('REHEARSAL',rh),('FEEDBACK',fb),('RUBRIC',rub)]
 for label,records in schema_match:
  schema=load(r/'schema'/f'PCI_{label}.schema.json');sv=Draft202012Validator(schema,format_checker=FormatChecker());errs=[]
  for record in records:
   for e in sv.iter_errors(record):errs.append(f"{record['id']}: {e.message}")
  check(f'{label} JSON Schema 2020-12 validation',not errs,errs[:3])
 for label,records,key in [('Activity',ac,'concept_ids'),('Scenario',sc,'linked_concept_ids'),('Rehearsal',rh,'linked_concept_ids')]:
  errs=[f"{x['id']}->{cid}" for x in records for cid in x[key] if cid not in con]
  check(f'{label} concept FK resolves',not errs,errs[:3])
  refs=[(x['id'],ref) for x in records for ref in x['source_refs']]
  errs=[f"{id}:{ref['source_id']}:{ref['pdf_page']}" for id,ref in refs if ref['source_id'] not in src or ref['pdf_page'] != src[ref['source_id']].get('pdf_page') or ref.get('source_sha256')!=man['book_pdf_sha256'] or not 1<=ref['pdf_page']<=332]
  check(f'{label} citation FKs and source page bounds',not errs,errs[:3])
 check('Chapter FK resolves for all content',all(x['chapter_id'] in ch for x in ac+sc+rh+prac))
 check('No author practice labeled an executable adaptation',all(x['origin']=='PCI_adaptation' and x['source_type']=='PCI_original_adaptation' and x['id'].startswith('PCI-ACT-') for x in ac) and all(x['source_type']=='author_practice' and x['original_record_unmodified'] for x in prac))
 check('Author practice timing and origin unchanged',all(x['timing_as_printed_or_paraphrased']==authors[x['practice_id']].get('timing_as_printed_or_paraphrased','duration_unknown') and x['frequency_per_week']==authors[x['practice_id']].get('frequency_per_week') and x['program_days']==authors[x['practice_id']].get('program_days') for x in prac))
 check('Each activity has transparent and non-diagnostic feedback',all(x['feedback_policy']['strategy']=='transparent_rule_based' and x['feedback_policy']['no_diagnosis'] is True and 'No automated' in x['feedback_policy']['free_text'] for x in ac))
 check('All activities have safe exit, no mandatory sensitive history',all(x['skip_target']=='SKIPPED' and x['safety']['stop_anytime'] is True and x['safety']['no_forced_disclosure'] is True for x in ac))
 err=[]
 for x in ac:
  steps={s['id']:s for s in x['steps']};cur=x['start_step_id'];seen=set()
  while cur not in x['terminal_states']:
   if cur not in steps or cur in seen:err.append(x['id']+':'+cur);break
   seen.add(cur);cur=steps[cur]['navigation']['next']
  fields={s['input']['field'] for s in steps.values()}
  if not set(x['completion_rule']['fields']).issubset(fields):err.append(x['id']+':completion_fields')
 check('Activity steps reachable with terminal completion and fields',not err,err[:3])
 fixtures=load(r/'tests/PCI_ACTIVITY_SMOKE_FIXTURES.json');res=[activity_run(next(x for x in ac if x['id']==v['target_id']),v['response']) for v in fixtures]
 check('32 activity completion simulations actually executed',len(res)==32 and all(x['status']=='completed' for x in res))
 skipres=[activity_run(x,{},skip_at_step='frame')['status']=='skipped' for x in ac]
 check('32 activity skip simulations actually executed',len(skipres)==32 and all(skipres))
 invalid=activity_run(ac[0],{'situation':''});check('Missing activity input causes incomplete not fabricated success',invalid['status']=='incomplete' and bool(invalid['missing']))
 decl=next(f for f in fixtures if f['target_id']==ac[0]['id']);ans=dict(decl['response'],observation_mode='declined');check('Explicit declined observation is skipped',activity_run(ac[0],ans)['status']=='skipped')
 graph_err=[];test_paths=0
 for s in sc:
  nodes={n['id']:n for n in s['nodes']}
  if len(nodes)!=len(s['nodes']) or s['start_node'] not in nodes or s['exit_node'] not in nodes:graph_err.append(s['id']+':duplicate/missing node');continue
  reachable={s['start_node']};stack=[s['start_node']]
  while stack:
   nid=stack.pop();node=nodes[nid]
   if node['type']=='decision':
    if len(node['choices'])<2:graph_err.append(s['id']+':single-choice')
    for choice in node['choices']:
     t=choice['target']
     if t not in nodes:graph_err.append(s['id']+':invalid '+t);continue
     if t not in reachable:reachable.add(t);stack.append(t)
   if node.get('skip_target') and node['skip_target'] not in nodes:graph_err.append(s['id']+':skip missing')
  if set(nodes)-reachable-{s['exit_node']}:graph_err.append(s['id']+':orphan decision/outcome')
  endings=[n for n in s['nodes'] if n['type']=='outcome']
  if len(endings)<2:graph_err.append(s['id']+':too few outcomes')
  for picks in itertools.product(range(2),repeat=2):
   result=scenario_run(s,picks);test_paths+=1
   if result['status']!='completed' or len(result['path'])!=3 or result['path'][-1] not in {n['id'] for n in endings}:
    graph_err.append(s['id']+':path '+str(picks))
  if scenario_run(s,[],skip_at_node=s['start_node'])['status']!='skipped':graph_err.append(s['id']+':no safe exit')
 check('Scenario graph, all states reachable, 2 decisions/path, 4 endings',not graph_err,f'{test_paths} actual paths; {graph_err[:3]}')
 check('All scenario outcomes explicitly hypothetical',all(n['outcome_kind']=='hypothetical' and 'not a prediction' in n['tradeoff'] for s in sc for n in s['nodes'] if n['type']=='outcome'))
 check('All scenarios include review and non-diagnostic framing',all(len(s['review_prompts'])>=2 and s['safety']['no_diagnostic_results'] and s['evaluation_policy']['no_inferred_internal_state'] for s in sc))
 check('All rehearsals support reduced time and no timer',all(x['timing']['reduced_seconds']<=x['timing']['full_seconds'] and x['timing']['no_timer_supported'] and x['timing']['full_seconds']<=1800 and x['timing']['reduced_seconds']>=0 for x in rh))
 check('Rehearsal duration equals all phase guidance',all(sum(p['suggested_seconds'] for p in x['phases'])==x['timing']['full_seconds']==x['timing']['phase_seconds_sum'] for x in rh))
 check('No rehearsal timing called a book prescription',all(x['timing']['book_duration_claimed'] is False for x in rh))
 check('Rehearsals allow stop, text mode and no imagery',all(x['safety']['may_stop_entirely'] and x['accessibility']['no_sensory_visualization_required'] and x['accessibility']['text_only'] for x in rh))
 chapindex=load(r/'indexes/PCI_CONTENT_BY_CHAPTER.json');conceptindex=load(r/'indexes/PCI_CONTENT_BY_CONCEPT.json')
 all_new={x['id'] for x in ac+sc+rh}
 check('Chapter index maps to real destinations',set(chapindex)==set(ch) and all(cid in all_new for row in chapindex.values() for arr in row.values() for cid in arr))
 check('Concept index maps to real sources and destinations',all(cid in con and x in all_new for cid,row in conceptindex.items() for arr in row.values() for x in arr))
 check('No PDF or personal journal included',not list(r.rglob('*.pdf')) and not list(r.rglob('journal*')))
 forbidden=[]
 for p in (r/'data').glob('*.json'):
  text=p.read_text().lower()
  for word in ['automated diagnosis','ai scored','guaranteed cure','guaranteed subconscious change']:
   if word in text:forbidden.append(p.name+':'+word)
 check('No forbidden efficacy/diagnostic promise strings',not forbidden,forbidden[:3])
 check('Future event JSON schema runnable',Draft202012Validator.check_schema(load(r/'schema/PCI_STORED_EVENT.schema.json')) is None)
 sample={'event_id':'EV-001','event_type':'activity.completed','target_id':ac[0]['id'],'timestamp_iso':'2026-11-20T12:00:00-08:00','schema_version':'1.0.0','privacy_mode':'device_local','data':{}}
 check('Future event sample validates',not list(Draft202012Validator(load(r/'schema/PCI_STORED_EVENT.schema.json'),format_checker=FormatChecker()).iter_errors(sample)))
 report={'status':'PASS' if all(x['status']=='PASS' for x in checks) else 'FAIL','passed':sum(x['status']=='PASS' for x in checks),'failed':sum(x['status']=='FAIL' for x in checks),'checks':checks,'count':{'activities':len(ac),'scenarios':len(sc),'rehearsals':len(rh),'author_practices_readonly':len(prac),'test_scenario_paths':test_paths,'new_ids':len(reg)-len(orig)},'test_classification':'structural/functional JSON and graph logic, not browser usability or scientific efficacy','command':'python tests/validate_stage06.py --root . --canonical-dir ../canonical --out audits/PCI_STAGE06_QA.json'}
 if a.out:Path(a.out).write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({'status':report['status'],'passed':report['passed'],'failed':report['failed'],'failed_checks':[x for x in checks if x['status']=='FAIL'],'count':report['count']},indent=2))
 return 0 if report['status']=='PASS' else 1
if __name__=='__main__':sys.exit(main())
