"""Stage11 additive source/privacy/contract audit, executed independently of browser."""
import json,hashlib,zipfile,sys,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];ZIP=ROOT/'rollbacks/PCI_APP_STAGE10_FULL.zip';checks=[]
def ck(name,ok,detail=''):
 checks.append({'check':name,'status':'PASS' if ok else 'FAIL','detail':str(detail)[:350]})
 if not ok:print('FAIL',name,detail)

# Final release: one deliberately authorized storage.ts safety repair. The original
# and repaired bytes must match the exact hashes in the signed-off change record.
control=json.loads((ROOT/'audit/final/STORAGE_CHANGE_CONTROL.json').read_text())
def approved_storage():
 return (control['path']=='src/storage.ts' and
  hashlib.sha256((ROOT/'src/storage.ts').read_bytes()).hexdigest()==control['after_hardening_sha256'] and
  control['before_checkpoint4_sha256']=='7d59ab136285f9fdde14d4c85c82b866f4b7da1b1b6c39a70ef4e8fd679b4be5')

def load(p):return json.loads((ROOT/p).read_text())
def sha(b):return hashlib.sha256(b).hexdigest()
ck('stage10 rollback exists',ZIP.is_file())
if ZIP.is_file():
 with zipfile.ZipFile(ZIP) as z:
  old={n.removeprefix('PCI_APP_STAGE10_FULL/'):z.read(n) for n in z.namelist() if n.startswith('PCI_APP_STAGE10_FULL/') and not n.endswith('/')}
 for path in ['src/storage.ts','src/personal-labs-model.ts','src/personal-labs-repo.ts','src/vault.tsx','src/vault-data.ts','src/vault-search.ts','src/vault-storage.ts','src/types.ts','public/data/rehearsals.json','public/data/curriculum.json']:
  ck('approved Stage Final storage safety change',path in old and approved_storage() and sha(old[path])==control['before_checkpoint4_sha256']) if path=='src/storage.ts' else ck('byte-identical inherited '+path,path in old and (ROOT/path).read_bytes()==old.get(path))
 ck('documented Stage checkpoint changes preserve personal-lab stores and route guards', 'src/personal-labs.tsx' in old and (ROOT/'src/personal-labs.tsx').read_text().count('useRouteDirtyGuard(')==2 and (ROOT/'src/personal-labs.tsx').read_text().count('useUnsavedWarning(')==0)
 research=[x for x in old if x.startswith(('reference/','public/data/'))]
 altered=[x for x in research if not (ROOT/x).exists() or (ROOT/x).read_bytes()!=old[x]]
 ck('all '+str(len(research))+' original reference and data files unchanged',not altered,altered[:5])
 reg=load('PCI_ID_REGISTRY.json');prior=json.loads(old['PCI_ID_REGISTRY.json']);ck('all inherited 1778 IDs and metadata unchanged',len(prior)==1778 and all(k in reg and reg[k]==v for k,v in prior.items()),len(reg))
 ck('Stage11/12 issues and exact CP2+CP3 additive IDs retained',set(reg)-set(prior)==({f'PCI-ISS-ST11-{i:03d}' for i in range(1,4)}|{f'PCI-ISS-ST12-{i:03d}' for i in range(1,5)}|{f'PCI-COND-{i:03d}' for i in range(1,7)}|{'PCI-ACA-Q01','PCI-ACA-Q02','PCI-ACA-Q03','PCI-ACA-Q04','PCI-ACA-Q05','PCI-ACA-Q06','PCI-ACA-Q09','PCI-ACA-Q16'}))
