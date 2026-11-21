"""CP4 self-contained acceptance/preservation gate, not clinical or native-browser verification."""
import json,hashlib,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];ROOT=root;audit=root/'audit/checkpoint4';base=json.loads((audit/'CP3_BASELINE_FINGERPRINTS.json').read_text());checks=[]

# Final release: one deliberately authorized storage.ts safety repair. The original
# and repaired bytes must match the exact hashes in the signed-off change record.
control=json.loads((ROOT/'audit/final/STORAGE_CHANGE_CONTROL.json').read_text())
def approved_storage():
 return (control['path']=='src/storage.ts' and
  hashlib.sha256((ROOT/'src/storage.ts').read_bytes()).hexdigest()==control['after_hardening_sha256'] and
  control['before_checkpoint4_sha256']=='7d59ab136285f9fdde14d4c85c82b866f4b7da1b1b6c39a70ef4e8fd679b4be5')

def ck(label,ok):
 checks.append({'name':label,'status':'PASS' if ok else 'FAIL'});
 if not ok:print('FAIL',label)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
protected=base['protected_sha256'];changed=[x for x,h in protected.items() if not (root/x).is_file() or sha(root/x)!=h]
ck(f'{len(protected)} original source/data/reference/contract files preserved, except approved storage repair',len(protected)>100 and set(changed).issubset({'src/storage.ts'}) and approved_storage() and protected.get('src/storage.ts')==control['before_checkpoint4_sha256'])
reg=json.loads((root/'PCI_ID_REGISTRY.json').read_text());ck('all 1799 stable registered IDs preserved byte-for-byte',len(reg)==1799 and sha(root/'PCI_ID_REGISTRY.json')==protected['PCI_ID_REGISTRY.json'])
manifest=json.loads((root/'PCI_PROJECT_MANIFEST.json').read_text());ck('same local DB v2 and 25 stores',manifest['personal_data_schema_version']=='2.0.0' and 'DB_VERSION=2' in (root/'src/storage.ts').read_text() and (root/'src/storage.ts').read_text().count("'bookmarks'")==1)
app=(root/'src/app.tsx').read_text();routes=['command-center','self-image','beliefs','theater','feedback','conditioning','scenarios','knowledge','academy','archive'];ck('all 10 module routes and global guard preserved',all(f"slug:'{s}'" in app for s in routes) and 'canNavigateRoute' in app and 'rollbackHash' in app)
ck('Command Center and Evolution Archive mounted as actual components',"slug==='command-center'?<PersonalCommandCenter" in app and "slug==='archive'?<PersonalEvolutionArchive" in app)
model=(root/'src/personal-intelligence-model.ts').read_text();ui=(root/'src/personal-intelligence.tsx').read_text();repo=(root/'src/personal-intelligence-repo.ts').read_text();ck('explainable counts and explicit links; no derived psychological scores',all(w in model for w in ['actualCounts','deterministicNext','goal_experiment','scene_session','lesson_practice']) and 'growth_score' not in model)
ck('private note revision, undo, and sensitive search checks',all(w in repo for w in ['revision_history','undoRemoveArchiveReflection','loadPersonalSnapshot','saveSuggestionPreference']) and 'safeArchiveSearch' in ui and 'Sensitive entry' in ui)
ck('app uses inherited SQLite-free IndexedDB and export/import',all(w in app for w in ['openPrivateDB','exportPrivate','importPrivate']) and 'indexedDB.open' in (root/'src/storage.ts').read_text())
ck('never ship user data/PDF in public assets',not list((root/'public').rglob('*.pdf')) and not list((root/'public').rglob('private*.json')))
ck('CP4 compiled assets, tests and handoff present',all((root/f).is_file() for f in ['dist-static/assets/personal-intelligence.js','dist-static/assets/personal-intelligence-repo.js','dist-static/assets/personal-intelligence-model.js','tests/checkpoint4.test.mjs','tests/browser_checkpoint4.py','public/personal-intelligence.css','HANDOFF_4.txt']))
issues=json.loads((root/'PCI_ISSUES.json').read_text());ck('original release blockers remain unresolved',any(x['id']=='PCI-ISS-ST08-001' for x in issues) and any(x['id']=='PCI-ISS-ST10-001' for x in issues))
report={'status':'PASS' if all(c['status']=='PASS' for c in checks) else 'FAIL','passed':sum(c['status']=='PASS' for c in checks),'failed':sum(c['status']=='FAIL' for c in checks),'changed_protected':changed,'scope':'Static/source preservation only; no native browser/clinical efficacy claims','checks':checks}
audit.mkdir(parents=True,exist_ok=True);(audit/'CP4_SOURCE_QA.json').write_text(json.dumps(report,indent=2)+'\n')
print('CP4 SOURCE',report['status'],report['passed'],'PASS',report['failed'],'FAIL');sys.exit(report['failed']!=0)
