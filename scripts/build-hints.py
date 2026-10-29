"""Build separate, source-linked hints; never mutate questions or accepted answers.
Positions and reference comparisons use the existing GSI/dataofjapan geometry.
Features reuse the reviewed descriptions; clue mode uses two independent map references.
"""
import json,math,collections
from pathlib import Path
r=Path(__file__).resolve().parents[1];qs=json.loads((r/'dist/assets/questions.json').read_text());fs=json.loads((r/'dist/assets/japan.geojson').read_text())['features'];byid={q['id']:q for q in qs}
positions=['本州の北にある大きな島が中心です。','東北地方の北端にあります。','東北地方の北東部にあります。','東北地方の南東部にあります。','東北地方の北西部にあります。','東北地方の南西部にあります。','東北地方の南端にあります。','関東地方の北東部にあります。','関東地方の北部、海に面しない県です。','関東地方の北西部、海に面しない県です。','関東地方の内陸部、東京都の北にあります。','関東地方の南東部にあります。','関東地方の南部で、西から東へ細長くのびています。','関東地方の南西部にあります。','中部地方の北東部、日本海側にあります。','中部地方の北部、日本海側にあります。','中部地方の北部で、日本海へ突き出した部分があります。','中部地方の北西部、日本海側にあります。','中部地方の東部、海に面しない県です。','中部地方の内陸部で、南北に長い県です。','中部地方の内陸部で、長野県の西にあります。','中部地方の南東部、太平洋側にあります。','中部地方の南部、太平洋側にあります。','近畿地方の東部、太平洋側にあります。','近畿地方の北東部、海に面しない県です。','近畿地方の北部から内陸にのびています。','近畿地方の西寄りで、瀬戸内海側にあります。','近畿地方の西部で、本州を南北にまたいでいます。','近畿地方の内陸部で、三重県の西にあります。','近畿地方の南西部、太平洋側にあります。','中国地方の北東部、日本海側にあります。','中国地方の北西部、日本海側にあります。','中国地方の南東部、瀬戸内海側にあります。','中国地方の南部、瀬戸内海側にあります。','本州の西端にあります。','四国の東部にあります。','四国の北東部、瀬戸内海側にあります。','四国の北西部、瀬戸内海側にあります。','四国の南部、太平洋側にあります。','九州の北部にあります。','九州の北西部、福岡県と長崎県の間にあります。','九州の西部で、多くの島も含みます。','九州の中央部から西側に広がっています。','九州の北東部にあります。','九州の南東部、太平洋側にあります。','九州の南部にあり、南の島々も含みます。','九州の南西に連なる島々にあります。']
edges=collections.defaultdict(set)
for f in fs:
 for poly in f['geometry']['coordinates'] if f['geometry']['type']=='MultiPolygon' else [f['geometry']['coordinates']]:
  for ring in poly:
   for a,b in zip(ring,ring[1:]):
    if a!=b:edges[tuple(sorted([tuple(a),tuple(b)]))].add(f['properties']['id'])
adj={q['pid']:set() for q in qs if q.get('pid')}
for ids in edges.values():
 if len(ids)>1:
  for i in ids:adj[i]|=ids-{i}
# The source includes an administrative sea boundary across the Seto bridge; not a land border.
adj[33].discard(37);adj[37].discard(33)
capitalFeatures={1:'石狩平野にあり、道内の中心的な都市です。',3:'北上川が流れる内陸の都市です。',4:'県の中部、太平洋側の平野にあります。',8:'那珂川の下流側にある都市です。',9:'県の中央付近にあります。',10:'県の南部、利根川沿いにあります。',11:'県の南東部にあります。',13:'答えるのは市ではなく、東京都区部にある区です。',14:'県の東部で、東京湾に面しています。',17:'県の中央部、日本海側の都市です。',19:'甲府盆地にある都市です。',23:'県の西部、濃尾平野にあります。',24:'伊勢湾に面した都市です。',25:'琵琶湖の南西側にある都市です。',28:'県の南部で、大阪湾に面しています。',32:'宍道湖の東側にある都市です。',37:'県の北部、瀬戸内海に面しています。',38:'県の西部、瀬戸内海側の都市です。',47:'沖縄島の南部、西海岸側にあります。'}
def point(q):
 if q.get('referencePoint'):return q['referencePoint']
 ps=[p for part in q.get('geometryParts',[q['geometry']]) for p in part];return [(min(p[0] for p in ps)+max(p[0] for p in ps))/2,(min(p[1] for p in ps)+max(p[1] for p in ps))/2]
