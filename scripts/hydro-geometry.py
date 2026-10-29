"""Extract named hydro features from GSI Global Map Japan 2.0.
Input: directory of unzipped gm-jpn-hydro_u_2 (source URL recorded in data).
"""
import json,sys
from pathlib import Path
import shapefile
from shapely.geometry import LineString,Polygon
p=Path('dist/assets/questions.json');qs=json.loads(p.read_text());base=Path(sys.argv[1]);water=shapefile.Reader(str(base/'inwatera_jpn'),encoding='utf-8');river=shapefile.Reader(str(base/'riverl_jpn'),encoding='utf-8')
names={'琵琶湖':'BIWA KO','霞ヶ浦':'KASUMI-GA URA','猪苗代湖':'INAWASHIRO KO','サロマ湖':'SAROMA KO','十和田湖':'TOWADA KO','諏訪湖':'SUWA KO','信濃川':'SHINANO G.','利根川':'TONE G.','木曽川':'KISO G.','四万十川':'SHIMANTO G.','石狩川':'ISHIKARI G.','北上川':'KITAKAMI G.','最上川':'MOGAMI G.','淀川':'YODO G.','吉野川':'YOSHINO G.','筑後川':'CHIKUGO G.'}
report=[]
for q in qs:
 if q['name'] not in names:continue
 reader=river if q['category']=='川' else water;parts=[]
 for sr in reader.iterShapeRecords():
  if sr.record['nam'].strip()!=names[q['name']]:continue
  starts=list(sr.shape.parts)+[len(sr.shape.points)]
  for a,b in zip(starts,starts[1:]):
   coords=sr.shape.points[a:b]
   if len(coords)<2:continue
   # Exclude unrelated rivers of identical romanized name by distance to existing reference extent.
   if q['category']=='川':
    near=LineString(q['geometry']).distance(LineString(coords))
    if near>0.4:continue
    g=LineString(coords).simplify(.0008)
    points=list(g.coords)
   else:
    if len(coords)<4:continue
    g=Polygon(coords).simplify(.0005,preserve_topology=True);points=list(g.exterior.coords)
   parts.append([[round(x,5),round(y,5)] for x,y in points])
 if not parts:report.append((q['name'],'NOT FOUND'));continue
 q['geometryParts']=parts;q['geometry']=max(parts,key=len);q['geometryAccuracy']='source-hydro';q['sourceFeature']=names[q['name']];q['status']='国土地理院「地球地図日本」第2版の水系データを簡略化。2011年公開資料のため、現況の細部とは異なる場合があります。';q['sources'].append({'title':'水系形状の出典：地球地図日本 第2版（簡略化加工）','url':'https://www.gsi.go.jp/kankyochiri/gm_jpn.html'});q['geometryProvenance']={'source':'https://www1.gsi.go.jp/geowww/globalmap-gsi/download/data/gm-japan/gm-jpn-hydro_u_2.zip','retrievedFrom':'https://huggingface.co/datasets/yuiseki/gsi-global-map-jp/resolve/main/raw/vector-2.0/gm-jpn-hydro_u_2.zip','feature':names[q['name']],'layer':'riverl_jpn' if q['category']=='川' else 'inwatera_jpn','simplificationDegrees':.0008 if q['category']=='川' else .0005};report.append((q['name'],len(parts)))
p.write_text(json.dumps(qs,ensure_ascii=False,separators=(',',':')));print(report)
