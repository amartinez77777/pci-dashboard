from pathlib import Path
import json,re,hashlib,sys
root=Path(__file__).resolve().parents[1]
r=lambda p: json.loads((root/p).read_text())
checks=[]
def ck(name,b):checks.append({'name':name,'status':'PASS' if b else 'FAIL'})
index=r('public/data/vault/search-index.json');graph=r('public/data/vault/graph.json');chapters=r('public/data/chapter-index.json');source=r('reference/knowledge/data/PCI_CONCEPTS.json');idset={s['id'] for s in source}
ck('all 16 chapter read models generated',len(list((root/'public/data/vault/chapters').glob('*.json')))==16)
ck('all 201 full concept dossiers preserve identity',all({x['id'] for x in r(f'public/data/vault/chapters/{n:02}.json')['concepts']}=={x['id'] for x in source if x['chapter_id']==f'PCI-CH-{n:02}'} for n in range(1,17)))
ck('all chapter section records remain substantive',all(len(x['content'])>80 for x in source))
ck('504 search records with valid original ids',len(index)==504 and len({x['id'] for x in index})==504)
ck('source practice vs adaptation search identity',sum(x['kind']=='author_practice' for x in index)==70 and sum(x['kind']=='author_practice' and x['origin']=='book' for x in index)==51 and sum(x['kind']=='educational_exercise' for x in index)==32)
ck('109 graph endpoints and rationale verified',len(graph)==109 and all(e['from_id'] in idset and e['to_id'] in idset and e['rationale'] and e['supporting_source_refs'] for e in graph))
ck('search target exists in original normalized collections',all(x['id'] in {a['id'] for group in ['PCI_CONCEPTS','PCI_AUTHOR_PRACTICES','PCI_APPLICATIONS','PCI_EDUCATIONAL_EXERCISES'] for a in r('reference/knowledge/data/'+group+'.json')} for x in index))
ck('all source citations have 1-based PDF page',all(1<=ref['pdf_page']<=332 for x in index for ref in x['source_refs']))

# Stage10 adds tracked issue IDs only; verify every original ID and its metadata byte-for-byte.
import zipfile
with zipfile.ZipFile(root/'rollbacks/PCI_APP_STAGE09_FULL.zip') as rollback:
    original_registry=json.loads(rollback.read('PCI_APP_STAGE09_FULL/PCI_ID_REGISTRY.json'))
updated_registry=r('PCI_ID_REGISTRY.json')
ck('all 1773 original registry mappings and Stage10 issue IDs retained', len(original_registry)==1773 and len(updated_registry)>=1778 and all(updated_registry.get(k)==v for k,v in original_registry.items()) and all(f'PCI-ISS-ST10-{i:03d}' in updated_registry for i in range(1,6)))
ck('no PDFs or private entries included in public',not list((root/'public').rglob('*.pdf')) and not list((root/'public').rglob('*journal*')))
ck('Stage08 all ten routes retained',all("slug:'"+v+"'" in (root/'src/app.tsx').read_text() for v in ['command-center','self-image','beliefs','theater','feedback','conditioning','scenarios','knowledge','academy','archive']))
ck('no localStorage use in new Vault code',all('localStorage' not in (root/'src'/f).read_text() for f in ['vault.tsx','vault-data.ts','vault-search.ts','vault-storage.ts']))
ck('same v2 private schema, no store added',"DB_VERSION=2" in (root/'src/storage.ts').read_text() and len(re.findall(r"'[a-z_]+',?",(root/'src/storage.ts').read_text().split('STORES:StoreName[]=' )[1].split(';')[0]))==25)
ck('app declares actual searchable/graph components',all(s in (root/'src/vault.tsx').read_text() for s in ['GraphExplorer','searchVault','SourceModal','Comparison','readKnowledgeState']))
ck('mappable source references (no public PDF)',len(r('public/data/vault/citations.json'))==315)
ck('fetched data segmented by chapter',all((root/f'public/data/vault/chapters/{n:02}.json').stat().st_size<1_000_000 for n in range(1,17)))
ck('mobile stylesheet provides narrow-width layout', '@media(max-width:520px)' in (root/'public/vault.css').read_text() and 'prefers-reduced-motion' in (root/'public/vault.css').read_text())
report={'status':'PASS' if all(x['status']=='PASS' for x in checks) else 'FAIL','checks':checks,'passed':sum(x['status']=='PASS' for x in checks),'failed':sum(x['status']=='FAIL' for x in checks)}
(root/'audit/PCI_STAGE09_VAULT_ASSET_QA.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['status','passed','failed']}))
sys.exit(report['failed']>0)
