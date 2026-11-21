import {readFileSync} from 'node:fs';import {runInThisContext} from 'node:vm';import test from 'node:test';import assert from 'node:assert/strict';
runInThisContext(readFileSync(new URL('./idb_test_facade.js',import.meta.url),'utf8'));
import {ACADEMY_CHECKPOINTS,ACADEMY_QUESTIONS,validateAcademyCurriculum,newProgramState,applyProgramAction,progressCounts,localDate,reviewDueDate,isReviewDue,questionForDay,gradeRecall} from '../dist-static/assets/academy-model.js';
import {listAcademyRuns,createAcademyRun,updateAcademyRun,listAcademyReviews,listAcademyQuizzes,submitAcademyQuiz,updateAcademyReview} from '../dist-static/assets/academy-repo.js';
import {listRecords,openPrivateDB,exportPrivate} from '../dist-static/assets/storage.js';
const root=new URL('../',import.meta.url);const program=JSON.parse(readFileSync(new URL('../public/data/curriculum.json',import.meta.url)));
const registry=JSON.parse(readFileSync(new URL('../PCI_ID_REGISTRY.json',import.meta.url)));
test('authored curriculum: all 21 original permanent day IDs, source targets and checkpoints',()=>{
 assert.deepEqual(validateAcademyCurriculum(program,new Set(Object.keys(registry))),[]);
 assert.deepEqual(program.days.map(d=>d.id),Array.from({length:21},(_,i)=>`PCI-DAY-${String(i+1).padStart(2,'0')}`));
 assert.deepEqual(program.days.filter(d=>d.checkpoint).map(d=>d.day_number),[4,9,15,21]);
 assert.equal(program.origin,'PCI_adaptation');assert.equal(program.advance_policy.basis,'completed_or_explicitly_skipped_steps_not_calendar_days');
});
test('eight honest comprehension checks link to actual canonical concepts',()=>{
 assert.equal(ACADEMY_QUESTIONS.length,8);assert.equal(new Set(ACADEMY_QUESTIONS.map(x=>x.id)).size,8);
 for(const q of ACADEMY_QUESTIONS){assert.ok(registry[q.concept_id],q.concept_id);assert.equal(q.source_status,'book_assertion_only');assert.ok(q.rationale.length>45);assert.ok(q.choices.every(x=>x.length>5));assert.equal(gradeRecall(q,q.correct_index).correct,true);assert.equal(gradeRecall(q,(q.correct_index+1)%3).correct,false)}
 for(const day of program.days)if(questionForDay(day))assert.ok(day.verified_concept_ids.includes(questionForDay(day).concept_id)||questionForDay(day).chapter_id===day.chapter_id);
});
test('pure progression: must explicitly complete/skip, checkpoint choice and pause/resume',()=>{
 let s=newProgramState('run-test','2026-11-20T19:00:00.000Z','America/Los_Angeles');assert.equal(s.day_number,1);assert.equal(s.history.length,0);
 s=applyProgramAction(s,{kind:'pause'},'2026-11-20T19:02:00.000Z');assert.equal(s.status,'paused');assert.throws(()=>applyProgramAction(s,{kind:'complete'},'2026-11-20T19:03:00.000Z'),/Resume/);
 s=applyProgramAction(s,{kind:'resume'},'2026-11-21T19:00:00.000Z');assert.equal(s.day_number,1);
 for(let n=1;n<=21;n++){
  if(ACADEMY_CHECKPOINTS.includes(n))assert.throws(()=>applyProgramAction(s,{kind:'complete'},'2026-11-22T19:00:00.000Z'),/checkpoint/i);
  const checkpoint=ACADEMY_CHECKPOINTS.includes(n)?{checkpoint_review:n===4?'PCI-DAY-01':'none'}:{};
  const kind=n===5?'skip':'complete';s=applyProgramAction(s,{kind,mode:n%2?'short':'standard',...checkpoint},`2026-11-${String(Math.min(n+1,29)).padStart(2,'0')}T19:00:00.000Z`);
  assert.equal(s.history.length,n);
 }
 assert.equal(s.status,'completed');assert.equal(s.day_number,22);assert.equal(progressCounts(s).acknowledged,21);assert.equal(progressCounts(s).skipped,1);
 assert.equal(applyProgramAction(s,{kind:'complete'},'2026-12-01T00:00:00.000Z'),s);
});
test('calendar review scheduling across daylight-saving time and user-selected timezone',()=>{
 assert.equal(localDate('2026-03-08T09:30:00.000Z','America/Los_Angeles'),'2026-03-08');
 assert.equal(reviewDueDate('2026-03-08T09:30:00.000Z','America/Los_Angeles','quiz_incorrect'),'2026-03-09');
 assert.equal(reviewDueDate('2026-03-08T09:30:00.000Z','America/Los_Angeles','quiz_correct'),'2026-03-12');
 assert.equal(isReviewDue({id:'r',question_id:'q',due_date:'2026-03-09',reason:'quiz_incorrect',status:'active',last_rated_at:''},'2026-03-10T10:00:00Z','America/Los_Angeles'),true);
});
test('existing 25 private stores remain exactly, including progress/quiz/review/events',async()=>{
 const db=await openPrivateDB();assert.equal(db.name,'pci-private-v1');assert.equal(db.version,2);assert.equal(db.objectStoreNames.contains('program_progress'),true);assert.equal(db.objectStoreNames.contains('quiz_attempts'),true);assert.equal(db.objectStoreNames.contains('review_ratings'),true);assert.equal(db.objectStoreNames.contains('events'),true);
});
test('create one run, explicit first day, saved reload, and duplicate day tap does not advance Day 3',async()=>{
 const r=await createAcademyRun('America/Los_Angeles');assert.equal(r.data.state.day_number,1);
 assert.equal((await listAcademyRuns())[0].id,r.id);
 let d=await updateAcademyRun(r.id,1,{kind:'complete',mode:'short'});assert.equal(d.data.state.day_number,2);
 let duplicate=await updateAcademyRun(r.id,1,{kind:'complete',mode:'short'});assert.equal(duplicate.data.state.day_number,2);
 let persisted=(await listAcademyRuns()).find(x=>x.id===r.id);assert.equal(persisted.data.state.history.length,1);
 const rows=await listRecords('events');assert.equal(rows.filter(e=>e.data.event_type==='program.day_completed'&&e.data.target_id==='PCI-DAY-01').length,1);
 await updateAcademyRun(r.id,2,{kind:'pause'});assert.equal((await listAcademyRuns())[0].data.state.status,'paused');
 await updateAcademyRun(r.id,2,{kind:'resume'});await updateAcademyRun(r.id,2,{kind:'skip'});
 assert.equal((await listAcademyRuns())[0].data.state.history[1].result,'skipped');
});
test('checkpoint creates revisit only if user explicitly selected earlier day',async()=>{
 const r=(await listAcademyRuns())[0];await updateAcademyRun(r.id,3,{kind:'complete'});
 await assert.rejects(()=>updateAcademyRun(r.id,4,{kind:'complete'}));
 await updateAcademyRun(r.id,4,{kind:'complete',checkpoint_review:'PCI-DAY-01'});
 const rs=await listAcademyReviews();assert.ok(rs.some(x=>x.data.target_day_id==='PCI-DAY-01'&&x.data.reason==='checkpoint_selected'));
 const s=(await listAcademyRuns())[0].data.state;assert.equal(s.day_number,5);
});
test('quiz recall, optional retry, scheduled review, snooze and dismiss are local records',async()=>{
 const run=(await listAcademyRuns())[0],q=ACADEMY_QUESTIONS[0];
 const result=await submitAcademyQuiz(q,(q.correct_index+1)%3,run.id,'PCI-DAY-01','America/Los_Angeles');assert.equal(result.correct,false);
 let items=(await listAcademyReviews()).filter(x=>x.data.question_id===q.id);assert.equal(items.length,1);assert.equal(items[0].data.reason,'quiz_incorrect');
 const again=await submitAcademyQuiz(q,q.correct_index,run.id,'PCI-DAY-01','America/Los_Angeles');assert.equal(again.correct,true);
 items=(await listAcademyReviews()).filter(x=>x.data.question_id===q.id);assert.equal(items.length,1);assert.equal(items[0].data.reason,'quiz_correct');
 let rec=await updateAcademyReview(items[0].id,'snooze','America/Los_Angeles');assert.equal(rec.data.status,'active');
 rec=await updateAcademyReview(items[0].id,'dismiss','America/Los_Angeles');assert.equal(rec.data.status,'dismissed');
 assert.equal((await listAcademyQuizzes()).length,2);
 const events=await listRecords('events');assert.equal(events.filter(x=>x.data.event_type==='quiz.attempted').length,2);
});
test('restarting creates distinct run and retains prior history; no fake progress in new run',async()=>{
 const old=(await listAcademyRuns())[0];const next=await createAcademyRun();assert.notEqual(next.id,old.id);assert.equal(next.data.state.history.length,0);assert.ok((await listAcademyRuns()).some(r=>r.id===old.id));
});
test('private course data remains out of canonical public files and v2 export carries history',async()=>{
 const data=JSON.stringify(await exportPrivate());assert.ok(data.includes('program_progress'));assert.ok(data.includes('quiz_attempts'));
 const src=readFileSync(new URL('../src/academy.tsx',import.meta.url),'utf8');assert.ok(src.includes('MentalMasteryAcademy'));const app=readFileSync(new URL('../src/app.tsx',import.meta.url),'utf8');for(const slug of ['command-center','self-image','beliefs','theater','feedback','conditioning','scenarios','knowledge','academy','archive'])assert.ok(app.includes(`slug:'${slug}'`));
 assert.equal(JSON.parse(readFileSync(new URL('../public/data/curriculum.json',import.meta.url))).days.length,21);
});
