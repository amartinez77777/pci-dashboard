"""Independent v1.1 source-integrity checks. Uses immutable input ZIP fingerprints, not historical rollback ZIPs."""
from pathlib import Path
import hashlib,json,re,sys
ROOT=Path(__file__).resolve().parents[1]
fp=json.loads((ROOT/'audit/v11/INPUT_CONTENT_FINGERPRINTS.json').read_text())
checks=[]
def check(name,ok):
 checks.append((name,bool(ok)))
 if not ok:print('FAIL',name)
check('Input source fingerprint recorded',fp['source_sha256']=='0a2392a94811cc17a3353b3b474f0994aa581c48d9b64d6748a1b275f899af8c')
check('249 protected file fingerprints stored',len(fp['protected'])==249)
missing=[];changed=[]
for rel,d in fp['protected'].items():
 path=ROOT/rel
 if not path.is_file():missing.append(rel)
 elif hashlib.sha256(path.read_bytes()).hexdigest()!=d['sha256']:changed.append(rel)
check('Every inherited research, reference, schema, IDs, storage and base CSS file byte-identical',not missing and not changed)
if missing:print('Missing:',missing[:6]);
if changed:print('Changed:',changed[:6]);
registry=json.loads((ROOT/'PCI_ID_REGISTRY.json').read_text())
concepts=json.loads((ROOT/'reference/knowledge/data/PCI_CONCEPTS.json').read_text())
curriculum=json.loads((ROOT/'public/data/curriculum.json').read_text())
check('Original 1,799 permanent IDs preserved',len(registry)==1799)
check('201 original canonical concept records',len(concepts)==201 and len({c['id'] for c in concepts})==201)
check('21 authored days preserved',len(curriculum['days'])==21 and [d['id'] for d in curriculum['days']]==[f'PCI-DAY-{i:02d}' for i in range(1,22)])
check('16 unchanged scenario chapter assets',len(list((ROOT/'public/data/scenarios').glob('*.json')))==16)
check('12 original PCI rehearsal templates',len(json.loads((ROOT/'public/data/rehearsals.json').read_text()))==12)
check('16 unchanged concept chapter assets',len(list((ROOT/'public/data/concepts').glob('*.json')))==16)
app=(ROOT/'src/app.tsx').read_text();slugs=['command-center','self-image','beliefs','theater','feedback','conditioning','scenarios','knowledge','academy','archive']
check('Ten app navigation modules present',all(f"slug:'{s}'" in app for s in slugs))
store=(ROOT/'src/storage.ts').read_text()
check('Version-2 private IndexedDB contract intact',"DB_NAME='pci-private-v1'" in store and 'DB_VERSION=2' in store and 'STORES:StoreName[]' in store)
engine=(ROOT/'src/pci-recommendations.ts').read_text();ui=(ROOT/'src/personal-intelligence.tsx').read_text()
check('Explainable recommendation logic and new Command Center are present',all(x in engine for x in ['REVIEW_DUE','OBSERVATION_PENDING','PRACTICE_UNFINISHED','RESUME_LESSON','START_WITH_GOAL']) and 'personalRecommendations' in ui)
check('Goal, belief, source and authored lesson deep links are wired',all(x in app for x in ['path={rest.join']) and 'theater/belief/' in (ROOT/'src/personal-labs.tsx').read_text() and 'conditioning/protocol/' in (ROOT/'src/vault.tsx').read_text())
check('No full book PDF or personal data under public assets',not list((ROOT/'public').rglob('*.pdf')) and not list((ROOT/'public').rglob('*PRIVATE_BACKUP*')))
check('GitHub Actions production install and build pipeline preserved',all(x in (ROOT/'.github/workflows/pci-pages.yml').read_text() for x in ['npm install','npm run build','tests/native_production_smoke.py']))
result={'status':'PASS' if all(b for _,b in checks) else 'FAIL','passed':sum(b for _,b in checks),'failed':sum(not b for _,b in checks),'checks':[{'name':n,'status':'PASS' if b else 'FAIL'} for n,b in checks], 'note':'This is structural and byte-identity validation, not PDF-image or native browser verification.'}
(ROOT/'audit/v11/INTEGRITY_QA.json').write_text(json.dumps(result,indent=2)+'\n')
print('PCI v1.1 integrity:',result['status'],result['passed'],'PASS',result['failed'],'FAIL')
sys.exit(result['failed']>0)
