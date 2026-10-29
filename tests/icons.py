"""Icon / manifest / source-preservation checks; no device browser claims."""
from pathlib import Path
import json,hashlib,re,math,xml.etree.ElementTree as ET
from PIL import Image
r=Path(__file__).resolve().parents[1];d=r/'dist';base=d/'icons/atlas-v7';m=json.loads((d/'manifest.json').read_text(encoding='utf-8'));old=json.loads((r/'tests/fixtures/manifest-v15.json').read_text(encoding='utf-8'))
assert {k:v for k,v in m.items() if k!='icons'}=={k:v for k,v in old.items() if k!='icons'},'App identity changed'
for entry in m['icons']:
 p=d/entry['src'];assert p.is_file()
 if entry['type']=='image/png':
  im=Image.open(p);assert f'{im.width}x{im.height}'==entry['sizes'];assert im.mode=='RGB';assert im.getpixel((0,0))==im.getpixel((im.width-1,im.height-1))==(16,63,57)
assert {x['purpose'] for x in m['icons']}=={'any','maskable'}
assert Image.open(base/'apple-touch-icon.png').size==(180,180)
for size in [16,32]:assert Image.open(base/f'favicon-{size}.png').size==(size,size)
assert Image.open(base/'favicon.ico').ico.sizes()=={(16,16),(32,32),(48,48),(64,64)}
ns={'s':'http://www.w3.org/2000/svg'};svg=ET.parse(base/'maskable.svg');paths=svg.findall('.//s:path',ns);assert len(paths)==4
for p in paths:
 for x,y in re.findall(r'[ML]([\d.]+),([\d.]+)',p.attrib['d']):assert math.hypot(float(x)-256,float(y)-256)<204.8
html=(d/'index.html').read_text(encoding='utf-8');sw=(d/'sw.js').read_text(encoding='utf-8')
for target in re.findall(r'(?:href|src)="(icons/atlas-v7/[^\"]+)"',html):assert (d/target).is_file();assert repr(target) in sw
# Assert exact bytes of all game code, learning/recognition data, CSS and immutable payloads.
snapshot=json.loads((r/'UPSTREAM_SOURCE.json').read_text(encoding='utf-8'));baseline={x['path']:x['sha256'] for x in snapshot['source_files']};tracked=list(baseline)
protected=[p for p in tracked if p.startswith('dist/releases/') or p.startswith('dist/assets/') or p in ['dist/app.js','dist/handwriting.js','dist/bootstrap.js','dist/style.css']]
for p in protected:assert hashlib.sha256((r/p).read_bytes()).hexdigest()==baseline[p],p+' changed'
assert 'localStorage' not in sw
print('PASS icon assets: declared sizes/purposes, opaque square corners, four source islands inside maskable safe zone, HTML/SW references, same PWA identity, byte-identical game/data/category icons/save code.')
