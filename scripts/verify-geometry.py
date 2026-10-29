import json,math
from pathlib import Path
from shapely.geometry import Polygon,Point
p=Path('dist/assets/questions.json');qs=json.loads(p.read_text());rows=json.load(open('scripts/reference/mountain-points.json'));fs=json.load(open('dist/assets/japan.geojson'))['features']
for q in qs:
 if q.get('pid'):continue
 if q['category']=='山':
  hits=[r for r in rows if (r['name']==q['name'] or r['name'].startswith(q['name']+'（')) and (r['reading']==q['reading'] or r['reading'].startswith(q['reading']+'（'))]
  if hits:
   r=hits[0];q['geometry']=[[round(x,6) for x in r['coords']]];q['geometryAccuracy']='source-point';q['status']='国土地理院・主な山岳の山頂座標を使用';q['pointRepresents']=r['name'];q['sources'].append({'title':'山頂座標の出典','url':'https://maps.gsi.go.jp/3d/mountain/mountain.html'})
 if q['category']=='島・諸島':
  pt=Point(q['geometry'][0]);best=None
  for f in fs:
   if f['properties']['nam_ja'] not in q['prefs']:continue
   polys=f['geometry']['coordinates'] if f['geometry']['type']=='MultiPolygon' else [f['geometry']['coordinates']]
   for poly in polys:
    if len(poly[0])<4:continue
    g=Polygon(poly[0]);center=g.centroid
    # Restrict candidate to the expected island's neighborhood and avoid mainland polygons.
    if g.area>3 or g.area<.002:continue
    ref=Point(sum(x[0] for x in q['geometry'])/len(q['geometry']),sum(x[1] for x in q['geometry'])/len(q['geometry']))
    if g.contains(ref) or g.distance(ref)<.08:
     score=g.distance(ref)
     if best is None or score<best[0]:best=(score,poly[0])
  if best:
   q['geometry']=best[1];q['geometryAccuracy']='source-outline';q['status']='地球地図日本の海岸線を簡略化して使用';q['sources'].append({'title':'輪郭の出典：地球地図日本（簡略化加工）','url':'https://www.gsi.go.jp/kankyochiri/gm_jpn.html'})
p.write_text(json.dumps(qs,ensure_ascii=False,separators=(',',':')))
print([(q['name'],q.get('geometryAccuracy')) for q in qs if q.get('geometryAccuracy','schematic')!='schematic'])
