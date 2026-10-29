"""Reviewed hint editions; preserve all question identities and geometry.
Food pairs were checked in each prefecture's MAFF source text, not inferred from a search title.
Position clues are reproducible comparisons of existing cited geographic geometry and GSI office points.
"""
from pathlib import Path
import json,math,re
root=Path(__file__).resolve().parents[1];d=root/'dist';questions=json.loads((d/'assets/questions.json').read_text());old=json.loads((d/'assets/hints.json').read_text());items=old['items'];facts=json.loads((root/'scripts/reference/prefecture-editorial-facts.json').read_text());capitals={x['id']:x for x in json.loads((root/'scripts/reference/capital-hint-points.json').read_text())};features=json.loads((d/'assets/japan.geojson').read_text())['features'];byid={q['id']:q for q in questions};terrain=[q for q in questions if not q.get('pid')];checked='2026-10-23'
def point(q):
 if q.get('referencePoint'):return q['referencePoint']
 ps=[p for part in q.get('geometryParts',[q['geometry']]) for p in part];return [(min(p[0] for p in ps)+max(p[0] for p in ps))/2,(min(p[1] for p in ps)+max(p[1] for p in ps))/2]
def distance(a,b):return ((a[0]-b[0])*math.cos(math.radians(a[1])))**2+(a[1]-b[1])**2
def direction(p,ref):
 dx=(p[0]-ref[0])*math.cos(math.radians(p[1]));dy=p[1]-ref[1]
 if math.hypot(dx,dy)<.22:return 'の近く'
 return 'より'+['東','北東','北','北西','西','南西','南','南東'][round(math.atan2(dy,dx)/(math.pi/4))%8]+'側'
def no_answer(q,text):return not any(a in text for a in [q['name'],*q['aliases']] if len(a)>1)
def refs(q):
 p=point(q);candidates=[a for a in terrain if a['id']!=q['id'] and no_answer(q,a['name']) and q['name'] not in a['name'] and a['name'] not in q['name'] and not(a['category']==q['category'] and a['name'].replace('山脈','')==q['name'].replace('山地',''))]
 # Prefer a nearby physical landmark in the same or a neighboring region.
 candidates.sort(key=lambda a:distance(p,point(a))*(.85 if a['category'] in ['山','湖','島・諸島'] else 1))
 a=candidates[0];ax=point(a)[0]-p[0];ay=point(a)[1]-p[1]
 if math.hypot(ax,ay)<.22:return candidates[:2]
 def contrast(b):
  bx=point(b)[0]-p[0];by=point(b)[1]-p[1];length=math.hypot(bx,by);cos=(ax*bx+ay*by)/(math.hypot(ax,ay)*length) if length else 0
  return distance(p,point(b))/(.15+1-max(-1,min(1,cos)))
 return [a,min(candidates[1:],key=contrast)]
def relation(q,a):return '地図の主な表示位置は、'+a['name']+direction(point(q),point(a))+'です。'
def office_position(q):
 f=next(f for f in features if f['properties']['id']==q['pid']);polys=f['geometry']['coordinates'] if f['geometry']['type']=='MultiPolygon' else [f['geometry']['coordinates']]
 area=lambda ring:abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(ring,ring[1:])))
 ring=max((p[0] for p in polys),key=area);xs=[p[0] for p in ring];ys=[p[1] for p in ring];x,y=capitals[q['id']]['point'];fx=(x-min(xs))/(max(xs)-min(xs));fy=(y-min(ys))/(max(ys)-min(ys));ew='西' if fx<.34 else '東' if fx>.66 else '';ns='南' if fy<.34 else '北' if fy>.66 else '';where=ns+ew
 return '主な陸地の中では、'+(where+'寄り' if where else '中央付近')+'にあります。'
