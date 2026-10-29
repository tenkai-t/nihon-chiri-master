// Synthetic DOM/input regression; no production data or browser profile is used.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),{JSDOM}=require('jsdom');
const root=path.resolve(__dirname,'../dist'),questions=JSON.parse(fs.readFileSync(path.join(root,'assets/questions.json')));
const dom=new JSDOM(fs.readFileSync(path.join(root,'index.html'),'utf8'),{url:'https://test.local/',runScripts:'outside-only'}),w=dom.window;
w.scrollTo=()=>{};w.confirm=()=>true;w.SVGElement.prototype.getBBox=()=>({x:300,y:250,width:30,height:40});w.HTMLDialogElement.prototype.showModal=function(){this.open=true};w.HTMLDialogElement.prototype.close=function(){this.open=false};
w.fetch=async p=>({ok:true,json:async()=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'))});
w.eval(fs.readFileSync(path.join(root,'app.js'),'utf8').replace('installPlayerProtection();','').replace('installOfficialRanking();','')+';window.evaluate=s=>eval(s)');
const e=s=>w.evaluate(s),grade=(q,s)=>e(`correct(${JSON.stringify(q)},${JSON.stringify(s)})`);
(async()=>{try{
 await new Promise(r=>setTimeout(r,100));e("choosePlayer('default')");
 const targets=questions.flatMap(q=>[q,...(q.pid?[{...q,name:q.capital,reading:q.capitalReading,aliases:[q.capital,q.capitalReading,...(q.pid===13?[]:[q.capital.slice(0,-1),q.capitalReading.slice(0,-1)])]}]:[])]);
 for(const q of targets)for(const alias of q.aliases)assert(grade(q,alias),q.name+': old alias '+alias);
 const examples=[['北海道','北かいどう'],['北海道','ほっかい道'],['北海道','ほっ海どう'],['富士山','富士さん'],['富士山','ふ士山'],['東京都','とう京と'],['神奈川県','神な川けん'],['大分県','大いた'],['鹿児島県','かご島けん'],['札幌市','札ぽろし'],['宇都宮市','宇つのみや市'],['さいたま市','さいたま市'],['琵琶湖','び琶こ'],['霞ヶ浦','かすみヶうら'],['八ヶ岳','八が岳'],['紀の川','紀のかわ'],['飛騨山脈','北あるぷす'],['長野盆地','善こう寺だいら'],['沖縄島','おき縄ほんとう'],['大雪山','だい雪ざん'],['佐渡島','さ渡がしま'],['鳥海山','鳥かいざん']];
 for(const [name,input]of examples)assert(grade(targets.find(q=>q.name===name),input),name+': '+input);
 for(const [name,input]of [['北海道','北かどう'],['北海道','北っかいどう'],['北海道','ほかい道'],['富士山','富士やま'],['富士山','ふ山'],['富士山','富士'],['神奈川県','神な山けん'],['東京都','とうきょ都'],['新宿区','新じゅく'],['琵琶湖','び琶'],['佐渡島','さ渡とう'],['沖縄島','おき縄ほんじま']])assert(!grade(targets.find(q=>q.name===name),input),name+': reject '+input);
 const rows=JSON.parse(e('JSON.stringify(mixedReadingRows)'));let variants=0;
 for(const q of targets){
  assert(rows.some(row=>row.name===q.name&&row.parts.join('')===q.reading),q.name+': canonical reading coverage');
  for(const row of rows)for(let length=1;length<=row.name.length;length++){
   const spelling=row.name.slice(0,length),parts=row.parts.slice(0,length);
   if(!q.aliases.includes(spelling)||!q.aliases.includes(parts.join('')))continue;
   for(let mask=0;mask<2**length;mask++){
    const input=[...spelling].map((c,i)=>mask&(1<<i)?parts[i]:c).join('');assert(grade(q,input),q.name+': '+input);assert(!grade(q,input+'あ'),q.name+': extra syllable');variants++;
   }
  }
  for(const other of targets)if(!q.aliases.includes(other.name))assert(!grade(q,other.name),q.name+': different place '+other.name);
 }
 e('state.settings.strict=true');for(const q of targets)for(const alias of q.aliases)assert.equal(grade(q,alias),alias===q.name,q.name+': strict '+alias);
 for(const [name,input]of examples)assert.equal(grade(targets.find(q=>q.name===name),input),input===name,name+': strict mixed');
 e('state.settings.strict=false');
 // Real form submission, IME guard, scoring, persistence and handwritten text use the same grader.
 const start=(id,input='type',format='name')=>e(`start({...defaultTerrain(),content:'mix',mode:'test10',input:'${input}',format:'${format}',level:'all',customIds:['${id}']})`);
 start('p1');const field=w.document.querySelector('#answer'),form=w.document.querySelector('#answerForm');field.value='北かいどう';field.oncompositionstart();form.dispatchEvent(new w.Event('submit',{cancelable:true}));assert.equal(e('game.answered'),false);field.oncompositionend();form.dispatchEvent(new w.Event('submit',{cancelable:true}));assert.equal(e('game.correct'),1);assert.equal(e('player().records.p1.correct'),1);assert.equal(e('player().testStats.correct'),1);assert.equal(JSON.parse(w.localStorage.getItem('japan-geography-master-v1')).players[0].records.p1.correct,1);
 start('t1','hand');w.document.querySelector('#inkText').value='富士さん';w.document.querySelector('#inkSubmit').click();assert.equal(e('game.correct'),1);
 start('p1','type','capital');w.document.querySelector('#answer').value='札ぽろ市';w.document.querySelector('#answerForm').dispatchEvent(new w.Event('submit',{cancelable:true}));assert.equal(e('game.correct'),1);
 console.log(`PASS mixed kana: ${targets.length} names/capitals, ${variants} spelling/reading combinations, old aliases, wrong readings/omissions/cross-place rejection, strict mode, IME, typed/handwritten forms and saved scoring.`);
 }finally{dom.window.close()}
})().catch(err=>{console.error(err);process.exitCode=1});
