import { rankingRequest } from './ranking.mjs';
import { legacyRankingRequest } from './ranking-legacy.mjs';
const digest=async s=>Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(s))),v=>v.toString(16).padStart(2,'0')).join('');
export async function handleRanking(request,DB,bank){
 const url=new URL(request.url),action=url.pathname.split('/').pop();
 if(!DB)return Response.json({error:'ランキングを準備できません。端末内学習は使えます。'},{status:503});
 if(request.method==='GET'&&action==='legacy')return legacyRankingRequest(request,'leaderboard',DB,bank,'public-view');
 const token=request.headers.get('Cookie')?.match(/(?:^|;\s*)japan_rank=([a-f0-9]{64})(?:;|$)/)?.[1];let owner=null;
 if(token){const hash=await digest(token);if(await DB.prepare('SELECT token_hash FROM online_actors WHERE token_hash=?').bind(hash).first())owner=hash;}
 if(request.method==='POST'&&request.headers.get('Origin')!==url.origin)return Response.json({error:'同じサイトから操作してください。'},{status:403});
 if(action==='identity'){
  if(request.method!=='POST')return new Response('Method not allowed',{status:405});
  if(owner)return Response.json({ready:true});
  const ip=await digest(request.headers.get('CF-Connecting-IP')||'local-preview'),n=await DB.prepare('SELECT COUNT(*) AS n FROM online_actors WHERE ip_hash=? AND created>?').bind(ip,Date.now()-3600000).first();
  if(n.n>=30)return Response.json({error:'参加登録の回数が上限です。1時間後に再試行してください。'},{status:429});
  const secret=Array.from(crypto.getRandomValues(new Uint8Array(32)),x=>x.toString(16).padStart(2,'0')).join('');
  await DB.prepare('INSERT INTO online_actors(token_hash,ip_hash,created) VALUES(?,?,?)').bind(await digest(secret),ip,Date.now()).run();
  return Response.json({ready:true},{headers:{'Set-Cookie':`japan_rank=${secret}; HttpOnly; Secure; SameSite=Strict; Path=/api/rank; Max-Age=31536000`,'Cache-Control':'no-store'}});
 }
 if(action==='participant'){
  if(!owner)return Response.json({error:'参加を確認できません。もう一度開いてください。'},{status:401});
  if(request.method!=='POST')return new Response('Method not allowed',{status:405});
  const n=await DB.prepare('SELECT COUNT(*) AS n FROM online_players WHERE owner_id=?').bind(owner).first();
  if(n.n>=500)return Response.json({error:'この端末の参加登録は500人までです。'},{status:429});
  const id=crypto.randomUUID(),key=Array.from(crypto.getRandomValues(new Uint8Array(32)),x=>x.toString(16).padStart(2,'0')).join('');
  await DB.prepare('INSERT INTO online_players(id,owner_id,secret_hash,created) VALUES(?,?,?,?)').bind(id,owner,await digest(key),Date.now()).run();
  return Response.json({id,key},{headers:{'Cache-Control':'no-store'}});
 }
 const id=request.headers.get('X-JG-Player'),key=request.headers.get('X-JG-Key');let uid=null;
 if(id||key){
  if(!owner||! /^[a-f0-9-]{36}$/.test(id||'')||! /^[a-f0-9]{64}$/.test(key||''))return Response.json({error:'このプレイヤーの参加確認が必要です。'},{status:403});
  const p=await DB.prepare('SELECT * FROM online_players WHERE id=?').bind(id).first();
  if(!p||p.owner_id!==owner||p.secret_hash!==await digest(key))return Response.json({error:'このプレイヤーの参加確認ができません。先生に相談してください。'},{status:403});
  uid='player:'+id;
 }
 if(action==='leaderboard'&&request.method==='GET')return rankingRequest(request,action,DB,bank,uid||'public-view');
 if(!uid)return Response.json({error:'登録した本人で入ってから挑戦してください。'},{status:403});
 if(action==='legacy-resume'||action==='legacy-answer')return legacyRankingRequest(request,action==='legacy-resume'?'resume':'answer',DB,bank,owner);
 return rankingRequest(request,action,DB,bank,uid);
}