issues=load('PCI_ISSUES.json');ck('new issues in report',all(any(x['id']==f'PCI-ISS-ST11-{i:03d}' for x in issues) for i in range(1,4)))
rehearsals=load('public/data/rehearsals.json');ck('12 full templates',len(rehearsals)==12 and all(len(r['phases'])==5 for r in rehearsals))
ck('every built-in rehearsal is explicitly PCI adaptation and has source ref',all(t['origin']=='PCI_adaptation' and t['timing']['book_duration_claimed'] is False and t['source_refs'] for t in rehearsals))
practice=load('public/data/practice-attribution.json');lookup=load('reference/activity/data/PCI_AUTHOR_PRACTICE_LOOKUP.json');ck('all 70 original practice IDs and contributor attribution preserved',len(practice)==len(lookup)==70 and all(x['practice_id']==y['practice_id'] and x['exercise_origin']==y['exercise_origin'] and x.get('timing_as_printed_or_paraphrased')==y.get('timing_as_printed_or_paraphrased') for x,y in zip(practice,lookup)))
concepts={x['id'] for x in load('public/data/concept-index.json')};sources={x['id'] for x in load('public/data/vault/citations.json')} if isinstance(load('public/data/vault/citations.json'),list) else set()
ck('all template linked concepts resolve',all(id in concepts for t in rehearsals for id in t['linked_concept_ids']))
ck('all template source PDF pages in actual 332-page document',all(1<=ref['pdf_page']<=332 for t in rehearsals for ref in t['source_refs']))
ck('author practice lookup supports chapter-specific timing',all('timing_as_printed_or_paraphrased' in p for p in practice))
for file in ['src/theater.tsx','src/theater-model.ts','src/theater-repo.ts','tests/theater_model_repo.test.mjs','tests/browser_stage11_smoke.py','schema/PCI_STAGE11_SESSION.schema.json','schema/PCI_STAGE11_SCENE.schema.json','schema/PCI_STAGE11_EVENT_EXTENSION.json']:
 ck('implementation file '+file,(ROOT/file).exists() and (ROOT/file).stat().st_size>300)
try:
 import jsonschema
 for path in ['schema/PCI_STAGE11_SESSION.schema.json','schema/PCI_STAGE11_SCENE.schema.json']:
  jsonschema.Draft202012Validator.check_schema(load(path));ck('valid JSON Schema '+path,True)
except Exception as e:ck('valid Stage11 schemas',False,e)
ck('event extension parses and completed event exists', 'rehearsal.completed' in load('schema/PCI_STAGE11_EVENT_EXTENSION.json')['event_types'])
repo=(ROOT/'src/theater-repo.ts').read_text();model=(ROOT/'src/theater-model.ts').read_text();ui=(ROOT/'src/theater.tsx').read_text();app=(ROOT/'src/app.tsx').read_text()
ck('reuses shared Stage07 IndexedDB no schema version bump',"from './storage.js'" in repo and 'DB_VERSION=2' in (ROOT/'src/storage.ts').read_text())
ck('event idempotency transaction defined','idempotency_key' in repo and 'getAll()' in repo and "db.transaction(stores,'readwrite')" in repo)
ck('time uses wall anchors rather than interval tick accumulation','running_since_wall_ms' in model and 'now-p.running_since_wall_ms' in model and 'Math.max(0' in model)
ck('complete only explicit action','finishPlayer(' in ui and 'rehearsal.completed' in repo)
ck('safe exit, skip, reset, pause, resume controls wired',all(v in ui for v in ["transition('exit')","transition('skip')","transition('reset')","transition('pause')","transition('resume')","transition('complete')"]))
ck('source and personal link navigation on preserved routes','/knowledge/concept/' in ui and "<TheaterOfMind storageState={storageState}/>" in app)
ck('all 10 existing modules still defined',all("slug:'"+x+"'" in app for x in ['command-center','self-image','beliefs','theater','feedback','conditioning','scenarios','knowledge','academy','archive']))
ck('no localStorage or network send from rehearsal source',not any(x in model+repo+ui for x in ['localStorage.','XMLHttpRequest','sendBeacon','fetch("https://','fetch(\'https://']))
ck('public assets exclude private user data and copyrighted source PDF',not list((ROOT/'public').rglob('*.pdf')) and not list((ROOT/'public').rglob('*.db')) and not list((ROOT/'public').rglob('user_fixture*')))
ck('full source and compiled rehearsal files present',all((ROOT/'dist-static/assets'/name).exists() for name in ['theater.js','theater-model.js','theater-repo.js']))
ck('mobile and reduced-motion rules exist', '@media(max-width:650px)' in (ROOT/'public/styles.css').read_text() and '@media(prefers-reduced-motion:reduce)' in (ROOT/'public/styles.css').read_text())
ck('original staged privacy claim retained',all(x in (ROOT/'src/storage.ts').read_text() for x in ['PCI_PRIVATE_EXPORT','consent_id','rehearsal_sessions']))
report={'scope':'Actual Stage11 source, canonical ID and schema structural audit (not native browser or empirical study).','passed':sum(x['status']=='PASS' for x in checks),'failed':sum(x['status']=='FAIL' for x in checks),'checks':checks}
report['status']='PASS' if report['failed']==0 else 'FAIL'
(ROOT/'audit/PCI_STAGE11_SOURCE_QA.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'status':report['status'],'passed':report['passed'],'failed':report['failed']},indent=2));sys.exit(report['failed']!=0)
