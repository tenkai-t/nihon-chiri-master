"""Synchronize the immutable release payload after source/data changes, then validate before publication.
The public URL and localStorage namespace stay unchanged. Do not reuse this release ID on a future update.
"""
from pathlib import Path
import json,shutil,hashlib
root=Path(__file__).resolve().parents[1];d=root/'dist';release=d/'releases/startup-header-20261030';release.mkdir(parents=True,exist_ok=True)
for name in ['app.js','security.js','online.js','style.css','handwriting.js','assets/questions.json','assets/japan.geojson','assets/handwriting.json','assets/hints.json']:
 target=release/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(d/name,target)
manifest={name:hashlib.sha256((release/name).read_bytes()).hexdigest() for name in ['app.js','security.js','online.js','style.css','handwriting.js','assets/questions.json','assets/japan.geojson','assets/handwriting.json','assets/hints.json']}
(release/'checksums.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('Built coherent startup-header-20261030 payload:',len(manifest),'files')