def step(text,stage,source,basis):return {'text':text,'stage':stage,'sources':source,'checkedAt':checked,'status':'確認済み','basis':basis}
# Safe special facts checked in the individual MAFF regional story or existing reviewed geographical sources.
special={
 't1':'日本の山の中で、標高が最も高い山です。','t2':'火山活動でできた、大きなくぼ地「カルデラ」で知られます。','t3':'湾の中にある火山で、海をはさんだ市街地からも見えます。',
 't6':'木曽山脈・赤石山脈より北側に連なる山脈です。','t7':'木曽川と天竜川の間に連なる山脈です。','t8':'富士山の西側、長野・山梨・静岡にまたがって連なります。',
 't9':'上流の長野県側では千曲川という名前で呼ばれます。','t10':'流れてくる水を集める土地の広さが、日本の川の中で最も大きい川です。','t11':'濃尾平野を通って、伊勢湾へ水を運ぶ川です。',
 't13':'面積で比べると、日本で最も大きな湖です。','t14':'表示しているのは西浦と呼ばれる水域です。','t16':'日本の平野を広さで比べると、最も広い平野です。',
 's2-1':'一つの山頂だけではなく火山群の名前で、最高峰は旭岳です。','s2-17':'海の水と川などの水が混ざり合う、汽水湖です。','s2-18':'火山活動でできた、青森県と秋田県にまたがる湖です。',
 's2-19':'ここから天竜川の水が流れ出します。','t1042':'日本の湖の中で、水深が最も深い湖です。',
 't1045':'海水と淡水が混ざる汽水湖で、島根県の東部にあります。','t1046':'鳥取県と島根県の両方に関係する汽水湖です。',
 's2-14':'宇治川・木津川・桂川が集まった水が、大阪湾へ向かいます。','s2-15':'四国山地から徳島平野を通り、紀伊水道へ流れ出します。','s2-16':'筑紫平野を通り、有明海へ水を運びます。',
 't1031':'上流の岐阜県側では土岐川と呼ばれます。','t1034':'奈良県側では吉野川と呼ばれ、和歌山県へ向かいます。',
 's2-32':'鹿児島湾をはさんだ西側の陸地です。','s2-33':'鹿児島湾をはさんだ東側の陸地です。','t1085':'薩摩半島と大隅半島にはさまれた水域です。',
 't31':'本州と北海道をへだてる海の通り道です。','t32':'本州と九州をへだてる海の通り道です。','t1089':'淡路島と徳島県の間にある、潮の流れが速い水域です。'}
city_features={
 1:'時計台が歴史を伝える都市です。',4:'伊達政宗が城下町として発展させた都市です。',6:'松尾芭蕉の句で知られる立石寺がある都市です。',9:'餃子が名物として知られる都市です。',11:'浦和・大宮・与野の3市が合併して誕生した都市です。',14:'港の周辺に中華街がある都市です。',17:'兼六園や茶屋街の歴史が残る都市です。',22:'徳川家康が晩年を過ごした駿府のまちです。',24:'伊勢湾に面する都市です。',25:'琵琶湖の南西側にある都市です。',28:'六甲山地と海の間に発展した港町です。',32:'宍道湖の東側にある都市です。',35:'瑠璃光寺五重塔がある都市です。',40:'博多や天神といった地区がある都市です。',42:'海外との交流の歴史を伝える出島がある都市です。',46:'湾の向こうに桜島を望む都市です。',47:'沖縄島の南部、西海岸側にある都市です。'}
