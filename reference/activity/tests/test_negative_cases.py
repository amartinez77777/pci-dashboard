"""Negative scenarios: expected rejected input is a passing test, NOT a run-time failure."""
import copy,json,sys
from pathlib import Path
from jsonschema import Draft202012Validator
from run_content import activity_run,scenario_run
p=Path(__file__).resolve().parent.parent
activities=json.load(open(p/'data/PCI_EXECUTABLE_ACTIVITIES.json'))
scenarios=json.load(open(p/'data/PCI_BRANCHING_SCENARIOS.json'))
rehearsals=json.load(open(p/'data/PCI_REHEARSAL_TEMPLATES.json'))
f=json.load(open(p/'tests/PCI_ACTIVITY_SMOKE_FIXTURES.json'))
checks=[]
def check(desc,condition):checks.append({'test':desc,'status':'PASS' if condition else 'FAIL'})
schema=json.load(open(p/'schema/PCI_ACTIVITY.schema.json'));sv=Draft202012Validator(schema)
mutated=copy.deepcopy(activities[0]);mutated.pop('steps')
check('Missing activity steps rejected by JSON Schema',bool(list(sv.iter_errors(mutated))))
mutated=copy.deepcopy(activities[0]);mutated['record_type']='clinical_diagnosis'
check('Falsely relabeled clinical activity rejected',bool(list(sv.iter_errors(mutated))))
ans=dict(f[0]['response']);ans['reasoning_choice']='not_a_real_choice'
check('Invalid activity choice rejected as incomplete',activity_run(activities[0],ans)['status']=='incomplete')
ans=dict(f[0]['response']);ans['situation']=''
check('Empty required input rejected',activity_run(activities[0],ans)['status']=='incomplete')
check('Skipping sensitive activity is possible without disclosure',activity_run(activities[19],{},skip_at_step='frame')['status']=='skipped')
ans=dict(f[0]['response']);ans['observation_mode']='declined'
check('Declined action does not count as successful completion',activity_run(activities[0],ans)['status']=='skipped')
try:scenario_run(scenarios[0],[55,0]);badchoice=False
except ValueError:badchoice=True
check('Out-of-range scenario option rejects',badchoice)
mut=copy.deepcopy(scenarios[0]);mut['nodes'][0]['choices'][0]['target']='MISSING_NODE'
try:scenario_run(mut,[0,0]);broken=False
except KeyError:broken=True
check('Missing graph endpoint does not silently resolve',broken)
mut=copy.deepcopy(scenarios[0]);mut['nodes'][0]['choices'][0]['target']='OPEN'
try:scenario_run(mut,[0]*30);cyclic=False
except ValueError:cyclic=True
check('Cyclic scenario does not claim completion',cyclic)
rs=json.load(open(p/'schema/PCI_REHEARSAL.schema.json'));mut=copy.deepcopy(rehearsals[0]);mut.pop('timing')
check('Missing rehearsal timing rejected by JSON Schema',bool(list(Draft202012Validator(rs).iter_errors(mut))))
result={'status':'PASS' if all(x['status']=='PASS' for x in checks) else 'FAIL','checks':checks,'passed':sum(x['status']=='PASS' for x in checks),'failed':sum(x['status']=='FAIL' for x in checks)}
(p/'audits/PCI_NEGATIVE_TESTS.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2));sys.exit(result['failed']>0)
