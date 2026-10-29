"""Derive compact stroke templates from KanjiVG SVG (CC BY-SA 3.0).
Usage: python scripts/build-handwriting.py /path/to/kanjivg
"""
import json,sys,math,xml.etree.ElementTree as ET
from pathlib import Path
from fontTools.svgLib.path import parse_path
from fontTools.pens.basePen import BasePen
class Sampler(BasePen):
 def __init__(self):super().__init__(None);self.points=[];self.cur=None
 def _moveTo(self,p):self.cur=p;self.points.append(p)
 def _lineTo(self,p):
  a=self.cur
  for i in range(1,17):self.points.append((a[0]+(p[0]-a[0])*i/16,a[1]+(p[1]-a[1])*i/16))
  self.cur=p
 def _curveToOne(self,b,c,d):
  a=self.cur
  for i in range(1,49):
   t=i/48;u=1-t;self.points.append(tuple(u*u*u*a[j]+3*u*u*t*b[j]+3*u*t*t*c[j]+t*t*t*d[j] for j in [0,1]))
  self.cur=d
 def _qCurveToOne(self,b,c):
  a=self.cur
  for i in range(1,49):
   t=i/48;u=1-t;self.points.append(tuple(u*u*a[j]+2*u*t*b[j]+t*t*c[j] for j in [0,1]))
  self.cur=c
 def _closePath(self):pass
 def _endPath(self):pass
def resample(ps,n=16):
 lens=[0]
 for a,b in zip(ps,ps[1:]):lens.append(lens[-1]+math.dist(a,b))
 if lens[-1]<1e-6:return [ps[0]]*n
 out=[];k=1
 for i in range(n):
  d=lens[-1]*i/(n-1)
  while k<len(ps)-1 and lens[k]<d:k+=1
  r=(d-lens[k-1])/(lens[k]-lens[k-1]) if lens[k]>lens[k-1] else 0
  out.append(tuple(ps[k-1][j]+r*(ps[k][j]-ps[k-1][j]) for j in [0,1]))
 return out
base=Path(sys.argv[1]);qs=json.load(open('dist/assets/questions.json'));chars=set('ー')
for q in qs:
 for key in ['name','reading','capital','capitalReading']:
  chars.update(q.get(key,''))
 for a in q.get('aliases',[]):chars.update(a)
chars.update(chr(c) for c in range(0x3041,0x3097));chars.update(chr(c) for c in range(0x30a1,0x30fb))
out={};missing=[]
for c in sorted(chars):
 f=base/'kanji'/f'{ord(c):05x}.svg'
 if not f.exists():missing.append(c);continue
 tree=ET.parse(f);ss=[]
 for path in tree.findall('.//{http://www.w3.org/2000/svg}path'):
  pen=Sampler();parse_path(path.attrib['d'],pen)
  if pen.points:ss.append(resample(pen.points))
 if not ss:continue
 xs=[p[0] for st in ss for p in st];ys=[p[1] for st in ss for p in st];xmin,xmax,ymin,ymax=min(xs),max(xs),min(ys),max(ys);size=max(xmax-xmin,ymax-ymin,1);cx=(xmin+xmax)/2;cy=(ymin+ymax)/2
 out[c]=[[[round((x-cx)/size*240+128),round((y-cy)/size*240+128)] for x,y in st] for st in ss]
meta={'version':1,'samples':16,'source':'https://github.com/KanjiVG/kanjivg','copyright':'Ulrich Apel and the KanjiVG contributors','license':'CC BY-SA 3.0','licenseUrl':'https://creativecommons.org/licenses/by-sa/3.0/','modification':'Selected characters, paths sampled at 16 points per stroke, normalized to 256-unit coordinates.','characters':out,'missing':missing}
Path('dist/assets/handwriting.json').write_text(json.dumps(meta,ensure_ascii=False,separators=(',',':')));Path('dist/licenses/KanjiVG-CC-BY-SA-3.0.txt').write_text((base/'COPYING').read_text());print(len(out),'characters; missing:', ''.join(missing));print('bytes',Path('dist/assets/handwriting.json').stat().st_size)
