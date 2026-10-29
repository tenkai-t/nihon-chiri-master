"""Apply the reviewed 2026-10-17 additions, retaining established question IDs.
Geometry extraction parameters and source feature IDs live in expansion-additions.json;
gazetteer row evidence lives in expansion-evidence.json. This script does no network lookup.
Run build-handwriting.py with a KanjiVG checkout after changing answer characters,
then build-release.py, then npm test.
"""
from pathlib import Path
import json
root=Path(__file__).resolve().parents[1];p=root/'dist/assets/questions.json';qs=json.loads(p.read_text());add=json.loads((root/'scripts/reference/expansion-additions.json').read_text());contract=json.loads((root/'scripts/reference/pre-expansion-contract.json').read_text())
for b in contract:
 current=next(q for q in qs if q['id']==b['id'])
 assert all(current[k]==v for k,v in b.items()),'Established answer identity changed: '+b['id']
byid={q['id']:q for q in qs}
for q in add:
 assert q['id'] not in {b['id'] for b in contract}
 if q['id'] not in byid:qs.append(q)
 else:qs[qs.index(byid[q['id']])]=q
assert len(qs)==len({q['id'] for q in qs})==len({q['name'] for q in qs})
p.write_text(json.dumps(qs,ensure_ascii=False,separators=(',',':')))
print('Reviewed terrain additions applied:',len(add))