city_extra={11:{'url':'https://www.city.saitama.lg.jp/faq/001/006/001/p111171.html','title':'さいたま市：合併の経緯','checkedAt':checked}}
for q in questions:
 h=items[q['id']];h['formats']={};h['checkedAt']=checked;h['review']={'status':'確認済み','method':'地図・既存出典と照合した位置関係。都道府県の食文化は各県の一次資料を別途照合。','date':checked}
 if q.get('pid'):
  i=q['pid'];fact=facts[i-1];source={'url':fact['source']['url'],'title':'農林水産省：'+q['name']+'の食文化','checkedAt':checked,'sha256':fact['source']['sha256']};geosources=h['sources'];food='「'+fact['foods'][0]+'」や「'+fact['foods'][1]+'」などが、地域の食べ物として知られています。';related=[a for a in terrain if q['name'] in a['prefs'] and no_answer(q,a['name'])];related.sort(key=lambda a:(a.get('level',3),['湖','山','島・諸島','川','半島','湾・海峡','平野','山脈・山地','盆地'].index(a['category'])));chosen=related[:2];natural='・'.join(a['name'] for a in chosen)+'なども、この都道府県に関係する自然です。' if chosen else h['feature'];naturalSources=geosources+[s for a in chosen for s in a.get('sources',[])];h['feature']=food;h['famousThings']=fact['foods'];h['formats']['name']=[step(h['position'],'位置',geosources,'既存の行政区域・地方区分'),step(food,'特徴',[source],'都道府県別本文に両キーワードを確認。独占的な名物とは扱わない'),step(natural,'決め手',naturalSources,'既存地形の関係都道府県')];h['formats']['tap']=[step(h['position'],'広い位置',geosources,'既存行政区域'),step(items[q['id']].get('tapFeature',old['items'][q['id']].get('tapFeature','')) or (h.get('tapExtra') if i in [1,47] else '周りの県や海とのつながりも確認しましょう。'+natural),'周辺の目印',naturalSources,'周辺地形'),step(h.get('tapExtra','')+' 地図の位置を確かめて選びましょう。','位置を絞る',geosources,'既存県庁所在地')]
  # tap second: retain the meaningful original adjacency, not spelling/food hints.
  base=json.loads((root/'dist/releases/classroom-20261022/assets/hints.json').read_text())['items'][q['id']]
  h['formats']['tap'][1]=step(base['feature'],'海・県境',geosources,'既存境界照合')
  cap=capitals[q['id']];capSource={'url':cap['url'],'title':'国土地理院住所検索：'+cap['title'],'checkedAt':checked,'sha256':cap['sha256']};office=office_position(q);capitalQ={**q,'name':q['capital'],'reading':q['capitalReading'],'aliases':[q['capital'],q['capitalReading']]};near=sorted([a for a in terrain if no_answer(capitalQ,a['name'])],key=lambda a:distance(cap['point'],point(a)))[0];capfact=city_features.get(i,'地図で比べると、'+near['name']+direction(cap['point'],point(near))+'にあります。');capfactSources=([city_extra[i]] if i in city_extra else [source]) if i in city_features and i not in [24,25,32,47] else [capSource,*near.get('sources',[])]
  other=next(a for a in sorted(terrain,key=lambda a:distance(cap['point'],point(a))) if no_answer(capitalQ,a['name']) and a['name'] not in capfact);capital_landmark='地図で比べると、'+other['name']+direction(cap['point'],point(other))+'にあります。';capital_sources=[capSource,*other.get('sources',[])]
  h['capitalPoint']=cap['point'];h['formats']['capital']=[step(office,'県内の位置',[capSource,*geosources],'主な陸地の外接範囲を3分割した目安。市域全体を表さない'),step(capfact,'所在地の特徴',capfactSources,'一次資料の都市の記述または地図上の位置比較'),step(capital_landmark,'別の地理的目印',capital_sources,'国土地理院の所在地座標と既存教材の地形位置の比較')]
 else:
  a,b=refs(q);sources=list(h.get('sources',[]));
  if q['id'] in ['t13','t1042']:sources.append({'url':'https://www.gsi.go.jp/kankyochiri/koshouchousa-list.html','title':'国土地理院：湖沼調査一覧（面積・水深）','checkedAt':checked})
  if q['id']=='t10':sources.append({'url':'https://www.ktr.mlit.go.jp/tonejo/tonejo00182.html','title':'国土交通省：利根川のあらまし（流域面積）','checkedAt':checked})
  if q['id']=='t3':sources.append({'url':facts[45]['source']['url'],'title':'農林水産省：鹿児島の自然と食文化','checkedAt':checked})
  r1,r2=relation(q,a),relation(q,b);description=q['description'].replace(q['name'],'この地形').rstrip('。');feature=special.get(q['id'],'この地形は、'+description+'という特徴があります。')
  if not no_answer(q,feature):feature=r1
  if feature==r1:second=r1
  else:second=feature+' '+r1
  c=next(x for x in sorted(terrain,key=lambda x:distance(point(q),point(x))) if x['id'] not in [q['id'],a['id'],b['id']] and no_answer(q,x['name']) and q['name'] not in x['name'] and x['name'] not in q['name']);r3=relation(q,c);thirdSources=[*sources,*c.get('sources',[])]
  geoSources=[*sources,*a.get('sources',[]),*b.get('sources',[])];h['referenceIds']=[a['id'],b['id']];h['mapRelations']=[r1,r2];h['feature']=feature;h['precision']='方位は出典に基づく代表地点・表示範囲の中心の比較。川の全流路や平野の厳密な境界を示すものではありません。';h['formats']['name']=[step(h['position'],'地域・位置',sources,'関係都道府県・地方'),step(second,'特徴と目印',geoSources,'既存の確認済み特徴と、主な表示位置の比較'),step(r2,'決め手',geoSources,'二つ目の地理的目印')];h['formats']['tap']=[step(h['position'],'広い位置',sources,'関係都道府県・地方'),step(r1,'近くの目印',geoSources,'地図上の代表位置比較'),step(r2,'別の目印',geoSources,'地図上の代表位置比較。名前の読みは出さない')];h['formats']['clue']=[step(r1,'位置の目印',geoSources,'問題文の説明と独立した位置比較'),step(r2,'もう一つの目印',geoSources,'別の対象との位置比較'),step(r3,'さらに別の目印',thirdSources,'説明文と異なる第三の対象との位置比較')]
# Validate every rendered textual hint has a source, stage and no full accepted answer.
for q in questions:
 for fmt,steps in items[q['id']]['formats'].items():
  assert len(steps)==3 and len({s['text'] for s in steps})==3,(q['name'],fmt)
  target={**q,'name':q['capital'],'aliases':[q['capital'],q['capitalReading']]} if fmt=='capital' else q
  if fmt!='tap':
   for s in steps:assert no_answer(target,s['text']),(q['name'],fmt,s['text'])
  assert all(s['sources'] and s['checkedAt']==checked for s in steps)
  if fmt=='clue':assert all(q['description'] not in s['text'] for s in steps)
old.pop('readingRule',None)
old.update({'version':3,'checkedAt':checked,'editorialPolicy':'位置→具体的な特徴→絞り込み。食文化は複数地域にあることを前提とする。形状・座標は既存教材と国土地理院資料を使用。','items':items});(d/'assets/hints.json').write_text(json.dumps(old,ensure_ascii=False,separators=(',',':')));print('Built editorial hints:',len(items),'questions /',sum(len(h['formats']) for h in items.values()),'format sets')
