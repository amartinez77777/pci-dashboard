#!/usr/bin/env python3
"""Reproducible schema, continuity, coverage and referential-integrity checks."""
import json, pathlib, argparse, collections, hashlib, re, sys
from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource
p=argparse.ArgumentParser();p.add_argument('--root',default='.');p.add_argument('--canonical-dir',required=True);p.add_argument('--activity-dir',required=True);p.add_argument('--out');args=p.parse_args()
R=pathlib.Path(args.root);C=pathlib.Path(args.canonical_dir);A=pathlib.Path(args.activity_dir)
def load(x):return json.loads(x.read_text(encoding='utf-8'))
checks=[]
def check(n,good,detail=''):
 checks.append({'name':n,'status':'PASS' if good else 'FAIL','detail':str(detail)[:600]})
reg=load(R/'PCI_ID_REGISTRY.json');creg=load(C/'PCI_ID_REGISTRY.json');areg=load(A/'PCI_ID_REGISTRY.json');man=load(R/'PCI_PROJECT_MANIFEST.json');days=load(R/'data/PCI_21_DAY_CURRICULUM.json');catalog=load(R/'data/PCI_RECOMMENDATION_CATALOG.json');modules=load(R/'data/PCI_MODULE_EVENT_MAP.json');seeds=load(R/'data/PCI_REVIEW_SEEDS.json');acts=load(A/'data/PCI_EXECUTABLE_ACTIVITIES.json');sc=load(A/'data/PCI_BRANCHING_SCENARIOS.json');rh=load(A/'data/PCI_REHEARSAL_TEMPLATES.json')
activity={x['id']:x for x in acts};scenario={x['id']:x for x in sc};rehearsal={x['id']:x for x in rh};concept={x['id']:x for x in load(C/'data/PCI_CONCEPTS.json')};srcset=set(x['id'] for x in load(C/'data/PCI_CITATIONS.json'))
check('canonical IDs unchanged',all(k in reg and reg[k]==v for k,v in creg.items()),f'{len(creg)} IDs')
check('stage06 IDs unchanged',all(k in reg and reg[k]==v for k,v in areg.items()),f'{len(areg)} IDs')
new=set(reg)-set(areg);check('22 declared new IDs',len(new)==22 and 'PCI-PROG-021' in new, sorted(new))
check('registry unique & stable',len(reg)==len(set(reg)) and len(reg)==1769)
check('source PDF fingerprint inherited',man['original_source_sha256']==load(C/'PCI_PROJECT_MANIFEST.json')['primary_source_sha256'])
check('curriculum length and order',len(days['days'])==21 and [x['day_number'] for x in days['days']]==list(range(1,22)))
check('unique curriculum IDs',len({x['id'] for x in days['days']})==21 and all(x['id'] in reg for x in days['days']))
check('source activity foreign keys',all(d['primary_activity_id'] in activity for d in days['days']))
check('concept ID references',all(d['verified_concept_ids'] and all(i in concept and i in reg for i in d['verified_concept_ids']) for d in days['days']))
check('source references resolve',all(d['source_refs'] and all(s['source_id'] in srcset for s in d['source_refs']) for d in days['days']))
check('rehearsal/scenario optional refs',all((d['optional_rehearsal_id'] is None or d['optional_rehearsal_id'] in rehearsal) and (d['optional_scenario_id'] is None or d['optional_scenario_id'] in scenario) for d in days['days']))
check('author origin separated',all(d['origin']=='PCI_adaptation' and d['program_is_book_mandate'] is False for d in days['days']))
check('distinct daily instructional content',len({d['daily_task'] for d in days['days']})==21 and len({d['reflection_prompt'] for d in days['days']})==21 and len({d['optional_real_world_experiment']['description'] for d in days['days']})==21)
check('short and safe alternatives',all(d['short_session']['completion_equivalent'] and d['short_session']['estimated_minutes']<=5 and len(d['safe_options'])>=3 for d in days['days']))
check('at least 4 checkpoints',sum(x['checkpoint'] is not None for x in days['days'])>=4)
check('checkpoint revision/stop',all(x['checkpoint']['allow_goal_revision'] and x['checkpoint']['allow_rest'] for x in days['days'] if x['checkpoint']))
check('10 modules represented',len(set(x['module'] for x in days['days']))==10 and set(modules['event_to_modules'][k][0] for k in [])==set())
check('module mapping complete',len(modules['modules'])==10 and all(m['consumes_event_types'] for m in modules['modules']))
check('source status explicit',all(d['source_status'] in ['provisional','verified_in_pdf','incomplete','not_located'] for d in days['days']))
check('no journal supplied',not list((R/'data').glob('*USER*')) and 'profile' not in man)
check('catalog total 60',len(catalog['items'])==60)
check('catalog unique IDs',len({x['id'] for x in catalog['items']})==60)
check('catalog targets resolve',all(x['id'] in areg for x in catalog['items']))
check('catalog source IDs',all(x['concept_ids'] and all(id in concept for id in x['concept_ids']) for x in catalog['items']))
check('201 concept review seeds',len(seeds)==201 and all(x['id'] in concept for x in seeds))
check('event mapping known types',all(v and all(m in [x['name'] for x in modules['modules']] for m in v) for v in modules['event_to_modules'].values()))
check('one true issue set unchanged',len(load(R/'PCI_ISSUES.json'))==len(load(A/'PCI_ISSUES.json')))
check('no source PDF in data pack',not list(R.rglob('*.pdf')))
# JSON schemas and synthetic checks
sch=load(R/'schema/PCI_PRIVATE_RECORD_v2.schema.json');exp=load(R/'schema/PCI_PRIVATE_EXPORT_v2.schema.json');ev=load(R/'schema/PCI_EVENT_v2.schema.json')
for name,s in [('record',sch),('export',exp),('event',ev)]:
 try:Draft202012Validator.check_schema(s);good=True
 except Exception as e:good=False
 check('schema meta-valid '+name,good)
