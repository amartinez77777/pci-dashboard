"""Lean Checkpoint 1 data preservation and repair assertions; no browser claims."""
import json,hashlib,re
from pathlib import Path
root=Path(__file__).resolve().parents[1]
checks=[]
def ck(name,condition):
 checks.append({'name':name,'status':'PASS' if condition else 'FAIL'})
 if not condition:print('FAIL',name)
records=json.loads((root/'PCI_ID_REGISTRY.json').read_text())
ck('all inherited 1785 IDs, six conditioning IDs and eight Academy quiz IDs retained',len(records)==1799 and all(f'PCI-COND-{i:03d}' in records for i in range(1,7)) and all(x in records for x in ['PCI-ACA-Q01','PCI-ACA-Q02','PCI-ACA-Q03','PCI-ACA-Q04','PCI-ACA-Q05','PCI-ACA-Q06','PCI-ACA-Q09','PCI-ACA-Q16']))
issues=json.loads((root/'PCI_ISSUES.json').read_text())
for i in [3,4]:
 r=next((x for x in issues if x.get('id')==f'PCI-ISS-ST12-{i:03d}'),None)
 ck(f'issue PCI-ISS-ST12-{i:03d} repaired with documented verification',bool(r and r['status']=='resolved' and r['repair'] and r['verification_method']))
immutable=json.loads((root/'PCI_PRESERVED_CONTENT_HASHES.json').read_text())
for path,expected in immutable.items():
 f=root/'reference'/path
 ck('unchanged preserved canonical '+path, f.is_file() and hashlib.sha256(f.read_bytes()).hexdigest()==expected)
for f in ['src/storage.ts','src/types.ts','src/theater-guidance.ts','src/feedback-model.ts','src/scenario-model.ts']:
 ck('preserved contract exists '+f,(root/f).exists())
reg=json.loads((root/'PCI_PROJECT_MANIFEST.json').read_text())
ck('storage v2 contract retained',reg['personal_data_schema_version']=='2.0.0' and 'DB_VERSION=2' in (root/'src/storage.ts').read_text())
app=(root/'src/app.tsx').read_text()
ck('ten module routes remain',all(f"slug:'{r}'" in app for r in ['command-center','self-image','beliefs','theater','feedback','conditioning','scenarios','knowledge','academy','archive']))
ck('global guard intercepts hashchange', 'canNavigateRoute(' in app and 'rollbackHash(' in app)
ck('scene and guidance not removed','phaseVisibleContent(' in (root/'src/theater.tsx').read_text() and "getRecord('rehearsals'" in (root/'src/theater.tsx').read_text())
ck('private data never bundled in public',not list((root/'public').rglob('*.pdf')) and not list((root/'public').rglob('private*.json')))
ck('manual phase budget is not automatic', 'if(!budgets || !t.timing.auto_advance)' in (root/'src/theater-model.ts').read_text())
ck('existing baseline rollbacks kept',all((root/'rollbacks'/f'PCI_APP_STAGE{i:02d}_FULL.zip').is_file() for i in (9,10,11)))
ck('offline compiler and tests remain',all((root/f).is_file() for f in ['scripts/build-offline.mjs','tests/theater_model_repo.test.mjs','tests/checkpoint1.test.mjs','tests/browser_checkpoint1.py','dist-static/assets/route-guard.js']))
result={'status':'PASS' if all(v['status']=='PASS' for v in checks) else 'FAIL','passed':sum(v['status']=='PASS' for v in checks),'failed':sum(v['status']=='FAIL' for v in checks),'checks':checks,'limits':'Structural checks only; native IndexedDB and production build require independent runtime verification.'}
(root/'audit/checkpoint1/SOURCE_PRESERVATION_QA.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:result[k] for k in ('status','passed','failed')}))
raise SystemExit(result['failed']!=0)
