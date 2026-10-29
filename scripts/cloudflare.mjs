// Keep CLI state in the ignored local directory; inherit proxy authentication and CA trust.
import {spawnSync} from 'node:child_process';
import {mkdirSync,readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
const root=fileURLToPath(new URL('../',import.meta.url));
const args=process.argv.slice(2);
const config=JSON.parse(readFileSync(path.join(root,'wrangler.jsonc'),'utf8'));
const publishes=args[0]==='deploy'&&!args.includes('--dry-run');
if((publishes||args.includes('--remote'))&&config.d1_databases.some(db=>db.database_id==='00000000-0000-0000-0000-000000000000')){
 console.error('Cloudflare D1の作成後、wrangler.jsoncのdatabase_idを設定してください。docs/CLOUDFLARE.md を参照。');process.exit(1);
}
const local=path.join(root,'.local','cloudflare');mkdirSync(local,{recursive:true});
const result=spawnSync(process.execPath,[path.join(root,'node_modules','wrangler','bin','wrangler.js'),...args],{cwd:root,stdio:'inherit',env:{...process.env,WRANGLER_SEND_METRICS:'false',XDG_CONFIG_HOME:path.join(local,'config'),XDG_CACHE_HOME:path.join(local,'cache'),WRANGLER_LOG_PATH:path.join(local,'logs')}});
if(result.error)console.error(result.error.message);
process.exit(result.status??1);
