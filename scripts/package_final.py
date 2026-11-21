#!/usr/bin/env python3
"""Deterministic source inventory/checksum packager; excludes private user records and production claims."""
from pathlib import Path
import hashlib,json,zipfile
R=Path(__file__).resolve().parents[1];target=Path('/mnt/data/PCI_FINAL_SOURCE.zip')
EXCLUDE={'CHECKSUMS.sha256','FILE_INVENTORY.json'}
# Treat a real npm install's node_modules/dist as external generated products.
records=[]
for p in sorted(R.rglob('*')):
 if not p.is_file():continue
 rel=p.relative_to(R).as_posix()
 if rel in EXCLUDE or any(x in rel.split('/') for x in ['node_modules','dist','__pycache__','.git']) or p.suffix in ['.pyc','.pdf','.png','.jpg','.jpeg']:
  continue
 b=p.read_bytes();records.append({'path':rel,'size_bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
(R/'CHECKSUMS.sha256').write_text(''.join(f"{x['sha256']}  {x['path']}\n" for x in records))
manifest={'app_version':'0.12.5-rc.1','artifact_type':'source_release_candidate_NOT_production_dist','files_with_sha256':len(records),'payload_bytes':sum(x['size_bytes'] for x in records),'checksum_policy':'All payload except this inventory and CHECKSUMS.sha256 (avoid recursive checksums)','files':records}
(R/'FILE_INVENTORY.json').write_text(json.dumps(manifest,indent=2)+'\n')
with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for entry in records:z.write(R/entry['path'],arcname='PCI_FINAL_SOURCE/'+entry['path'])
 for file in EXCLUDE:z.write(R/file,arcname='PCI_FINAL_SOURCE/'+file)
with zipfile.ZipFile(target) as z:
 bad=z.testzip();assert bad is None,bad
 assert len(z.namelist())==len(records)+2
 assert 'PCI_FINAL_SOURCE/FINAL_HANDOFF.txt' in z.namelist()
 print('created',target,'bytes',target.stat().st_size,'members',len(z.namelist()),'payload_sha256',len(records),'zipsha256',hashlib.sha256(target.read_bytes()).hexdigest())
