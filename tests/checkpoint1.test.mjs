import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {initialPlayer,settleClock,startPlayer,pausePlayer,stepPlayer,interruptOnLoad,finishPlayer,phaseBudgets,stopPlayer} from '../dist-static/assets/theater-model.js';
import {setEditorDirty,hasDirtyEditors,needsRouteLeaveConfirmation,canNavigateRoute,rollbackHash,handleBeforeUnload} from '../dist-static/assets/route-guard.js';
const rehearsals=JSON.parse(readFileSync(new URL('../public/data/rehearsals.json',import.meta.url),'utf8'));
const base=1_780_000_000_000;
const manual=rehearsals[0];

test('all 12 real templates have explicit manual advancement; budgets are cues',()=>{
 assert.equal(rehearsals.length,12);
 for(const t of rehearsals){assert.equal(t.timing.auto_advance,false);assert.ok(t.phases.every(p=>p.pause_after===true));}
});
test('manual phase remains running after 30 minutes; only Next changes it',()=>{
 let p=startPlayer(initialPlayer(manual,'full'),base);
 p=settleClock(p,manual,base+1_800_000);
 assert.equal(p.phase_index,0);assert.equal(p.status,'running');assert.equal(p.elapsed_ms,1_800_000);
 p=stepPlayer(p,manual,base+1_800_100,'next');
 assert.equal(p.phase_index,1);
});
test('all optional timing modes retain manual step behavior',()=>{
 for(const mode of ['full','short','custom','untimed']){
  const p=settleClock(startPlayer(initialPlayer(manual,mode,null,mode==='custom'?90:null),base),manual,base+600_000);
  assert.equal(p.phase_index,0);assert.equal(p.status,'running');
 }
 assert.equal(phaseBudgets(manual,initialPlayer(manual,'short')).reduce((a,b)=>a+b,0),60_000);
});
test('pausing freezes clock, resuming excludes paused interval, refresh safely pauses',()=>{
 let p=startPlayer(initialPlayer(manual),base);
 p=pausePlayer(p,manual,base+20_000);
 assert.equal(settleClock(p,manual,base+600_000).elapsed_ms,20_000);
 p=startPlayer(p,base+600_000);
 p=settleClock(p,manual,base+610_000);
 assert.equal(p.elapsed_ms,30_000);
 assert.equal(interruptOnLoad(p).status,'paused');
 assert.equal(interruptOnLoad(p).running_since_wall_ms,null);
});
test('autoplay applies only to explicit auto mode and respects per-phase pause_after',()=>{
 const automatic={...manual,timing:{...manual.timing,auto_advance:true},phases:manual.phases.map(p=>({...p,pause_after:false}))};
 const advanced=settleClock(startPlayer(initialPlayer(automatic),base),automatic,base+200_000);
 assert.ok(advanced.phase_index>1);
 const held={...automatic,phases:automatic.phases.map((p,i)=>({...p,pause_after:i===0}))};
 const still=settleClock(startPlayer(initialPlayer(held),base),held,base+200_000);
 assert.equal(still.phase_index,0);
});
test('manual final phase requires an explicit Next or Finish, never timer completion',()=>{
 let p=startPlayer(initialPlayer(manual),base);
 for(let i=0;i<4;i++)p=stepPlayer(p,manual,base+i*500,'next');
 p=settleClock(p,manual,base+1_000_000);
 assert.equal(p.phase_index,4);assert.equal(p.status,'running');
 assert.equal(stepPlayer(p,manual,base+1_000_100,'next').status,'review');
 assert.equal(finishPlayer(p,manual,base+1_000_100).status,'completed');
 assert.equal(stopPlayer(p,manual,base+1_000_100).status,'stopped');
});
test('untouched editor has no warning; dirty editor prompts only when leaving its module',()=>{
 setEditorDirty('belief',false);assert.equal(hasDirtyEditors(),false);
 assert.equal(needsRouteLeaveConfirmation('beliefs','knowledge'),false);
 setEditorDirty('belief',true);
 assert.equal(needsRouteLeaveConfirmation('beliefs/id','beliefs/another'),true);
 assert.equal(needsRouteLeaveConfirmation('beliefs','knowledge'),true);
 let calls=0;
 assert.equal(canNavigateRoute('beliefs','knowledge',()=>{calls++;return false}),false);
 assert.equal(calls,1);
 assert.equal(canNavigateRoute('beliefs','knowledge',()=>{calls++;return true}),true);
 assert.equal(calls,2);
 setEditorDirty('belief',false);assert.equal(hasDirtyEditors(),false);
});
test('cancelled hash navigation restores URL without triggering an additional hashchange',()=>{
 setEditorDirty('scene',true);
 let calls=0,url='';
 const fakeHist={state:{},replaceState:(_state,_title,newUrl)=>{calls++;url=newUrl}};
 const permitted=canNavigateRoute('theater','feedback',()=>false);
 assert.equal(permitted,false);
 rollbackHash('theater',{pathname:'/pci/',search:'?local=1'},fakeHist);
 assert.equal(url,'/pci/?local=1#/theater');assert.equal(calls,1);
 setEditorDirty('scene',false);
});
test('beforeunload registers protection only for meaningful dirty work',()=>{
 const e={preventDefault(){this.prevented=true},returnValue:null,prevented:false};
 handleBeforeUnload(e);assert.equal(e.prevented,false);
 setEditorDirty('archive',true);handleBeforeUnload(e);
 assert.equal(e.prevented,true);assert.equal(e.returnValue,'');setEditorDirty('archive',false);
});
