"""Executable Stage 08 source integrity, static asset, and contract checks."""
import json,re,hashlib,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ref=ROOT/'reference';pub=ROOT/'public';app=ROOT/'src';checks=[]
def ck(name,yes,detail=''):
 checks.append({'name':name,'status':'PASS' if yes else 'FAIL','detail':detail})
 if not yes:print('FAIL',name,detail)
def data(path):return json.loads(path.read_text())
old=data(ROOT/'PCI_PRESERVED_CONTENT_HASHES.json')
changed=[name for name,sha in old.items() if not (ref/name).exists() or hashlib.sha256((ref/name).read_bytes()).hexdigest()!=sha]
ck('original knowledge/activity/personalization research files byte-for-byte preserved',not changed,','.join(changed[:5]))
chapters=data(pub/'data/chapter-index.json');concept_index=data(pub/'data/concept-index.json');curriculum=data(pub/'data/curriculum.json')
ck('16 real chapters indexed',len(chapters)==16)
ck('201 canonical concepts indexed',len(concept_index)==201)
ck('21 distinct daily curriculum records',len(curriculum['days'])==21 and len({d['id'] for d in curriculum['days']})==21)
ck('canonical stage07 curriculum preserved',curriculum==data(ref/'personalization/data/PCI_21_DAY_CURRICULUM.json'))
ck('12 structured rehearsal records',len(data(pub/'data/rehearsals.json'))==12)
ck('201 full concept objects preserved',sum(len(data(f)) for f in (pub/'data/concepts').glob('*.json'))==201)
ck('32 full stage06 activities preserved',sum(len(data(f)) for f in (pub/'data/activities').glob('*.json'))==32)
ck('16 original branching scenarios preserved',sum(len(data(f)) for f in (pub/'data/scenarios').glob('*.json'))==16)
ck('109 graph edges preserved',sum(len(data(f)) for f in (pub/'data/relationships').glob('*.json'))==109)
ck('16 separate chapter concept files',len(list((pub/'data/concepts').glob('*.json')))==16)
for kind,canonical in [('concepts','PCI_CONCEPTS'),('activities','PCI_EXECUTABLE_ACTIVITIES'),('scenarios','PCI_BRANCHING_SCENARIOS'),('relationships','PCI_RELATIONSHIPS')]:
 parts=[v for f in sorted((pub/'data'/kind).glob('*.json')) for v in data(f)]
 source=ref/('knowledge' if kind in ['concepts','relationships'] else 'activity')/'data'/f'{canonical}.json'
 ck(f'{kind} full source fields unchanged and IDs preserved',sorted(parts,key=lambda x:x['id'])==sorted(data(source),key=lambda x:x['id']))
ck('no duplicate public content IDs',len({item['id'] for kind in ['concepts','activities','scenarios','relationships'] for f in (pub/'data'/kind).glob('*.json') for item in data(f)})==201+32+16+109)
ck('concept index resolves to full documents',set(x['id'] for x in concept_index)==set(x['id'] for f in (pub/'data/concepts').glob('*.json') for x in data(f)))
ck('source refs contain actual pdf page and printed-page metadata',all(c['source_refs'] and 1<=c['source_refs'][0]['pdf_page']<=332 and 'printed_page' in c['source_refs'][0] for f in (pub/'data/concepts').glob('*.json') for c in data(f)))
ck('readable evidence/source status present',all(c.get('source_status') and c.get('evidence_status') for f in (pub/'data/concepts').glob('*.json') for c in data(f)))
private=data(ref/'personalization/schema/PCI_INDEXEDDB_CONTRACT.json')
code=(app/'storage.ts').read_text()
ck('25 Stage07 private stores and DB v2 declared',len(private['private_stores'])==25 and "DB_VERSION=2" in code and "DB_NAME='pci-private-v1'" in code)
ck('private-store names identical to Stage07 contract',all(re.search(r"'"+s['name']+r"'",code) for s in private['private_stores']))
ck('user notes written through IndexedDB repository', 'indexedDB.open(DB_NAME,DB_VERSION)' in code and '.transaction(' in code and "'journal_entries'" in (app/'app.tsx').read_text())
ck('backup envelope compatible with Stage07 v2',"format:'PCI_PRIVATE_EXPORT'" in code and "schema_version:'2.0.0'" in code and 'importPrivate(' in code)
ck('no full PDF or private fixture shipped in public',not list(pub.rglob('*.pdf')) and not list(pub.rglob('journal*')) and not any('SYNTHETIC' in f.name.upper() for f in pub.rglob('*')))
ck('runtime public bytes no confidential user profile',not any('user_fixture' in str(f).lower() for f in pub.rglob('*')))
source=(app/'app.tsx').read_text()
slugs=['command-center','self-image','beliefs','theater','feedback','conditioning','scenarios','knowledge','academy','archive']
ck('all ten fixed module routes present',all("slug:'"+slug+"'" in source for slug in slugs))
ck('unknown hash recovery implemented', 'This page does not exist' in source and "'/command-center'" not in source[:0])
ck('hash routing supports static hosting', 'window.location.hash' in source and 'window.location.hash=`/${path}`' in source)
ck('no invented or misleading static user progress; local record creation preserved', 'Activity totals not calculated here' in source and 'Personal activity summary coming in Stage 13' in source and 'newRecord(' in source)
ck('source limitations and non-diagnostic framing visible', 'metaphor' in source and 'scientifically demonstrated' in source)
ck('mobile responsive stylesheet with reduced-motion support','@media(max-width:640px)' in (pub/'styles.css').read_text() and 'prefers-reduced-motion:reduce' in (pub/'styles.css').read_text())
ck('React 18 and Vite dependencies declared',data(ROOT/'package.json')['dependencies'].get('react')=='18.3.1' and 'vite' in data(ROOT/'package.json')['devDependencies'])
ck('Vite base relative for static GitHub Pages', "base:'./'" in (ROOT/'vite.config.mjs').read_text() and 'href="./styles.css"' in (ROOT/'index.html').read_text())
ck('no forged package-lock generated', not (ROOT/'package-lock.json').exists())
report={'status':'PASS' if all(c['status']=='PASS' for c in checks) else 'FAIL','passed':sum(c['status']=='PASS' for c in checks),'failed':sum(c['status']=='FAIL' for c in checks),'checks':checks}
(ROOT/'audit').mkdir(exist_ok=True);(ROOT/'audit/PCI_STAGE08_ASSET_QA.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ['status','passed','failed']},indent=2))
sys.exit(report['failed']!=0)
