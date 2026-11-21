"""Stage10 additive preservation/privacy/schema audit, reproducible from repository root."""
import hashlib,json,os,re,zipfile,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE=Path(os.environ.get('PCI_STAGE09_ORIGINAL',str(ROOT/'rollbacks/PCI_APP_STAGE09_FULL.zip')))
checks=[]

# Final release: one deliberately authorized storage.ts safety repair. The original
# and repaired bytes must match the exact hashes in the signed-off change record.
control=json.loads((ROOT/'audit/final/STORAGE_CHANGE_CONTROL.json').read_text())
def approved_storage():
 return (control['path']=='src/storage.ts' and
  hashlib.sha256((ROOT/'src/storage.ts').read_bytes()).hexdigest()==control['after_hardening_sha256'] and
  control['before_checkpoint4_sha256']=='7d59ab136285f9fdde14d4c85c82b866f4b7da1b1b6c39a70ef4e8fd679b4be5')

def test(name,ok,detail=''):
 checks.append({'check':name,'status':'PASS' if ok else 'FAIL','detail':str(detail)[:200]})
 if not ok:print('FAIL:',name,detail)
def sha(data):return hashlib.sha256(data).hexdigest()
if not SOURCE.exists():test('previous source archive exists',False,str(SOURCE))
else:
 with zipfile.ZipFile(SOURCE) as z:
  original={n.split('PCI_APP_STAGE09_FULL/',1)[1]:z.read(n) for n in z.namelist() if n.startswith('PCI_APP_STAGE09_FULL/') and not n.endswith('/')}
 for f in ['src/types.ts','src/storage.ts','src/data.ts','src/vault-data.ts','src/vault-search.ts','src/vault-storage.ts','src/vault.tsx','public/vault.css']:
  test('documented storage hardening '+f,approved_storage() and sha(original[f])==control['before_checkpoint4_sha256']) if f=='src/storage.ts' else test('unmodified '+f,sha((ROOT/f).read_bytes())==sha(original[f]))
 static=[p for p in original if p.startswith(('public/data/','reference/'))]
 mismatches=[p for p in static if not (ROOT/p).exists() or sha((ROOT/p).read_bytes())!=sha(original[p])]
 test('all '+str(len(static))+' upstream data/reference assets byte-preserved',not mismatches,mismatches[:10])
 for f in ['PCI_PROJECT_MANIFEST.json','PCI_ID_REGISTRY.json','PCI_ISSUES.json']:
  test('canonical required '+f,(ROOT/f).exists())
registry=json.loads((ROOT/'PCI_ID_REGISTRY.json').read_text())
original_registry=json.loads(original['PCI_ID_REGISTRY.json'].decode()) if SOURCE.exists() else {};test('all original 1773 IDs and metadata preserved',len(original_registry)==1773 and all(k in registry and registry[k]==v for k,v in original_registry.items()),len(registry))
test('5 new issue IDs registered',len(registry)>=1778 and all(f'PCI-ISS-ST10-{i:03d}' in registry for i in range(1,6)))
idx=json.loads((ROOT/'public/data/concept-index.json').read_text())
valid={x['id'] for x in idx}
from subprocess import run
for group in ['professional','communication','coaching','relationships','confidence','goals']:
 m=re.search(rf"{group}:\[([^\]]+)\]",(ROOT/'src/personal-labs-model.ts').read_text())
 ids=re.findall(r"PCI-C-CH\d{2}-\d{3}",m.group(1)) if m else []
 test('explicit '+group+' concepts valid',len(ids)==3 and all(i in valid for i in ids),ids)
for p in ['schema/PCI_STAGE10_BELIEF_DATA.schema.json','schema/PCI_STAGE10_EVENT_EXTENSION.json']:
 try:json.loads((ROOT/p).read_text());test('parse '+p,True)
 except Exception as e:test('parse '+p,False,str(e))
try:
 import jsonschema
 schema=json.loads((ROOT/'schema/PCI_STAGE10_BELIEF_DATA.schema.json').read_text());jsonschema.Draft202012Validator.check_schema(schema);test('belief JSON Schema itself valid',True)
except Exception as e:test('belief JSON Schema itself valid',False,str(e))
for source in ['src/personal-labs.tsx','src/personal-labs-model.ts','src/personal-labs-repo.ts']:
 text=(ROOT/source).read_text()
 test('privacy boundaries '+source,not re.search(r'(localStorage\.|fetch\s*\(|XMLHttpRequest|sendBeacon|navigator\.geolocation)',text))
app=(ROOT/'src/app.tsx').read_text()
test('existing 10 routes retained',len(re.findall(r"slug:'(command-center|self-image|beliefs|theater|feedback|conditioning|scenarios|knowledge|academy|archive)'",app))==10)
test('both labs actively mounted',"<SelfImageLab storageState={storageState}/>" in app and "<BeliefStudio storageState={storageState}" in app)
test('no original full book PDF in static assets',not list((ROOT/'public').rglob('*.pdf')))
test('no user records in public',not any('private' in x.name.lower() and x.suffix in ('.json','.db') for x in (ROOT/'public').rglob('*')))
source=(ROOT/'src/personal-labs-repo.ts').read_text();test('uses same 25-store IDB v2 repository',"from './storage.js'" in source and (ROOT/'src/storage.ts').read_text().count("export const DB_VERSION=2") == 1)
test('maintains before/after revision snapshots',"before:prior.data,after:snap" in source)
test('save/delete guarded by transactions',"db.transaction(LAB_STORES,'readwrite')" in source and "deleteBeliefCascade" in source)
test('source links never auto-authoritative',"Book statements are not independently proven" in (ROOT/'src/personal-labs.tsx').read_text())
report={'scope':'Stage10 code, static source and schema audit. Not scientific, React18 production, physical iPhone or native IndexedDB validation.','status':'PASS' if all(x['status']=='PASS' for x in checks) else 'FAIL','passed':sum(x['status']=='PASS' for x in checks),'failed':sum(x['status']=='FAIL' for x in checks),'checks':checks}
(ROOT/'audit/PCI_STAGE10_ASSET_QA.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'status':report['status'],'passed':report['passed'],'failed':report['failed']},indent=2));sys.exit(1 if report['failed'] else 0)
