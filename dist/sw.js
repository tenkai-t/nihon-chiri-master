'use strict';
const RELEASE='nihon-chiri-v15-inline-hints';
// Cache the canonical directory URL. /index.html redirects to / on this host.
const FILES=['releases/inline-hints-20261024/checksums.json','./','bootstrap.js','releases/inline-hints-20261024/style.css','releases/inline-hints-20261024/app.js','releases/inline-hints-20261024/security.js','releases/inline-hints-20261024/online.js','releases/inline-hints-20261024/handwriting.js','releases/inline-hints-20261024/assets/japan.geojson','releases/inline-hints-20261024/assets/questions.json','releases/inline-hints-20261024/assets/handwriting.json','releases/inline-hints-20261024/assets/hints.json','licenses/KanjiVG-CC-BY-SA-3.0.txt','manifest.json','icon.svg','icon-192.png','icon-512.png','apple-touch-icon.png','favicon.ico','icons/atlas-v7/normal.svg','icons/atlas-v7/maskable.svg','icons/atlas-v7/favicon.svg','icons/atlas-v7/icon-192.png','icons/atlas-v7/icon-512.png','icons/atlas-v7/maskable-192.png','icons/atlas-v7/maskable-512.png','icons/atlas-v7/apple-touch-icon.png','icons/atlas-v7/favicon-16.png','icons/atlas-v7/favicon-32.png','icons/atlas-v7/favicon.ico'];
const absolute=p=>new URL(p,self.registration.scope).href;
async function cleanResponse(response){
 if(!response||!response.ok||response.type==='opaque'||response.type==='opaqueredirect')throw Error('Unreadable response');
 if(response.url&&new URL(response.url).origin!==self.location.origin)throw Error('Cross-origin response');
 const headers=new Headers(response.headers);
 for(const name of ['location','content-encoding','content-length','transfer-encoding'])headers.delete(name);
 // A fresh Response has no redirect history. Safari rejects redirected cached navigation responses.
 return new Response(await response.arrayBuffer(),{status:response.status,statusText:response.statusText,headers});
}
async function download(path){const response=await fetch(absolute(path),{credentials:'same-origin',redirect:'follow',cache:'reload'});const clean=await cleanResponse(response);if(path==='./'&&!(await clean.clone().text()).includes('releases/inline-hints-20261024/app.js'))throw Error('Not the game document');return clean;}
async function verify(cache){const missing=[];for(const path of FILES)if(!await cache.match(absolute(path)))missing.push(path);if(missing.length)return {ready:false,version:RELEASE,missing};const sums=await(await cache.match(absolute('releases/inline-hints-20261024/checksums.json'))).json();if(typeof crypto!=='undefined'&&crypto.subtle){for(const [file,want]of Object.entries(sums)){const path='releases/inline-hints-20261024/'+file,r=await cache.match(absolute(path));if(!r){missing.push(path);continue}const hash=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',await r.arrayBuffer()))).map(b=>b.toString(16).padStart(2,'0')).join('');if(hash!==want)missing.push(path);}}return {ready:missing.length===0,version:RELEASE,missing}}
let preparing=null;
function prepare(){if(preparing)return preparing;preparing=(async()=>{const stageName=RELEASE+'-staging',stage=await caches.open(stageName);try{await Promise.all(FILES.map(async path=>stage.put(absolute(path),await download(path))));const result=await verify(stage);if(!result.ready)throw Error('Incomplete release');const cache=await caches.open(RELEASE);for(const path of FILES)await cache.put(absolute(path),await stage.match(absolute(path)));return result;}finally{await caches.delete(stageName)}})().finally(()=>{preparing=null});return preparing}
self.addEventListener('install',e=>{e.waitUntil(prepare())});
self.addEventListener('activate',e=>{e.waitUntil(self.clients.claim())});
self.addEventListener('message',e=>{if(e.data?.type==='APPLY_UPDATE')self.skipWaiting();if(['CHECK_OFFLINE','PREPARE_OFFLINE'].includes(e.data?.type))e.waitUntil((async()=>{let result;try{if(e.data.type==='PREPARE_OFFLINE')await prepare();result=await verify(await caches.open(RELEASE));}catch(error){result={ready:false,version:RELEASE,error:'prepare-failed'}}e.ports[0]?.postMessage(result)})())});
self.addEventListener('fetch',e=>{const req=e.request,url=new URL(req.url),scope=new URL(self.registration.scope);if(req.method!=='GET'||url.origin!==self.location.origin)return;
 // Recovery and platform sign-in routes must be handled by the network, never the cached game shell.
 if(req.mode==='navigate'){
  if(![scope.pathname,scope.pathname+'index.html'].includes(url.pathname))return;
  e.respondWith((async()=>{const cache=await caches.open(RELEASE),cached=await cache.match(absolute('./'));if(cached)return cleanResponse(cached);try{const clean=await download('./');await cache.put(absolute('./'),clean.clone());return clean;}catch(error){return new Response('<!doctype html><meta charset="utf-8"><title>通信を確認してください</title><p>通信を確認して、もう一度開いてください。</p><a href="repair.html">起動を修復する</a>',{status:503,headers:{'Content-Type':'text/html; charset=utf-8'}});}})());return;
 }
 const path=FILES.find(p=>new URL(p,self.registration.scope).pathname===url.pathname);if(!path)return;
 e.respondWith((async()=>{const cache=await caches.open(RELEASE),cached=await cache.match(absolute(path));if(cached)return cleanResponse(cached);return download(path);})());
});
