#!/usr/bin/env python3
"""Reproducible checksum inventory and complete CP4 package from local source."""
import json,hashlib,zipfile,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
out=Path(sys.argv[1]) if len(sys.argv)>1 else root.parent/'PCI_APP_CHECKPOINT_4.zip'
excluded={'CHECKSUMS.sha256','FILE_INVENTORY.json'}
files=sorted(p for p in root.rglob('*') if p.is_file() and p.relative_to(root).as_posix() not in excluded)
entries=[{'path':p.relative_to(root).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]
(root/'FILE_INVENTORY.json').write_text(json.dumps({'checkpoint':'PCI-APP-CP4','file_count':len(entries),'inventory_excludes':sorted(excluded),'files':entries},indent=2)+'\n')
(root/'CHECKSUMS.sha256').write_text(''.join(f'{e["sha256"]}  {e["path"]}\n' for e in entries))
files+= [root/'FILE_INVENTORY.json',root/'CHECKSUMS.sha256']
with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=8,allowZip64=True) as z:
 for f in sorted(files):z.write(f,'PCI_APP_CHECKPOINT_4/'+f.relative_to(root).as_posix())
with zipfile.ZipFile(out) as z:
 assert z.testzip() is None
 assert len(z.namelist())==len(files)
print(json.dumps({'zip':str(out),'members':len(files),'checksums':len(entries),'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest()}))
