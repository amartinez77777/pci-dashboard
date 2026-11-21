import {readFileSync} from 'node:fs';import {runInThisContext} from 'node:vm';import test from 'node:test';import assert from 'node:assert/strict';
runInThisContext(readFileSync(new URL('./idb_test_facade.js',import.meta.url),'utf8'));
import {actualCounts,recordsTimeline,safeArchiveSearch,explicitLinks,deterministicNext,latestAcademyRun,INTELLIGENCE_STORES} from '../dist-static/assets/personal-intelligence-model.js';
import {loadPersonalSnapshot,saveArchiveReflection,removeArchiveReflection,undoRemoveArchiveReflection,loadSuggestionPreference,saveSuggestionPreference} from '../dist-static/assets/personal-intelligence-repo.js';
import {listRecords,newRecord,putRecord,exportPrivate,importPrivate,DB_NAME,DB_VERSION,STORES} from '../dist-static/assets/storage.js';
import {newProgramState} from '../dist-static/assets/academy-model.js';
const curriculum=JSON.parse(readFileSync(new URL('../public/data/curriculum.json',import.meta.url),'utf8'));
let goal,experiment,scene,session,practice,run,note;
test('new user returns true zero totals, no invented suggestions/history',async()=>{
 const s=await loadPersonalSnapshot(),c=actualCounts(s);assert.equal(Object.values(c).every(v=>v===0),true);assert.equal(recordsTimeline(s,curriculum).length,0);
 assert.equal(deterministicNext(s).route,'feedback');assert.equal(latestAcademyRun(s),undefined);
 assert.equal(DB_NAME,'pci-private-v1');assert.equal(DB_VERSION,2);assert.equal(STORES.length,25);assert.equal(new Set(INTELLIGENCE_STORES).size,INTELLIGENCE_STORES.length);
});
test('synthetic explicit goal→experiment, scene→session, and authored lesson→practice links',async()=>{
 goal=newRecord('goals',{feedback_contract_version:'1.0.0',title:'Synthetic goal',next_action:'Observe 1 attempt',concept_id:'PCI-C-CH01-001'},['PCI-C-CH01-001']);
 experiment=newRecord('experiments',{feedback_contract_version:'1.0.0',goal_id:goal.id,status:'planned'},[goal.id]);
 scene=newRecord('rehearsals',{title:'Synthetic scene'},['PCI-RH-001']);
 session=newRecord('rehearsal_sessions',{scene_id:scene.id,template_id:'PCI-RH-001',status:'completed',completed_at:'2026-11-20T10:00:00.000Z'},[scene.id]);
 practice=newRecord('practice_sessions',{conditioning_contract_version:'1.0.0',protocol_id:'PCI-COND-001',status:'completed'},[curriculum.days[0].primary_activity_id]);
 const state=newProgramState('synthetic-run','2026-11-20T09:00:00.000Z','America/Los_Angeles');state.history=[{day_id:'PCI-DAY-01',day_number:1,result:'completed',mode:'short',at:'2026-11-20T09:00:00.000Z'}];state.day_number=2;
 run=newRecord('program_progress',{academy_contract:'1.0.0',program_id:'PCI-PROG-021',state},['PCI-PROG-021']);
 for(const r of [goal,experiment,scene,session,practice,run])await putRecord(r);
 const s=await loadPersonalSnapshot(),links=explicitLinks(s,curriculum),c=actualCounts(s);
 assert.equal(c.goals,1);assert.equal(c.experiments,1);assert.equal(c.observed,0);assert.equal(c.rehearsals,1);assert.equal(c.conditioning,1);assert.equal(c.academyDays,1);
 assert.equal(links.filter(l=>l.kind==='goal_experiment'&&l.to_id===experiment.id).length,1);
 assert.equal(links.filter(l=>l.kind==='scene_session'&&l.to_id===session.id).length,1);
 assert.equal(links.filter(l=>l.kind==='lesson_practice'&&l.to_id===practice.id).length,1);
 assert.equal(deterministicNext(s).route,'academy');assert.equal(deterministicNext(s).label,'Continue Academy Day 2');
 assert.equal(recordsTimeline(s,curriculum).filter(x=>x.kind==='academy')[0].id,run.id+'@PCI-DAY-01');
});
test('saved prediction and actual observation counted separately, no false efficacy score',async()=>{
 const prediction=newRecord('predicted_outcomes',{feedback_contract_version:'1.0.0',experiment_id:experiment.id,prediction:'Synthetic expectation'},[experiment.id]);
 const observed=newRecord('observed_outcomes',{feedback_contract_version:'1.0.0',experiment_id:experiment.id,observed:'Synthetic result'},[experiment.id]);
 await putRecord(prediction);await putRecord(observed);
 const s=await loadPersonalSnapshot(),c=actualCounts(s);assert.equal(c.experiments,1);assert.equal(c.observed,1);assert.equal('growth_score' in c,false);
 assert.equal(explicitLinks(s,curriculum).filter(l=>l.kind==='goal_experiment').length,1);
});
test('archive local creation, meaningful edit history, deletion with undo and export/import',async()=>{
 note=await saveArchiveReflection({title:'User-authored synthetic title',text:'First version',tags:'work, practice',sensitive:false,consented:false});
 assert.equal(note.store,'journal_entries');assert.equal(note.owner,'user');assert.equal(note.privacy_mode,'device_local');
 let s=await loadPersonalSnapshot(),timeline=recordsTimeline(s,curriculum);
 assert.equal(safeArchiveSearch(timeline,'practice','notes').filter(x=>x.id===note.id).length,1);
 assert.equal(safeArchiveSearch(timeline,'First version','notes').filter(x=>x.id===note.id).length,0,'searches title/tags, not private body');
 note=await saveArchiveReflection({title:'Edited synthetic title',text:'Second version',tags:'observation',sensitive:false,consented:false},note);
 assert.equal(note.data.revision_history.length,1);assert.equal(note.data.revision_history[0].text,'First version');
 assert.equal((await listRecords('journal_entries')).find(x=>x.id===note.id).data.text,'Second version');
 const exported=await exportPrivate();assert.equal(exported.format,'PCI_PRIVATE_EXPORT');assert.equal((await importPrivate(exported)).skipped>0,true);
 const removed=await removeArchiveReflection(note.id);assert.equal((await listRecords('journal_entries')).some(x=>x.id===note.id),false);
 await undoRemoveArchiveReflection(removed);assert.equal((await listRecords('journal_entries')).some(x=>x.id===note.id),true);
});
test('sensitive entries default hidden in searches, redacted in export and require explicit consent',async()=>{
 await assert.rejects(()=>saveArchiveReflection({title:'Sensitive case',text:'Do not disclose',tags:'confidential',sensitive:true,consented:false}),/consent/i);
 const sensitive=await saveArchiveReflection({title:'Sensitive case',text:'Do not disclose',tags:'confidential',sensitive:true,consented:true});
 const s=await loadPersonalSnapshot(),all=recordsTimeline(s,curriculum);
 assert.equal(safeArchiveSearch(all,'Sensitive case','notes').some(x=>x.id===sensitive.id),false);
 assert.equal(safeArchiveSearch(all,'Sensitive case','notes',true).some(x=>x.id===sensitive.id),true);
 const bundle=await exportPrivate();assert.equal(JSON.stringify(bundle).includes('Do not disclose'),false);
 assert.equal(JSON.stringify(bundle).includes('Edited synthetic title'),true);
});
test('suggestion preference is explicit, saved and user-disableable',async()=>{
 let p=await loadSuggestionPreference();assert.equal(p.enabled,true);
 const rec=await saveSuggestionPreference(false);p=await loadSuggestionPreference();assert.equal(p.enabled,false);assert.equal(p.record.id,rec.id);
 const update=await saveSuggestionPreference(true,p.record);assert.equal(update.id,rec.id);assert.equal((await loadSuggestionPreference()).enabled,true);
});
test('source assets and 10 module route keys remain present; no private fixture in public directory',()=>{
 const app=readFileSync(new URL('../src/app.tsx',import.meta.url),'utf8');for(const slug of ['command-center','self-image','beliefs','theater','feedback','conditioning','scenarios','knowledge','academy','archive'])assert.ok(app.includes(`slug:'${slug}'`));
 for(const str of ['PersonalCommandCenter','PersonalEvolutionArchive','canNavigateRoute','handleBeforeUnload','exportPrivate','importPrivate'])assert.ok(app.includes(str));
 const index=readFileSync(new URL('../index.html',import.meta.url),'utf8');assert.ok(index.includes('personal-intelligence.css'));
 const pub=readFileSync(new URL('../public/data/curriculum.json',import.meta.url),'utf8');assert.equal(pub.includes('Synthetic goal'),false);assert.equal(JSON.parse(pub).days.length,21);
});
