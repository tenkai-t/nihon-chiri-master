// Usage-mode (school/home) integration: first-run choice, password-free home play,
// no idle lock at home, and both switch directions. Real auth stays in security suites.
const {JSDOM}=require('jsdom');const fs=require('fs'),assert=require('assert');const root=require('path').resolve(__dirname,'../dist')+'/';const KEY='japan-geography-master-v1',USAGE=KEY+'-usage-mode-v1';const sleep=(ms=30)=>new Promise(r=>setTimeout(r,ms));
async function boot(saved){const dom=new JSDOM(fs.readFileSync(root+'index.html'),{url:'https://test.local/',runScripts:'outside-only'}),w=dom.window;Object.defineProperty(w,'crypto',{value:require('crypto').webcrypto});w.TextEncoder=TextEncoder;w.scrollTo=()=>{};w.confirm=()=>true;w.HTMLDialogElement.prototype.showModal=function(){this.open=true};w.HTMLDialogElement.prototype.close=function(){this.open=false;this.dispatchEvent(new w.Event('close'))};w.SVGElement.prototype.getBBox=()=>({x:300,y:250,width:30,height:40});w.SVGElement.prototype.setPointerCapture=()=>{};w.URL.createObjectURL=()=>'blob:test';w.URL.revokeObjectURL=()=>{};w.HTMLAnchorElement.prototype.click=()=>{};w.fetch=async p=>({ok:true,json:async()=>JSON.parse(fs.readFileSync(root+p))});if(saved)w.localStorage.setItem(KEY,typeof saved==='string'?saved:JSON.stringify(saved));w.eval(fs.readFileSync(root+'online.js','utf8')+'\n'+fs.readFileSync(root+'security.js','utf8')+'\n'+fs.readFileSync(root+'handwriting.js','utf8')+'\n'+fs.readFileSync(root+'app.js','utf8')+';window.e=s=>eval(s)');await sleep(60);const e=s=>w.e(s),$=s=>w.document.querySelector(s);return {dom,w,e,$,async submit(id,expected){const f=$(id);await f.onsubmit({preventDefault(){}});await sleep(60);const msg=f.isConnected?f.querySelector('[role=status]')?.textContent:'';if(expected)assert(msg?.includes(expected),msg+' expected '+expected);else if(msg&&!msg.includes('確認・保存'))throw Error(msg);return msg},pair(id,p){$('#'+id).value=p;$('#'+id+'Again').value=p}}}
const base={version:1,current:'default',players:[{id:'default',name:'児童A',icon:'🌱',records:{},sessions:[],resume:null}],settings:{sound:false,reduce:false,strict:false}};
(async()=>{
 // Fresh device: choice screen first; pick home.
 let c=await boot(base),{w,e,$}=c;
 assert($('#usageSchool')&&$('#usageHome'),'first run must offer the usage choice');
 assert(!$('#teacherEntry'),'choice screen replaces the picker');
 $('#usageHome').click();await sleep();
 assert.equal(w.localStorage.getItem(USAGE),'home');
 assert($('#secureNewPlayer')&&$('#secureGuest'));assert(!$('#teacherEntry'),'home mode hides teacher entry');
 // Create a player with no password fields at all.
 $('#secureNewPlayer').click();await sleep();
 assert(!$('#newPassword'),'home mode must not ask for a password');
 $('#profileName').value='家族B';await c.submit('#secureProfile');
 assert.equal(e('state.players.length'),2);assert(!e('state.security?.admin')&&!Object.keys(e('state.security?.players||{}')).length,'no verifiers are created at home');
 // Pick the existing player: straight home, no login modal, no idle lock.
 $('[data-player="default"]').click();await sleep();
 assert.equal(e('view'),'home');assert(!$('#playerLogin'));
 e("start({...defaultTerrain(),content:'pref',mode:'practice',input:'type',customIds:['p2']})");
 e("answer(false,'わからない')");assert.equal(e('pstats().total'),1);
 const realNow=w.Date.now,began=realNow();w.Date.now=()=>began+360000;await new Promise(r=>setTimeout(r,1100));
 assert(!$('#childLock'),'home mode never idle-locks');w.Date.now=realNow;
 // Settings offers the switch to school; confirm it.
 e('navigate(settings)');assert($('#usageToSchool'));$('#usageToSchool').click();await sleep();
 $('#usageToSchoolConfirm').click();await sleep();
 assert.equal(w.localStorage.getItem(USAGE),'school');
 assert($('#teacherEntry'),'school mode restores teacher entry');
 assert($('#app').textContent.includes('初期設定'),'teacher setup is required next');
 c.dom.window.close();
 // Fresh device: pick school, run teacher setup, then switch to home from the teacher panel.
 c=await boot(base);({w,e,$}=c);
 $('#usageSchool').click();await sleep();
 assert.equal(w.localStorage.getItem(USAGE),'school');assert($('#teacherEntry'));
 $('#teacherEntry').click();await sleep();
 c.pair('setupPassword','654321');$('#teacherConsent').checked=true;await c.submit('#teacherSetup');
 $('#recoveryDone').click();await sleep();assert.equal(e('view'),'teacher');
 assert($('#teacherToHome'));$('#teacherToHome').click();await sleep();
 $('#teacherToHomeConfirm').click();await sleep();
 assert.equal(w.localStorage.getItem(USAGE),'home');assert(!$('#teacherEntry'));
 $('[data-player="default"]').click();await sleep();assert.equal(e('view'),'home','password stays set but home mode does not ask for it');
 c.dom.window.close();
 console.log('PASS usage mode: first-run choice, home play without passwords or idle lock, player creation without teacher setup, settings->school and teacher panel->home switches, records preserved.');
})().catch(e=>{console.error(e);process.exit(1)});
