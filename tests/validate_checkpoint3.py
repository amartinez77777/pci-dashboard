"""Self-contained checkpoint-3 integrity; CP2 fingerprint fixture is bundled.
No prior ZIP, external network or user data required."""
import json,hashlib,sys
from pathlib import Path
r=Path(__file__).resolve().parents[1];ROOT=r;out=r/'audit/checkpoint3';checks=[]

# Final release: one deliberately authorized storage.ts safety repair. The original
# and repaired bytes must match the exact hashes in the signed-off change record.
control=json.loads((ROOT/'audit/final/STORAGE_CHANGE_CONTROL.json').read_text())
def approved_storage():
 return (control['path']=='src/storage.ts' and
  hashlib.sha256((ROOT/'src/storage.ts').read_bytes()).hexdigest()==control['after_hardening_sha256'] and
  control['before_checkpoint4_sha256']=='7d59ab136285f9fdde14d4c85c82b866f4b7da1b1b6c39a70ef4e8fd679b4be5')

def ck(name,ok,detail=''):
 checks.append({'name':name,'status':'PASS' if ok else 'FAIL','detail':detail})
 if not ok:print('FAIL',name,detail)
sha=lambda b:hashlib.sha256(b).hexdigest()
orig=json.loads((out/'CP2_BASELINE_FINGERPRINTS.json').read_text());reg=json.loads((r/'PCI_ID_REGISTRY.json').read_text());prior=orig['original_id_metadata_sha256']
ck('1791 inherited permanent IDs and exact metadata unchanged',len(prior)==1791 and all(k in reg and sha(json.dumps(reg[k],sort_keys=True,separators=(',',':')).encode())==v for k,v in prior.items()))
additional={'PCI-ACA-Q01','PCI-ACA-Q02','PCI-ACA-Q03','PCI-ACA-Q04','PCI-ACA-Q05','PCI-ACA-Q06','PCI-ACA-Q09','PCI-ACA-Q16'}
ck('exactly 8 new immutable educational question IDs',set(reg)-set(prior)==additional and len(reg)==1799 and all(reg[k]['record_type']=='academy_question' and reg[k]['immutable'] for k in additional))
protected=orig['protected_sha256'];changed=[p for p,h in protected.items() if not (r/p).exists() or sha((r/p).read_bytes())!=h]
ck('canonical research and prior labs intact; only approved storage safety edit',len(protected)>100 and set(changed).issubset({'src/storage.ts'}) and approved_storage() and protected.get('src/storage.ts')==control['before_checkpoint4_sha256'],f'{len(protected)} checked; approved change={changed[:5]}')
program=json.loads((r/'public/data/curriculum.json').read_text());ck('21 authored curriculum records intact',program['id']=='PCI-PROG-021' and len(program['days'])==21 and sha((r/'public/data/curriculum.json').read_bytes())==protected['public/data/curriculum.json'])
ck('four checkpoints preserved',program['checkpoint_days']==[4,9,15,21])
app=(r/'src/app.tsx').read_text();ck('all 10 routes and functioning Academy mounted',all(f"slug:'{slug}'" in app for slug in ['command-center','self-image','beliefs','theater','feedback','conditioning','scenarios','knowledge','academy','archive']) and "slug==='academy'?<MentalMasteryAcademy" in app)
storage=(r/'src/storage.ts').read_text();ck('25 original v2 stores, no schema migration',"DB_VERSION=2" in storage and len(storage.split('export const STORES:StoreName[]=')[1].split('];')[0].split(','))==25)
ck('source/repo/tests and offline compiled entry exist',all((r/p).is_file() for p in ['src/academy.tsx','src/academy-model.ts','src/academy-repo.ts','tests/checkpoint3.test.mjs','tests/browser_checkpoint3.py','public/academy.css','dist-static/assets/academy.js']))
ck('no PDF or personal fixtures in public',not list((r/'public').rglob('*.pdf')) and not list((r/'public').rglob('private*.json')))
report={'status':'PASS' if all(x['status']=='PASS' for x in checks) else 'FAIL','passed':sum(x['status']=='PASS' for x in checks),'failed':sum(x['status']=='FAIL' for x in checks),'preserved_file_count':len(protected),'baseline_zip_sha256':orig['source_zip_sha256'],'scope':'Static/byte-level verification, not native browser persistence','checks':checks}
(out/'CP3_SOURCE_QA.json').write_text(json.dumps(report,indent=2)+'\n');print('CP3 SOURCE',report['status'],report['passed'],'PASS',report['failed'],'FAIL');sys.exit(report['failed']!=0)
