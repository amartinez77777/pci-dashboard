"""Deterministic checkpoint-2 baseline/content integrity checks. No browser claims."""
import json,hashlib,re,sys
from pathlib import Path
r=Path(__file__).resolve().parents[1];ROOT=r;a=r/'audit/checkpoint2';checks=[]

# Final release: one deliberately authorized storage.ts safety repair. The original
# and repaired bytes must match the exact hashes in the signed-off change record.
control=json.loads((ROOT/'audit/final/STORAGE_CHANGE_CONTROL.json').read_text())
def approved_storage():
 return (control['path']=='src/storage.ts' and
  hashlib.sha256((ROOT/'src/storage.ts').read_bytes()).hexdigest()==control['after_hardening_sha256'] and
  control['before_checkpoint4_sha256']=='7d59ab136285f9fdde14d4c85c82b866f4b7da1b1b6c39a70ef4e8fd679b4be5')

def ck(name,ok):
 checks.append({'check':name,'status':'PASS' if ok else 'FAIL'})
 if not ok:print('FAIL',name)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
orig=json.loads((a/'CP1_BASELINE_FINGERPRINTS.json').read_text())
ck('all CP1 original data/contract files identical except approved storage safety edit',approved_storage() and orig['immutable_files'].get('src/storage.ts')==control['before_checkpoint4_sha256'] and all((r/p).is_file() and sha(r/p)==h for p,h in orig['immutable_files'].items() if p!='src/storage.ts'))
reg=json.loads((r/'PCI_ID_REGISTRY.json').read_text());cks=orig['id_metadata_hashes']
ck('all original 1785 permanent IDs and metadata retained',len(cks)==1785 and all(k in reg and hashlib.sha256(json.dumps(reg[k],sort_keys=True,separators=(',',':')).encode()).hexdigest()==v for k,v in cks.items()))
new=set(reg)-set(cks);ck('only six conditioning and eight Academy quiz IDs are additive',new=={f'PCI-COND-{i:03d}' for i in range(1,7)} | {'PCI-ACA-Q01','PCI-ACA-Q02','PCI-ACA-Q03','PCI-ACA-Q04','PCI-ACA-Q05','PCI-ACA-Q06','PCI-ACA-Q09','PCI-ACA-Q16'} and len(reg)==1799)
ck('protocols are registered as immutable educational content',all(reg[x]['immutable'] and reg[x]['record_type']=='conditioning_protocol' for x in new if x.startswith('PCI-COND-')) and all(reg[x]['immutable'] and reg[x]['record_type']=='academy_question' for x in new if x.startswith('PCI-ACA-')))
manifest=json.loads((r/'PCI_PROJECT_MANIFEST.json').read_text());ck('schema 2 local stores unchanged',manifest['personal_data_schema_version']=='2.0.0' and 'DB_VERSION=2' in (r/'src/storage.ts').read_text() and len(re.findall(r"'[_a-z]+'",(r/'src/storage.ts').read_text().split('export const STORES:StoreName[]=')[1].split('];')[0]))==25)
app=(r/'src/app.tsx').read_text();ck('all ten routes and real conditioning component mounted',all(f"slug:'{slug}'" in app for slug in ['command-center','self-image','beliefs','theater','feedback','conditioning','scenarios','knowledge','academy','archive']) and "slug==='conditioning'?<MentalConditioningLab" in app)
ck('six protocols, source links and origin explicitly in data',len(re.findall(r"id:'PCI-COND-\d{3}'",(r/'src/conditioning-model.ts').read_text()))==6 and (r/'src/conditioning-model.ts').read_text().count("origin:'PCI_adaptation'")>=6)
ck('session/event/review use established private stores',all(x in (r/'src/conditioning-repo.ts').read_text() for x in ["'practice_sessions'","'review_ratings'","'events'","saveLearningTransaction"]))
ck('no full PDF or user data serialized to public',not list((r/'public').rglob('*.pdf')) and not list((r/'public').rglob('private*.json')))
ck('offline harness and pruned rollback fixtures retained',all((r/'rollbacks'/f'PCI_APP_STAGE{i:02d}_FULL.zip').is_file() for i in [9,10,11]) and (r/'dist-static/assets/conditioning.js').is_file())
ck('test and handoff present',all((r/f).is_file() for f in ['tests/checkpoint2.test.mjs','tests/browser_checkpoint2.py','HANDOFF_2.txt','scripts/build-offline.mjs']))
report={'status':'PASS' if all(x['status']=='PASS' for x in checks) else 'FAIL','passed':sum(x['status']=='PASS' for x in checks),'failed':sum(x['status']=='FAIL' for x in checks),'checks':checks,'scope':'Source fingerprints and contracts; no native browser or empirical evidence claims'}
(a/'CP2_SOURCE_QA.json').write_text(json.dumps(report,indent=2)+'\n');print('CHECKPOINT2 AUDIT',report['status'],report['passed'],'PASS',report['failed'],'FAIL');sys.exit(report['failed']!=0)
