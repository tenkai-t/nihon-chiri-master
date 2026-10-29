"""Atlas icon: existing GSI/dataofjapan coast, simplified and projected north-up.
No user state / question data writes. SVG and PNG share the same polygon coordinates.
"""
from pathlib import Path
import json,math
from shapely.geometry import Polygon
from shapely.ops import unary_union
from PIL import Image,ImageDraw
root=Path(__file__).resolve().parents[1];out=root/'dist/icons/atlas-v7';out.mkdir(parents=True,exist_ok=True)
geo=json.loads((root/'dist/assets/japan.geojson').read_text());polys=[]
for f in geo['features']:
 for rings in f['geometry']['coordinates'] if f['geometry']['type']=='MultiPolygon' else [f['geometry']['coordinates']]:
  if len(rings[0])>=4:polys.append(Polygon(rings[0]).buffer(0))
land=unary_union(polys);main=sorted([p for p in land.geoms if p.area>1],key=lambda p:-p.area)
assert len(main)==4,[(p.area,p.centroid.coords[:]) for p in main]
BG='#103f39';FG='#f4efdf';GOLD='#b89a60'
def paths(kind):
 # Local cylindrical projection: longitude scaled at 36N. No island rearrangement or rotation.
 ps=[]
 for g in main:
  g=g.simplify(.075 if kind=='favicon' else .018,preserve_topology=True)
  ps.append([(x*math.cos(math.radians(36)),-y) for x,y in g.exterior.coords])
 xs=[x for p in ps for x,y in p];ys=[y for p in ps for x,y in p];cx=(min(xs)+max(xs))/2;cy=(min(ys)+max(ys))/2
 radius=max(math.hypot(x-cx,y-cy) for p in ps for x,y in p)
 scale=(187 if kind=='maskable' else 215)/radius
 return [[(256+(x-cx)*scale,256+(y-cy)*scale) for x,y in p] for p in ps]
def svg(kind):
 ps=paths(kind);gold='' if kind=='favicon' else '<circle cx="256" cy="256" r="233" fill="none" stroke="'+GOLD+'" stroke-width="1.5" opacity=".65"/>'
 d=''.join('<path d="'+''.join(('M' if i==0 else 'L')+f'{x:.3f},{y:.3f}' for i,(x,y) in enumerate(p))+'Z"/>' for p in ps)
 return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><title>日本地理マスター</title><rect width="512" height="512" fill="{BG}"/>{gold}<g fill="{FG}">{d}</g></svg>\n'
def raster(kind,size):
 s=4;im=Image.new('RGB',(size*s,size*s),BG);d=ImageDraw.Draw(im);k=size*s/512
 if kind!='favicon':d.ellipse([23*k,23*k,489*k,489*k],outline=GOLD,width=max(1,round(1.5*k)))
 for p in paths(kind):d.polygon([(round(x*k),round(y*k)) for x,y in p],fill=FG)
 return im.resize((size,size),Image.Resampling.LANCZOS)
for kind in ['normal','maskable','favicon']:(out/(kind+'.svg')).write_text(svg(kind))
for kind,size,name in [('normal',192,'icon-192.png'),('normal',512,'icon-512.png'),('normal',180,'apple-touch-icon.png'),('maskable',192,'maskable-192.png'),('maskable',512,'maskable-512.png'),('favicon',16,'favicon-16.png'),('favicon',32,'favicon-32.png')]:raster(kind,size).save(out/name)
raster('favicon',64).save(out/'favicon.ico',sizes=[(16,16),(32,32),(48,48),(64,64)])
# Legacy filenames stay valid, including old installed manifest references.
for name in ['icon-192.png','icon-512.png','apple-touch-icon.png']:(root/'dist'/name).write_bytes((out/name).read_bytes())
(root/'dist/icon.svg').write_text(svg('normal'))
proof=Image.new('RGB',(880,560),'#ecebe3');d=ImageDraw.Draw(proof);proof.paste(raster('normal',384),(32,48));proof.paste(raster('maskable',256),(470,48));d.text((32,20),'NORMAL / APPLE',fill=BG);d.text((470,20),'MASKABLE',fill=BG)
for i,size in enumerate([16,32,60,96]):
 x=470+i*92;proof.paste(raster('favicon' if size<=32 else 'normal',size),(x,380));d.text((x,490),str(size)+' px',fill=BG)
proof.save(out/'preview.png')
(out/'provenance.json').write_text(json.dumps({'source':'https://www.gsi.go.jp/kankyochiri/gm_jpn.html','conversion':'https://github.com/dataofjapan/land','input':'assets/japan.geojson','processing':'Prefecture polygons unioned; four main islands selected by area; coast simplified; longitude scaled by cos(36 degrees), north up; no island rearrangement. Small offshore islands omitted for clarity.','colors':{'background':BG,'land':FG,'accent':GOLD},'maskableLandMaxRadius':187,'maskableSafeRadius':204.8},ensure_ascii=False,indent=2)+'\n')
print('Generated SVG / 180,192,512 PNG / maskable / 16,32 favicon / ICO. Four source islands retained.')
