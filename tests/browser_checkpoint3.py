"""Chromium in-memory React16-compatible UI with synthetic IndexedDB.
Does NOT establish actual HTTPS/React18/iPhone IndexedDB durability."""
import json,re
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];DIST=ROOT/'dist-static'
modules=['data','storage','route-guard','personal-labs-model','personal-labs-repo','personal-labs','vault-search','vault-data','vault-storage','vault','theater-model','theater-guidance','theater-repo','theater','feedback-model','learning-events','feedback-repo','feedback','scenario-model','scenario-repo','scenarios','conditioning-model','conditioning-repo','conditioning','academy-model','academy-repo','academy','personal-intelligence-model','personal-intelligence-repo','personal-intelligence','app','main']
code=[]
for part in modules:
 s=(DIST/'assets'/f'{part}.js').read_text()
 s=re.sub(r'^import [^\n]*\n','',s,flags=re.M)
 s=re.sub(r'\bexport\s+(?=(async\s+)?(function|const|class))','',s)
 if part=='app':s='const AdvancedKnowledgeVault = KnowledgeVault;\n'+s
 code.append(s)
assets={str(f.relative_to(DIST)):json.loads(f.read_text()) for f in (DIST/'data').rglob('*.json')}
results=[]
def ck(name,val):
 results.append({'name':name,'status':'PASS' if val else 'FAIL'})
 if not val:print('FAIL',name,flush=True)
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage','--disable-gpu'])
 for width in [390,1440]:
  pg=b.new_page(viewport={'width':width,'height':844});pg.set_default_timeout(10000)
  css='\n'.join((DIST/f).read_text() for f in ['styles.css','vault.css','stage12.css','conditioning.css','academy.css'])
  pg.set_content(f'<html><head><style>{css}</style></head><body><div id="root"></div></body></html>')
  for f in ['react.production.min.js','react-dom.production.min.js','react16-hooks-bridge.js']:
   pg.add_script_tag(content=(DIST/'vendor'/f).read_text())
  pg.add_script_tag(content=(ROOT/'tests/idb_test_facade.js').read_text())
  pg.evaluate('data=>{window.__research=data;window.fetch=(path)=>Promise.resolve({ok:true,json:()=>Promise.resolve(window.__research[String(path).replace(/^\\.\\//,"")])})}',assets)
  pg.add_script_tag(content='\n'.join(code));pg.locator('h1').first.wait_for(timeout=16000)
  pg.evaluate('location.hash="#/academy"')
  pg.get_by_role('heading',name='21 days of deliberate learning').wait_for()
  ck('21-authored-days-'+str(width),pg.locator('.academy-day-grid button').count()==21)
  ck('honest-no-progress-'+str(width),'No activity is recorded' in pg.locator('.academy-panel').first.inner_text())
  pg.get_by_role('button',name='Start optional course').click()
  pg.get_by_role('heading',name='A specific self-description').wait_for()
  ck('first-day-task-'+str(width),'working' in pg.locator('.academy-workspace').inner_text().lower() or 'description' in pg.locator('.academy-workspace').inner_text().lower())
  ck('day1-first-'+str(width),'PCI-DAY-01' in pg.locator('.academy-stephead').inner_text())
  pg.get_by_role('button',name='Acknowledge main task attempted').click()
  pg.get_by_role('heading',name='Set a target and find feedback').wait_for()
  ck('explicit-day1-to-day2-'+str(width),'PCI-DAY-02' in pg.locator('.academy-stephead').inner_text())
  # No external lesson link automatically completes a day.
  ck('only-one-acknowledged-'+str(width),len(pg.evaluate('(async()=>{let db=await openPrivateDB();return (await listAcademyRuns())[0].data.state.history})()'))==1)
  pg.get_by_role('button',name='Pause, keep position').click()
  pg.get_by_text('This run is paused',exact=False).first.wait_for()
  pg.get_by_role('button',name='Back to course').click()
  pg.get_by_role('button',name='Resume course').click()
  # Resume course is on home; return to active day
  pg.get_by_role('button',name='Continue Day 2').click()
  pg.get_by_role('button',name='Explicitly skip this day').click()
  pg.get_by_role('heading',name='Rehearse then act').wait_for()
  pg.get_by_role('button',name='Acknowledge main task attempted').click()
  pg.get_by_role('heading',name='Inspect an invisible standard').wait_for()
  ck('checkpoint-day4-shown-'+str(width),pg.get_by_role('heading',name='Checkpoint: review and choose').count()==1)
  ck('checkpoint-prevents-auto-advance-'+str(width),pg.get_by_role('button',name='Acknowledge main task attempted').is_disabled())
  pg.locator('.academy-checkpoint select').select_option('PCI-DAY-01')
  pg.get_by_role('button',name='Acknowledge main task attempted').click()
  pg.get_by_role('heading',name='Make a low-stakes prediction').wait_for()
  ck('checkpoint-review-added-'+str(width),len(pg.evaluate('(async()=>await listAcademyReviews())()'))>=1)
  pg.get_by_role('button',name='Back to course').click()
  pg.get_by_role('button',name='Review queue',exact=False).click()
  ck('explainable-review-'+str(width),'explicitly selected' in pg.locator('.academy-review-item').first.inner_text())
  pg.get_by_role('button',name='Day history').click()
  ck('completed-and-skipped-history-'+str(width),'skipped' in pg.locator('.academy-day-grid').inner_text())
  ck('no-horizontal-overflow-'+str(width),pg.evaluate('document.documentElement.scrollWidth<=window.innerWidth+2'))
  for route,expected in [('feedback','.cycle-root'),('scenarios','.scenario-item'),('knowledge','.kv-root'),('conditioning','.conditioning-card')]:
   pg.evaluate(f'location.hash="#/{route}"');pg.locator(expected).first.wait_for(timeout=10000);ck(f'route-{route}-{width}',pg.locator(expected).count()>0)
  pg.close()
 b.close()
summary={'status':'PASS' if all(x['status']=='PASS' for x in results) else 'FAIL','passed':sum(x['status']=='PASS' for x in results),'failed':sum(x['status']=='FAIL' for x in results),'environment':'in-memory Chromium React16 compatibility, synthetic IndexedDB; no native reload or Safari','checks':results}
out=ROOT/'audit/checkpoint3';out.mkdir(parents=True,exist_ok=True);(out/'BROWSER_CHECKPOINT3_QA.json').write_text(json.dumps(summary,indent=2)+'\n')
print('CP3 BROWSER',summary['status'],summary['passed'],'PASS',summary['failed'],'FAIL',flush=True)
raise SystemExit(summary['failed']!=0)
