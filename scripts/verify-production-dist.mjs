// PCI real production distribution gate. Fails closed if build output is missing,
// references unbundled source, contains historical/private artifacts, or drops book data.
// This script does not claim browser or iPhone certification.
import {readFileSync,existsSync,readdirSync,statSync} from 'node:fs';
import {join,resolve,relative,extname} from 'node:path';
import {createHash} from 'node:crypto';

const base=resolve(process.cwd());
const dist=join(base,'dist');
const fail=(msg)=>{console.error('PRODUCTION BUILD REJECTED: '+msg);process.exitCode=1};
const must=(file)=>{if(!existsSync(file)){fail('Missing '+relative(base,file));return false}return true};
const readJson=(path)=>JSON.parse(readFileSync(path,'utf8'));
const hash=(file)=>createHash('sha256').update(readFileSync(file)).digest('hex');
const list=(dir)=>!existsSync(dir)?[]:readdirSync(dir,{withFileTypes:true}).flatMap(d=>d.isDirectory()?list(join(dir,d.name)):[join(dir,d.name)]);

if(!must(join(dist,'index.html')))process.exit(1);
const html=readFileSync(join(dist,'index.html'),'utf8');
if(!/id=["']root["']/.test(html))fail('React root element absent');
if(/src=["'][^"']*src\/main\.tsx/.test(html))fail('Unbundled TypeScript source in index');
if(/offline-vendor|react16-hooks-bridge|dist-static/.test(html))fail('Compatibility-only runtime in index');
const entryScripts=[...html.matchAll(/<script\b[^>]*type=["']module["'][^>]*src=["']([^"']+)["']/gi)].map(x=>x[1]);
if(!entryScripts.length)fail('No built module script in production index');
for(const url of entryScripts){
 if(/^(?:https?:)?\/\//.test(url)){fail('External script is not self-contained: '+url);continue}
 const path=resolve(dist,url.replace(/^\.\//,''));
 if(!path.startsWith(dist+'/')||!must(path))fail('Broken built entry script: '+url);
}
const required=['styles.css','vault.css','stage12.css','conditioning.css','academy.css','personal-intelligence.css','data/research-metadata.json','data/concept-index.json','data/rehearsals.json','data/curriculum.json','data/chapter-index.json','data/practice-attribution.json'];
for(const file of required){
 const target=join(dist,file),original=join(base,'public',file);
 if(!must(target))continue;
 if(!must(original))continue;
 if(hash(target)!==hash(original))fail('Public canonical asset differs from source: '+file);
}
const files=list(dist),rel=files.map(f=>relative(dist,f).replaceAll('\\','/'));
for(const f of rel){
 if(/^(?:reference|rollbacks|audit|tests|offline-vendor|dist-static|src|node_modules|schema|third-party)\//.test(f))fail('Source/test/private directory leaked: '+f);
 if(/(?:^|\/)(?:PCI_PRIVATE_BACKUP|\.env)/i.test(f))fail('Private file leaked: '+f);
 if(/\.(?:pdf|ts|tsx|map)$/i.test(f))fail('Non-runtime source asset leaked: '+f);
}
const js=files.filter(f=>extname(f)==='.js');
if(!js.length)fail('No built JS bundles');
for(const [pkg,major] of [['react',18],['react-dom',18],['vite',5]]){
 const p=join(base,'node_modules',pkg,'package.json');
 if(!must(p))continue;
 const version=readJson(p).version;
 if(Number(version.split('.')[0])!==major)fail(`${pkg} version ${version}, expected major ${major}`);
}
if(process.exitCode){console.error('Check failed; do NOT deploy this archive');process.exit(process.exitCode)}
console.log(`PASS: Genuine React18/Vite bundle inspected (${files.length} public files, ${js.length} JS assets), ${required.length} required assets match canonical public source.`);
console.log('NOT CERTIFIED: Live iPhone Safari/VoiceOver, multi-tab collisions and full backup restore still require device testing.');
