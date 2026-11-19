// Auto update (apply at next launch) + auto offline-material download.
// Drives app functions with stubbed SW registration/worker messages.
const {JSDOM}=require('jsdom');const fs=require('fs'),assert=require('assert');const root=require('path').resolve(__dirname,'../dist')+'/';const KEY='japan-geography-master-v1',APPLY=KEY+'-apply-update-v1';const sleep=(ms=30)=>new Promise(r=>setTimeout(r,ms));
async function boot(saved){const dom=new JSDOM(fs.readFileSync(root+'index.html'),{url:'https://test.local/',runScripts:'outside-only'}),w=dom.window;Object.defineProperty(w,'crypto',{value:require('crypto').webcrypto});w.TextEncoder=TextEncoder;w.scrollTo=()=>{};w.confirm=()=>true;w.HTMLDialogElement.prototype.showModal=function(){this.open=true};w.HTMLDialogElement.prototype.close=function(){this.open=false;this.dispatchEvent(new w.Event('close'))};w.SVGElement.prototype.getBBox=()=>({x:300,y:250,width:30,height:40});w.SVGElement.prototype.setPointerCapture=()=>{};w.URL.createObjectURL=()=>'blob:test';w.URL.revokeObjectURL=()=>{};w.HTMLAnchorElement.prototype.click=()=>{};w.fetch=async p=>({ok:true,json:async()=>JSON.parse(fs.readFileSync(root+p))});Object.defineProperty(w.navigator,'serviceWorker',{value:{addEventListener(){},controller:null,getRegistration:async()=>undefined,register:async()=>{throw Error('no-sw')}}});w.localStorage.setItem(KEY,JSON.stringify(saved));w.eval(fs.readFileSync(root+'online.js','utf8')+'\n'+fs.readFileSync(root+'security.js','utf8')+'\n'+fs.readFileSync(root+'handwriting.js','utf8')+'\n'+fs.readFileSync(root+'app.js','utf8')+';window.e=s=>eval(s)');await sleep(60);const e=s=>w.e(s),$=s=>w.document.querySelector(s);return {dom,w,e,$}}
const base={version:1,current:'default',players:[{id:'default',name:'児童A',icon:'🌱',records:{},sessions:[],resume:null}],settings:{sound:false,reduce:false,strict:false}};
(async()=>{
 const {dom,w,e,$}=await boot(base);
 // A waiting worker raises the apply-at-next-launch flag and an informational notice.
 e("window.__posted=[];swRegistration={waiting:{postMessage(m){window.__posted.push(m.type)}},active:{}}");
 e("view='home'");e('updateNotice()');
 assert.equal(w.localStorage.getItem(APPLY),'1');
 assert($('#appUpdateNotice')&&$('#appUpdateNotice').textContent.includes('次回起動時に自動で更新されます'));
 assert.equal($('#applyNewVersion').textContent,'今すぐ更新');
 // Next launch with a single tab: applies once and consumes the flag.
 e("workerMessage=async()=>({count:1})");await e('autoApplyUpdate(swRegistration)');
 assert.deepEqual(e('window.__posted'),['APPLY_UPDATE']);assert.equal(e('updateRequested'),true);
 assert.equal(w.localStorage.getItem(APPLY),null,'flag is consumed before applying');
 // Multiple tabs: defer and keep the flag for the following launch.
 e("window.__posted=[];updateRequested=false");w.localStorage.setItem(APPLY,'1');
 e("workerMessage=async()=>({count:3})");await e('autoApplyUpdate(swRegistration)');
 assert.deepEqual(e('window.__posted'),[]);assert.equal(e('updateRequested'),false);
 assert.equal(w.localStorage.getItem(APPLY),'1','deferred apply keeps the flag');
 // No flag: nothing happens.
 w.localStorage.removeItem(APPLY);e("workerMessage=async()=>({count:1})");await e('autoApplyUpdate(swRegistration)');
 assert.deepEqual(e('window.__posted'),[]);
 // Offline materials: a failed check while online repairs itself automatically, once.
 e("window.__calls=[];window.__queue=[{ready:false,version:APP_RELEASE},{ready:true,version:APP_RELEASE}];workerMessage=async(w2,type)=>{window.__calls.push(type);return window.__queue.shift()};swRegistration={active:{},waiting:null}");
 await e('checkOffline()');
 assert.deepEqual(e('window.__calls'),['CHECK_OFFLINE','PREPARE_OFFLINE']);assert.equal(e('offlineInfo.ready'),true);
 // A second failing check in the same session does not download again...
 e("window.__calls=[];window.__queue=[{ready:false,version:APP_RELEASE}]");await e('checkOffline()');
 assert.deepEqual(e('window.__calls'),['CHECK_OFFLINE']);
 // ...but the manual retry still repairs.
 e("window.__calls=[];window.__queue=[{ready:false,version:APP_RELEASE},{ready:true,version:APP_RELEASE}]");await e('checkOffline(true)');
 assert.deepEqual(e('window.__calls'),['CHECK_OFFLINE','PREPARE_OFFLINE']);
 // A waiting newer version is never "repaired" into the old cache; it points at auto update.
 e("autoPrepareDone=false;window.__calls=[];window.__queue=[{ready:false,version:'other-release'}]");await e('checkOffline()');
 assert.deepEqual(e('window.__calls'),['CHECK_OFFLINE']);assert(e('offlineInfo.message').includes('次回起動時に自動で更新されます'));
 dom.window.close();
 console.log('PASS auto update/materials: waiting worker sets next-launch flag, single-tab startup applies once, multi-tab defers, online check auto-repairs materials once per session, manual retry intact.');
})().catch(e=>{console.error(e);process.exit(1)});