anchorNames='富士山 大雪山 岩手山 磐梯山 筑波山 白山 大山 石鎚山 桜島 宮之浦岳 琵琶湖 猪苗代湖 サロマ湖 佐渡島 淡路島 屋久島 沖縄島 石垣島 利尻島 宮古島 奄美大島'.split();anchors=[q for q in qs if q['name'] in anchorNames]
def relation(q,a):
 p=point(q);p2=point(a);dx=(p[0]-p2[0])*math.cos(math.radians(p[1]));dy=p[1]-p2[1];
 if math.hypot(dx,dy)<.25:return f'位置の目安は、{a["name"]}の近くです。'
 angle=math.atan2(dy,dx);dirs=['東','北東','北','北西','西','南西','南','南東'];direction=dirs[round(angle/(math.pi/4))%8];return f'位置の目安は、{a["name"]}より{direction}側です。'
items={}
for q in qs:
 if q.get('pid'):
  i=q['pid'];near=[byid['p'+str(j)]['name'] for j in sorted(adj[i])[:3]]
  feature='県境を接するのは、'+'・'.join(near)+'などです。' if near else ('本州との間には津軽海峡があります。' if i==1 else '沖縄島のほか、宮古島や石垣島も含みます。')
  cap=capitalFeatures.get(i,'都道府県名と同じ名前の市です。')
  items[q['id']]={'position':positions[i-1],'feature':feature,'tapExtra':'県庁等の所在地は'+q['capital']+'です。','capitalPosition':'都道府県は'+q['name']+'です。','capitalFeature':cap,'sources':[{'title':'国土地理院：都道府県・都道府県庁所在地','url':'https://www.gsi.go.jp/CHIRIKYOUIKU/todofuken.html'},{'title':'地球地図日本／既存行政区域（位置と近隣関係）','url':'https://www.gsi.go.jp/kankyochiri/gm_jpn.html'}]}
 else:
  p=point(q);refs=sorted([a for a in anchors if a['id']!=q['id'] and q['name'] not in a['name'] and a['name'] not in q['name']],key=lambda a:((p[0]-point(a)[0])*math.cos(math.radians(p[1])))**2+(p[1]-point(a)[1])**2)[:2]
  feature=q['description'].replace(q['name'],'この地形');items[q['id']]={'position':'関係する地方は'+'・'.join(dict.fromkeys(next(p['region'] for p in qs if p.get('pid') and p['name']==name) for name in q['prefs']))+'。都道府県は'+'・'.join(q['prefs'])+'です。','feature':feature,'mapRelations':[relation(q,a) for a in refs],'referenceIds':[a['id'] for a in refs],'referenceSources':[{ 'id':a['id'],'sources':a.get('sources',[])} for a in refs],'sources':q.get('sources',[]),'precision':'地図の参考地点どうしの方位比較。川など長い対象の全体位置を断定するものではない。'}
out={'version':1,'checkedAt':'2026-10-18','readingRule':'ひらがな1字を1文字として数え、小書きの「ゃ・ゅ・ょ・っ」も1文字。名称の接尾語は地名本体と分ける。','items':items}
(r/'dist/assets/hints.json').write_text(json.dumps(out,ensure_ascii=False,separators=(',',':')))
print('Built separate hint records:',len(items))