uuid='11111111-2222-4333-8444-555555555555';consent='11111111-2222-4333-8444-666666666666';created='2026-11-20T10:00:00-08:00'
r={'id':uuid,'store':'goals','created_at':created,'updated_at':created,'owner':'user','privacy_mode':'device_local','schema_version':'2.0.0','data':{'title':'SYNTHETIC FICTIONAL goal','status':'active','priority':2},'refs':['PCI-C-CH01-001'],'sensitive':False}
val=Draft202012Validator(sch,format_checker=FormatChecker());check('synthetic private record valid',not list(val.iter_errors(r)))
invalid={**r,'sensitive':True};check('sensitive consent enforced',bool(list(val.iter_errors(invalid))))
invalid={**r,'data':{'status':'active'}};check('required goal title enforced',bool(list(val.iter_errors(invalid))))
event={'event_id':uuid,'idempotency_key':'test-session-001','event_type':'activity.completed','target_id':'PCI-ACT-CH01-001','timestamp_iso':created,'time_zone':'America/Los_Angeles','session_id':'synthetic-session','schema_version':'2.0.0','privacy_mode':'device_local','payload':{}}
check('synthetic event valid',not list(Draft202012Validator(ev,format_checker=FormatChecker()).iter_errors(event)))
check('invalid event type rejected',bool(list(Draft202012Validator(ev,format_checker=FormatChecker()).iter_errors({**event,'event_type':'personality.inferred'}))))
backup={'format':'PCI_PRIVATE_EXPORT','version':2,'created_at':created,'schema_version':'2.0.0','source_app':'PSYCHO-CYBERNETICS-INTELLIGENCE','metadata':{'time_zone':'America/Los_Angeles','included_stores':['goals'],'sensitive_data_warning':'Unencrypted unless user explicitly encrypts the file','export_mode':'selected_stores'},'records':{'goals':[r]},'checksum_sha256':None}
registry_ref=Registry().with_resource('PCI_PRIVATE_RECORD_v2.schema.json',Resource.from_contents(sch))
check('synthetic export valid',not list(Draft202012Validator(exp,registry=registry_ref,format_checker=FormatChecker()).iter_errors(backup)))
check('future export version rejected',bool(list(Draft202012Validator(exp,registry=registry_ref,format_checker=FormatChecker()).iter_errors({**backup,'version':3}))))
check('privacy schema keeps all six legacy stores',all(s in load(R/'schema/PCI_INDEXEDDB_CONTRACT.json')['legacy_stores_preserved'] for s in ['journal_entries','identity_notes','belief_tests','rehearsals','goal_metrics','quiz_attempts']))
check('no content user profile seeded',not (R/'data/PCI_USER_PROFILE.json').exists())
check('all modules get published ids',all(d['primary_activity_id'] in areg for d in days['days']))
status='PASS' if all(c['status']=='PASS' for c in checks) else 'FAIL'
report={'status':status,'passed':sum(c['status']=='PASS' for c in checks),'failed':sum(c['status']=='FAIL' for c in checks),'checks':checks,'counts':{'new_program_ids':len(new),'21_day_records':len(days['days']),'catalog_items':len(catalog['items']),'private_stores':len(load(R/'schema/PCI_INDEXEDDB_CONTRACT.json')['private_stores']),'review_seeds':len(seeds)}}
if args.out:pathlib.Path(args.out).write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='checks'},indent=2));
for c in checks:
 if c['status']=='FAIL':print('FAIL',c)
sys.exit(0 if status=='PASS' else 1)
