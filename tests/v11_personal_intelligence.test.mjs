import {readFileSync} from 'node:fs';
import {runInThisContext} from 'node:vm';
import test from 'node:test';import assert from 'node:assert/strict';
runInThisContext(readFileSync(new URL('./idb_test_facade.js',import.meta.url),'utf8'));
import {newRecord,putRecord,listRecords,exportPrivate,importPrivate,DB_NAME,DB_VERSION,STORES} from '../dist-static/assets/storage.js';
import {personalRecommendations} from '../dist-static/assets/pci-recommendations.js';
import {loadPersonalSnapshot} from '../dist-static/assets/personal-intelligence-repo.js';
import {actualCounts,explicitLinks,recordsTimeline} from '../dist-static/assets/personal-intelligence-model.js';
import {newProgramState} from '../dist-static/assets/academy-model.js';
import {CONDITIONING_PROTOCOLS} from '../dist-static/assets/conditioning-model.js';
const curriculum=JSON.parse(readFileSync(new URL('../public/data/curriculum.json',import.meta.url),'utf8'));
const now='2026-11-20T21:00:00.000Z';const mk=(store,data,refs=[])=>newRecord(store,data,refs);
const has=(rs,code)=>rs.some(r=>r.reason_code===code);
const a=(s)=>personalRecommendations(s,now);
let goal,bel,scene,sess,exp,obs,academy,practice;
test('empty account: two real onboarding choices, no synthetic self-scoring',async()=>{
 const s=await loadPersonalSnapshot(),out=a(s);
 assert.equal(out[0].reason_code,'START_WITH_GOAL');assert.equal(out[0].route,'feedback');
 assert.equal(out[1].route,'knowledge');assert.equal(actualCounts(s).goals,0);
 assert.equal(out.every(r=>!('personality_score'in r)&&!('confidence_score'in r)),true);
 assert.equal(DB_NAME,'pci-private-v1');assert.equal(DB_VERSION,2);assert.equal(STORES.length,25);
});
test('belief -> private scene -> session: explicit UUID links persist through read',async()=>{
 bel=mk('beliefs',{statement:'Fixture hypothesis'});
 goal=mk('goals',{feedback_contract_version:'1.0.0',title:'Fixture goal',next_action:'Try one question',concept_id:'PCI-C-CH01-001'},['PCI-C-CH01-001']);
 scene=mk('rehearsals',{title:'Fixture scene',template_id:'PCI-RH-001',belief_id:bel.id,goal_id:goal.id,concept_id:'PCI-C-CH01-001'},['PCI-RH-001',bel.id,goal.id]);
 sess=mk('rehearsal_sessions',{scene_id:scene.id,template_id:'PCI-RH-001',status:'completed',completed_at:now},[scene.id]);
 for(const r of [bel,goal,scene,sess])await putRecord(r);
 const s=await loadPersonalSnapshot();const links=explicitLinks(s,curriculum);
 for(const [kind,from,to] of [['belief_scene',bel.id,scene.id],['goal_scene',goal.id,scene.id],['scene_session',scene.id,sess.id]])assert.ok(links.some(l=>l.kind===kind&&l.from_id===from&&l.to_id===to));
 assert.ok(has(a(s),'BELIEF_TO_REHEARSAL'));assert.ok(has(a(s),'REHEARSAL_FOLLOW_UP'));
 assert.equal(recordsTimeline(s,curriculum).some(x=>x.kind==='scenes'&&x.id===scene.id),true);
 assert.equal(actualCounts(s).rehearsals,1);
});
test('goal -> experiment -> observation changes recommendations without rewriting history',async()=>{
 exp=mk('experiments',{feedback_contract_version:'1.0.0',goal_id:goal.id,status:'planned',action:'Ask a question'},[goal.id]);await putRecord(exp);
 const s=await loadPersonalSnapshot();const before=a(s);
 assert.ok(has(before,'OBSERVATION_PENDING'));
 assert.equal(before.find(r=>r.reason_code==='OBSERVATION_PENDING').route,`feedback/${goal.id}/${exp.id}`);
 obs=mk('observed_outcomes',{feedback_contract_version:'1.0.0',experiment_id:exp.id,observed:'Fixture observation'},[exp.id]);await putRecord(obs);
 const changed=await loadPersonalSnapshot();assert.ok(!has(a(changed),'OBSERVATION_PENDING'));
 assert.ok(explicitLinks(changed,curriculum).some(l=>l.kind==='experiment_outcome'&&l.to_id===obs.id));
 assert.equal(actualCounts(changed).observed,1);
});
test('Academy course and missed quiz create differentiated, deterministic review routes',async()=>{
 const state=newProgramState('fixture','2026-11-20T18:00:00.000Z','UTC');state.day_number=2;state.history=[{day_id:'PCI-DAY-01',day_number:1,result:'completed',mode:'short',at:now}];
 academy=mk('program_progress',{academy_contract:'1.0.0',program_id:'PCI-PROG-021',state},['PCI-PROG-021']);await putRecord(academy);
 let s=await loadPersonalSnapshot();assert.ok(has(a(s),'RESUME_LESSON'));
 assert.equal(a(s).find(r=>r.reason_code==='RESUME_LESSON').route,'academy/day/2');
 const review=mk('review_ratings',{academy_review:true,program_run_id:academy.id,question_id:'PCI-ACA-Q01',target_day_id:'PCI-DAY-01',reason:'quiz_incorrect',status:'active',due_date:'2026-11-18'},['PCI-C-CH01-001']);await putRecord(review);
 s=await loadPersonalSnapshot();assert.equal(a(s)[0].reason_code,'REVIEW_DUE');assert.equal(a(s)[0].route,'academy/review');
 assert.match(a(s)[0].why,/comprehension/);
 await putRecord({...review,updated_at:now,data:{...review.data,status:'dismissed'}});
 assert.ok(!has(a(await loadPersonalSnapshot()),'REVIEW_DUE'));
});
test('unfinished conditioning session has explicit resume route, completed session removes it',async()=>{
 const protocol=CONDITIONING_PROTOCOLS[0];practice=mk('practice_sessions',{conditioning_contract_version:'1.0.0',protocol_id:protocol.id,status:'paused'},[protocol.id,protocol.activity_id,protocol.concept_id]);
 await putRecord(practice);let s=await loadPersonalSnapshot();assert.equal(a(s).find(r=>r.reason_code==='PRACTICE_UNFINISHED').route,`conditioning/${practice.id}`);
 await putRecord({...practice,updated_at:now,data:{...practice.data,status:'completed'}});s=await loadPersonalSnapshot();assert.ok(!has(a(s),'PRACTICE_UNFINISHED'));assert.equal(actualCounts(s).conditioning,1);
 assert.ok(explicitLinks(s,curriculum).every(l=>l.from_id&&l.to_id));
});
test('private export/import retains UUIDs and links; repeated import is idempotent',async()=>{
 const b=await exportPrivate();const copy=JSON.parse(JSON.stringify(b));const before=await loadPersonalSnapshot();
 assert.ok(JSON.stringify(copy).includes(goal.id));assert.ok(JSON.stringify(copy).includes(scene.id));
 const first=await importPrivate(copy);const second=await importPrivate(copy);
 assert.ok(first.skipped>=1&&second.skipped>=1);
 const after=await loadPersonalSnapshot();assert.equal(after.goals.filter(x=>x.id===goal.id).length,1);
 assert.equal(explicitLinks(before,curriculum).length,explicitLinks(after,curriculum).length);
});
test('sensitive data never appears in reason, title, route or public source',async()=>{
 const sensitive=newRecord('goals',{feedback_contract_version:'1.0.0',title:'PRIVATE_FIXTURE_SECRET_7712',next_action:'secret detail'},[],true,'fixture-consent');await putRecord(sensitive);
 const recs=a(await loadPersonalSnapshot());const payload=JSON.stringify(recs);
 assert.ok(!payload.includes('PRIVATE_FIXTURE_SECRET_7712'));
 assert.ok(!payload.includes('secret detail'));
 const exported=await exportPrivate();assert.ok(!JSON.stringify(exported).includes('PRIVATE_FIXTURE_SECRET_7712'));
});
test('six concept-linked Conditioning protocols retain canonical source IDs and source status',()=>{
 assert.equal(CONDITIONING_PROTOCOLS.length,6);assert.equal(new Set(CONDITIONING_PROTOCOLS.map(x=>x.id)).size,6);
 for(const p of CONDITIONING_PROTOCOLS){assert.match(p.concept_id,/^PCI-C-CH\d{2}-\d+/);assert.match(p.activity_id,/^PCI-ACT-CH\d{2}-\d+/);assert.equal(p.origin,'PCI_adaptation');}
});
test('full source contains all ten route keys and direct links to existing modules',()=>{
 const app=readFileSync(new URL('../src/app.tsx',import.meta.url),'utf8');const home=readFileSync(new URL('../src/personal-intelligence.tsx',import.meta.url),'utf8');
 for(const slug of ['command-center','self-image','beliefs','theater','feedback','conditioning','scenarios','knowledge','academy','archive'])assert.ok(app.includes(`slug:'${slug}'`),slug);
 for(const route of ['feedback/${g.id}','academy/review','knowledge/concept/','theater/goal/'])assert.ok(home.includes(route),route);
 assert.equal(JSON.stringify(curriculum.days).includes('PRIVATE_FIXTURE_SECRET_7712'),false);
});
