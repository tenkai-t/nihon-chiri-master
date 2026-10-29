// Portable build adapter; does not alter the application or publish anything.
import {spawnSync} from 'node:child_process';
const candidates=process.env.JAPAN_GEOGRAPHY_PYTHON?[[process.env.JAPAN_GEOGRAPHY_PYTHON,[]]]:[['python3',[]],['python',[]],['py',['-3']]];
let python;for(const [command,args]of candidates){const p=spawnSync(command,[...args,'-c','import sys;assert sys.version_info >= (3,8)'],{stdio:'ignore'});if(p.status===0){python=[command,args];break;}}
if(!python){console.error('Python 3.8以上が必要です。WindowsではPythonをPATHへ追加するか、JAPAN_GEOGRAPHY_PYTHONを設定してください。');process.exit(1);}
for(const script of ['scripts/build-release.py','scripts/build-worker.py']){const r=spawnSync(python[0],[...python[1],script],{stdio:'inherit',env:{...process.env,PYTHONUTF8:'1'}});if(r.status!==0)process.exit(r.status||1);}
