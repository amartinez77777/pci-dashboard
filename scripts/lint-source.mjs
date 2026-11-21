import {readFileSync} from 'node:fs';
import {execFileSync} from 'node:child_process';
const files=['src/app.tsx','src/data.ts','src/storage.ts','src/main.tsx','src/vault.tsx','src/vault-data.ts','src/vault-search.ts','src/vault-storage.ts'];
let errors=[];
for(const f of files){const s=readFileSync(f,'utf8');if(/\beval\s*\(/.test(s))errors.push(f+': eval prohibited');if(/\blocalStorage\s*\./.test(s))errors.push(f+': localStorage prohibited as personal persistence');if(/console\.log\s*\(/.test(s))errors.push(f+': console logging in runtime prohibited');}
try{execFileSync('tsc',['--noEmit','-p','tsconfig.json'],{stdio:'inherit'})}catch{errors.push('TypeScript strict typecheck failed')}
if(errors.length){console.error(errors.join('\n'));process.exit(1)}console.log('PASS: lightweight safety lint and strict TypeScript typecheck. Not ESLint.');
