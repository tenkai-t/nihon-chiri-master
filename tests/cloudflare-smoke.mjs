// Exercise the actual local Cloudflare Worker and D1 with synthetic data only.
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
const root=new URL(process.argv[2]||'http://127.0.0.1:8787');
assert(['127.0.0.1','localhost','[::1]'].includes(root.hostname),'This test is local-only; never send synthetic writes to production.');
const request=async(path,init={})=>fetch(new URL(path,root),{redirect:'manual',...init});
for(const path of ['/','/index.html','/?cloudflare-smoke=1']){
 const r=await request(path);assert.equal(r.status,200,path);assert(!r.headers.has('location'));assert((await r.text()).includes('releases/mixed-kana-20261030/app.js'));
}
const checksums=JSON.parse(readFileSync(new URL('../dist/releases/mixed-kana-20261030/checksums.json',import.meta.url)));
for(const [path,want]of Object.entries(checksums)){
 const r=await request('/releases/mixed-kana-20261030/'+path);assert.equal(r.status,200,path);assert.equal(createHash('sha256').update(Buffer.from(await r.arrayBuffer())).digest('hex'),want,path);
}
let r=await request('/api/rank/leaderboard?department=pref');assert.equal(r.status,200);assert(Array.isArray((await r.json()).rows));
r=await request('/api/rank/identity',{method:'POST',headers:{origin:'https://external.invalid','content-type':'application/json'},body:'{}'});assert.equal(r.status,403);
r=await request('/api/rank/identity',{method:'POST',headers:{origin:root.origin,'content-type':'application/json'},body:'{}'});assert.equal(r.status,200);const setCookie=r.headers.get('set-cookie');assert(setCookie.includes('HttpOnly'));assert(setCookie.includes('Secure'));assert(setCookie.includes('SameSite=Strict'));const cookie=setCookie.split(';')[0];
const headers={origin:root.origin,'content-type':'application/json',cookie};
r=await request('/api/rank/participant',{method:'POST',headers,body:'{}'});assert.equal(r.status,200);const participant=await r.json();assert(participant.id&&participant.key);
const playerHeaders={...headers,'X-JG-Player':participant.id,'X-JG-Key':participant.key};
const post=async(path,body)=>{const r=await request('/api/rank/'+path,{method:'POST',headers:playerHeaders,body:JSON.stringify(body)});assert.equal(r.status,200,path);return r.json()};
let run=await post('start',{department:'pref',nickname:'Cloudflare人工検証'});assert.equal(run.position,0);
for(let position=0;position<10;position++){
 const body={run:run.run,position,question:run.question.id,choice:run.question.item};
 run=await post('answer',body);assert.equal(run.position,position+1);assert.equal(run.right,position+1);
 if(position===0){const retry=await post('answer',body);assert.equal(retry.position,1);assert.equal(retry.right,1)}
}
assert(run.done);r=await request('/api/rank/leaderboard?department=pref',{headers:playerHeaders});assert.equal(r.status,200);const board=await r.json();assert.equal(board.own.right_count,10);assert.equal(board.own.nickname,'Cloudflare人工検証');assert(board.rows.some(row=>row.nickname==='Cloudflare人工検証'&&row.right===10));
console.log('PASS Cloudflare runtime + D1: nonredirecting HTML, 9 release checksums, origin guard, secure identity, participant, 10 server-graded answers, idempotent retry, saved leaderboard. Synthetic local data only.');
