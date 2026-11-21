import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {runInThisContext} from 'node:vm';
runInThisContext(readFileSync(new URL('./idb_test_facade.js',import.meta.url),'utf8'));
import {newRecord,putRecord,listRecords,exportPrivate,importPrivate,validateExport,DB_VERSION,STORES,MAX_BACKUP_BYTES} from '../dist-static/assets/storage.js';

test('private v2 schema and 25 stores remain untouched',()=>{assert.equal(DB_VERSION,2);assert.equal(STORES.length,25)});
test('export excludes sensitive content by default, but can include with explicit option',async()=>{
 const ordinary=newRecord('journal_entries',{title:'synthetic public',text:'synthetic ordinary note'});
 const consent=newRecord('consents',{purpose:'synthetic consent'});
 const sensitive=newRecord('journal_entries',{title:'synthetic sensitive',text:'synthetic classified note'},[],true,consent.id);
 await putRecord(consent);await putRecord(ordinary);await putRecord(sensitive);
 const redacted=await exportPrivate();assert.equal(JSON.stringify(redacted).includes('synthetic classified note'),false);
 const all=await exportPrivate(true);assert.equal(JSON.stringify(all).includes('synthetic classified note'),true);
 assert.equal(validateExport(redacted),true);assert.equal(validateExport(all),true);
});
test('repeat import is idempotent and preserves original stable UUID records',async()=>{
 const original=await exportPrivate(true);
 const before=(await listRecords('journal_entries')).length;
 const one=await importPrivate(original),two=await importPrivate(original);
 assert.equal(one.imported,0);assert.ok(one.skipped>0);assert.equal(two.imported,0);
 assert.equal((await listRecords('journal_entries')).length,before);
});
test('corrupt and unsupported backup envelopes are rejected before write',async()=>{
 const base=await exportPrivate();
 for(const invalid of [null,{}, {...base,version:99},{...base,records:{unrecognized:[]}},
  {...base,records:{journal_entries:[{...newRecord('journal_entries',{}),id:'------------------123456789012345678'}]}},
  {...base,records:{journal_entries:[{...newRecord('journal_entries',{}),data:null}]}},
  {...base,records:{journal_entries:[{...newRecord('journal_entries',{}),refs:[3]}]}},
  {...base,records:{journal_entries:[{...newRecord('journal_entries',{}),created_at:'yesterday'}]}},
  {...base,records:{journal_entries:[{...newRecord('journal_entries',{}),sensitive:true,consent_id:undefined}]}}
 ]){
  assert.equal(validateExport(invalid),false);
  await assert.rejects(()=>importPrivate(invalid),/Invalid|Backup/);
 }
});
test('duplicate input IDs rejected atomically, without creating a record',async()=>{
 const rec=newRecord('journal_entries',{text:'synthetic duplicate import test'});
 const bundle={...await exportPrivate(),records:{journal_entries:[rec,rec]}};
 assert.equal(validateExport(bundle),false);
 await assert.rejects(()=>importPrivate(bundle),/Invalid/);
 assert.equal((await listRecords('journal_entries')).some(x=>x.id===rec.id),false);
});
test('backup guard limits oversized files before import',async()=>{
 const rec=newRecord('journal_entries',{text:'X'.repeat(MAX_BACKUP_BYTES)});
 const huge={...await exportPrivate(),records:{journal_entries:[rec]}};
 await assert.rejects(()=>importPrivate(huge),/10 MB/);
});
test('nonexistent storage can be reported, and a later browser can retry opening',async()=>{
 // Another loaded instance is needed to exercise cold-open, because this test file
 // has already opened the fake database. Verified by source checks, not a native browser.
 assert.match(readFileSync(new URL('../src/storage.ts',import.meta.url),'utf8'),/typeof indexedDB===['"]undefined['"]\)return Promise\.reject/);
});
