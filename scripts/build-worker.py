from pathlib import Path
import json,hashlib,base64,gzip
r=Path(__file__).resolve().parents[1];d=r/'dist';blobs={};paths={};mime={'.js':'text/javascript','.json':'application/json','.css':'text/css','.html':'text/html','.svg':'image/svg+xml','.png':'image/png','.ico':'image/x-icon','.txt':'text/plain','.geojson':'application/geo+json'}
for p in d.rglob('*'):
 if not p.is_file() or 'server' in p.relative_to(d).parts or '.openai' in p.relative_to(d).parts:continue
 raw=p.read_bytes();key=hashlib.sha256(raw).hexdigest();blobs[key]=base64.b64encode(raw).decode();paths['/'+str(p.relative_to(d))]=[key,mime.get(p.suffix,'application/octet-stream')]
legacy=(r/'server/ranking-legacy.mjs').read_text().replace('export ','')
import re
code='const legacyRankingRequest=(()=>{'+legacy+'\nreturn legacyRankingRequest;})();\n'+(r/'server/ranking.mjs').read_text().replace('export ','')+'\n'+re.sub(r'^import .*?;\n','',(r/'server/handler.mjs').read_text(),flags=re.M).replace('export ','')
code+='\nconst bank='+ (d/'assets/questions.json').read_text()+';\nconst blobs='+json.dumps(blobs)+';\nconst paths='+json.dumps(paths)+''';
export default {async fetch(request,env){const url=new URL(request.url);if(url.pathname.startsWith('/api/rank/')){try{return await handleRanking(request,env.DB,bank)}catch{return Response.json({error:'通信に失敗しました。再試行できます。'},{status:503})}}let path=decodeURI(url.pathname);if(path==='/')path='/index.html';if(path==='/repair')path='/repair.html';const entry=paths[path];if(!entry)return new Response('Not found',{status:404});if(!['GET','HEAD'].includes(request.method))return new Response('Method not allowed',{status:405});const raw=atob(blobs[entry[0]]),body=Uint8Array.from(raw,c=>c.charCodeAt(0));return new Response(request.method==='HEAD'?null:body,{headers:{'Content-Type':entry[1]+'; charset=utf-8','Cache-Control':path.includes('/releases/')?'public,max-age=31536000,immutable':'no-cache','X-Content-Type-Options':'nosniff'}})}};
'''
(d/'server').mkdir(exist_ok=True);(d/'server/index.js').write_text(code);(d/'.openai').mkdir(exist_ok=True);(d/'.openai/hosting.json').write_text((r/'.openai/hosting.json').read_text());print('Worker build',len(paths),'paths,',len(blobs),'deduplicated blobs, gzip',len(gzip.compress(code.encode())))
