"""Deterministic Stage12 source/contract audit, runnable without production browser.
Only structural checks; not empirical evidence or native IndexedDB durability.
"""
from pathlib import Path
import json,re,hashlib,zipfile,sys
ROOT=Path(__file__).resolve().parents[1];AUDIT=ROOT/'audit'/'stage12';AUDIT.mkdir(parents=True,exist_ok=True)
checks=[]
def ck(label,yes,detail=''):
 checks.append({'check':label,'status':'PASS' if yes else 'FAIL','detail':str(detail)[:250]})
 if not yes:print('FAIL:',label,detail)

# Final release: one deliberately authorized storage.ts safety repair. The original
# and repaired bytes must match the exact hashes in the signed-off change record.
control=json.loads((ROOT/'audit/final/STORAGE_CHANGE_CONTROL.json').read_text())
def approved_storage():
 return (control['path']=='src/storage.ts' and
  hashlib.sha256((ROOT/'src/storage.ts').read_bytes()).hexdigest()==control['after_hardening_sha256'] and
  control['before_checkpoint4_sha256']=='7d59ab136285f9fdde14d4c85c82b866f4b7da1b1b6c39a70ef4e8fd679b4be5')

def load(path):return json.loads((ROOT/path).read_text())
with zipfile.ZipFile(ROOT/'rollbacks/PCI_APP_STAGE11_FULL.zip') as z:
 prior={n.removeprefix('PCI_APP_STAGE11_FULL/'):z.read(n) for n in z.namelist() if n.startswith('PCI_APP_STAGE11_FULL/') and not n.endswith('/')}
orig=json.loads(prior['PCI_ID_REGISTRY.json']);reg=load('PCI_ID_REGISTRY.json')
ck('all '+str(len(orig))+' original stable IDs and metadata preserved',all(reg.get(k)==v for k,v in orig.items()) and len(orig)==1781)
new=set(reg)-set(orig);wanted={f'PCI-ISS-ST12-{i:03d}' for i in range(1,5)}
ck('Stage12 issue IDs and exact additive CP2/CP3 content IDs only',new==wanted|{f'PCI-COND-{i:03d}' for i in range(1,7)}|{'PCI-ACA-Q01','PCI-ACA-Q02','PCI-ACA-Q03','PCI-ACA-Q04','PCI-ACA-Q05','PCI-ACA-Q06','PCI-ACA-Q09','PCI-ACA-Q16'},new)
issues=load('PCI_ISSUES.json');ck('new issue records and audit aliases recorded',all(any(x['id']==id and x.get('provenance',{}).get('independent_audit_alias') for x in issues) for id in wanted))
ck('all four Stage12 issues retained with verified repairs in checkpoint',all(next(x for x in issues if x['id']==f'PCI-ISS-ST12-{i:03d}')['status']=='resolved' for i in range(1,5)) and all(next(x for x in issues if x['id']==f'PCI-ISS-ST12-{i:03d}')['owner_stage']==('Stage 12' if i<=2 else 'Final Prompt 1 / Foundation Rescue') for i in range(1,5)))
changed=[n for n in prior if n.startswith(('public/data/','reference/','src/storage.ts','src/types.ts')) and ((ROOT/n).read_bytes()!=prior[n] if (ROOT/n).exists() else True)]
ck('all public research and type contracts byte-identical, storage only approved safety edit',set(changed).issubset({'src/storage.ts'}) and approved_storage() and hashlib.sha256(prior['src/storage.ts']).hexdigest()==control['before_checkpoint4_sha256'],changed[:10])
chk=['command-center','self-image','beliefs','theater','feedback','conditioning','scenarios','knowledge','academy','archive'];app=(ROOT/'src/app.tsx').read_text()
ck('all 10 route definitions preserved',all(f"slug:'{x}'" in app for x in chk))
ck('Feedback and Scenario modules rendered instead of placeholders',"slug==='feedback'?<FeedbackLab" in app and "slug==='scenarios'?<ScenarioSimulator" in app)
ck('Theater scene context resolves by UUID into private store',"getRecord('rehearsals'" in (ROOT/'src/theater.tsx').read_text() and "phaseVisibleContent(" in (ROOT/'src/theater.tsx').read_text())
ck('original generic text-only guidance no longer defaults on', 'textMode,setTextMode]=React.useState(false)' in (ROOT/'src/theater.tsx').read_text())
ck('new stores NOT invented',"DB_VERSION=2" in (ROOT/'src/storage.ts').read_text() and len(re.findall(r"'[_a-z]+'",(ROOT/'src/storage.ts').read_text().split('export const STORES:StoreName[]=')[1].split('];')[0]))==25)
ck('feedback uses private v2 stores and separately stored predictions',"newRecord('predicted_outcomes'" in (ROOT/'src/feedback-repo.ts').read_text() and "newRecord('observed_outcomes'" in (ROOT/'src/feedback-repo.ts').read_text())
ck('scenario uses existing scenario_progress and minimal events',"newRecord('scenario_progress'" in (ROOT/'src/scenario-repo.ts').read_text() and "scenario.completed" in (ROOT/'src/scenario-repo.ts').read_text())
idx={r['id'] for r in load('public/data/concept-index.json')}
counts=[]
for j in range(1,17):
 p=f'public/data/scenarios/{j:02d}.json';rows=load(p);counts.extend(rows)
 for s in rows:
  nodes={n['id']:n for n in s['nodes']};edges=[c['target'] for n in s['nodes'] for c in n.get('choices',[])]
  ck('scenario '+s['id']+' valid targets, source, 2+ decisions',s['start_node'] in nodes and all(t in nodes for t in edges) and sum(n['type']=='decision' for n in s['nodes'])>=2 and all(c in idx for c in s['linked_concept_ids']) and all(1<=a['pdf_page']<=332 for a in s['source_refs']))
ck('16 original scenario IDs preserved',len(counts)==16 and len({x['id'] for x in counts})==16)
ck('201 concepts, 12 rehearsals, 70 source practices preserved',len(idx)==201 and len(load('public/data/rehearsals.json'))==12 and len(load('public/data/practice-attribution.json'))==70)
ck('no book PDF or personal fixtures in public',not list((ROOT/'public').rglob('*.pdf')) and not list((ROOT/'public').rglob('user*')))
ck('no raw public collection of user authored scenes or goals',not any('personal' in p.name.lower() or 'private' in p.name.lower() for p in (ROOT/'public/data').rglob('*.json')))
try:
 from jsonschema import Draft202012Validator
 for p in sorted((ROOT/'schema').glob('PCI_STAGE12_*.schema.json')):
  Draft202012Validator.check_schema(json.loads(p.read_text()));ck('valid JSON Schema '+p.name,True)
except Exception as e:ck('JSON Schema validity',False,str(e))
ck('TypeScript implementation and executable new tests present',all((ROOT/p).is_file() and (ROOT/p).stat().st_size>200 for p in ['src/feedback.tsx','src/scenarios.tsx','src/theater-guidance.ts','tests/stage12_model_repo.test.mjs','tests/browser_stage12_smoke.py']))
report={'stage':'12','status':'PASS' if all(x['status']=='PASS' for x in checks) else 'FAIL','passed':sum(x['status']=='PASS' for x in checks),'failed':sum(x['status']=='FAIL' for x in checks),'checks':checks,'limitation':'Structural audit only, not source empirical verification or native browser persistence'}
(AUDIT/'PCI_STAGE12_ASSET_QA.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'status':report['status'],'passed':report['passed'],'failed':report['failed']},indent=2))
if report['failed']:sys.exit(1)
