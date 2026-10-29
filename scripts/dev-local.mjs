// Local-only HTTP + in-memory SQLite adapter. Never connects to production D1.
import http from 'node:http';import fs from 'node:fs';import {localDB} from '../server/db-local.mjs';import worker from '../dist/server/index.js';import {localRequest} from './local-http.mjs';
const {DB,sqlite}=localDB(),port=Number(process.env.PORT||4173),host=process.env.JAPAN_GEOGRAPHY_HOST||(process.env.SITES_MANAGED_LINUX_CONTAINER==='1'?'0.0.0.0':'127.0.0.1');
if(!Number.isInteger(port)||port<1||port>65535)throw Error('PORT must be a valid local port');
const server=http.createServer(async(req,res)=>{try{
 const authority=req.headers.host||`localhost:${port}`;const url=new URL(req.url,`http://${authority}`);
 if(!['localhost','127.0.0.1','[::1]','terminal.local'].includes(url.hostname)){res.writeHead(403);res.end('Local preview only');return;}
 if(req.url==='/__qa_hints'){res.writeHead(200,{'Content-Type':'text/html; charset=utf-8'});res.end(fs.readFileSync(new URL('../tests/browser/hint-viewport.html',import.meta.url)));return;}
 const parts=[];for await(const part of req)parts.push(part);
 const request=localRequest(req,['GET','HEAD'].includes(req.method)?undefined:Buffer.concat(parts));
 const out=await worker.fetch(request,{DB});res.writeHead(out.status,Object.fromEntries(out.headers));res.end(Buffer.from(await out.arrayBuffer()));
 }catch{res.writeHead(500,{'Content-Type':'text/plain; charset=utf-8'});res.end('ローカルプレビューでエラーが発生しました。npm run buildの実行結果を確認してください。');}});
server.listen(port,host,()=>console.log(`日本地理マスター: http://localhost:${port}/\nランキングのDBはローカルのメモリー内だけです。終了すると公式挑戦のテストデータは消えます。`));
for(const signal of ['SIGINT','SIGTERM'])process.on(signal,()=>server.close(()=>{sqlite.close();process.exit(0)}));
