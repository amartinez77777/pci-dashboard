"""Chromium in-memory React16 compatibility + synthetic IndexedDB UI checks.
NOT native IndexedDB, React18/Vite deployment, or physical Safari."""
import json,re
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]; DIST=ROOT/'dist-static'
modules=['data','storage','route-guard','personal-labs-model','personal-labs-repo','personal-labs','vault-search','vault-data','vault-storage','vault','theater-model','theater-guidance','theater-repo','theater','feedback-model','learning-events','feedback-repo','feedback','scenario-model','scenario-repo','scenarios','conditioning-model','conditioning-repo','conditioning','personal-intelligence-model','personal-intelligence-repo','personal-intelligence','app','main']
code=[]
for part in modules:
 s=(DIST/'assets'/f'{part}.js').read_text()
 s=re.sub(r'^import [^\n]*\n','',s,flags=re.M)
 s=re.sub(r'\bexport\s+(?=(async\s+)?(function|const|class))','',s)
 if part=='app': s='const AdvancedKnowledgeVault = KnowledgeVault;\n'+s
 code.append(s)
assets={str(f.relative_to(DIST)):json.loads(f.read_text()) for f in (DIST/'data').rglob('*.json')}
results=[]
def ck(name,yes):
 results.append({'name':name,'status':'PASS' if yes else 'FAIL'})
 if not yes: print('FAIL',name,flush=True)
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage','--disable-gpu'])
 for width in [390,1440]:
  pg=b.new_page(viewport={'width':width,'height':844})
  pg.set_default_timeout(9000)
  css='\n'.join((DIST/f).read_text() for f in ['styles.css','vault.css','stage12.css','conditioning.css'])
  pg.set_content(f'<html><head><style>{css}</style></head><body><div id="root"></div></body></html>')
  for name in ['react.production.min.js','react-dom.production.min.js','react16-hooks-bridge.js']:
   pg.add_script_tag(content=(DIST/'vendor'/name).read_text())
  pg.add_script_tag(content=(ROOT/'tests/idb_test_facade.js').read_text())
  pg.evaluate('data=>{window.__research=data;window.fetch=(path)=>Promise.resolve({ok:true,json:()=>Promise.resolve(window.__research[String(path).replace(/^\\.\\//,"")])})}',assets)
  pg.add_script_tag(content='\n'.join(code))
  pg.locator('h1').first.wait_for(timeout=14000)
  pg.evaluate('location.hash="#/conditioning"');pg.get_by_role('heading',name='Practice one response at a time.').wait_for(timeout=9000)
  pg.wait_for_timeout(190)
  ck('all-six-protocol-cards-'+str(width),pg.locator('.conditioning-card').count()==6)
  ck('all-card-start-controls-'+str(width),pg.get_by_role('button',name='Start practice').count()==6)
  ck('six-distinct-titles-'+str(width),len(set(pg.locator('.conditioning-card h3').all_text_contents()))==6)
  ck('empty-history-'+str(width),'No recorded practices' in pg.locator('.conditioning-empty').inner_text())
  pg.get_by_label('Practice style').select_option('written')
  pg.locator('.conditioning-card').first.get_by_role('button',name='Details').click()
  ck('source-chips-provenance-'+str(width),'PCI-C-CH06-001' in pg.locator('.conditioning-source').first.inner_text() and 'PCI adaptation' not in pg.locator('.conditioning-source').first.inner_text())
  pg.locator('.conditioning-card').first.get_by_role('button',name='Start practice').click()
  pg.get_by_role('heading',name='Name the interruption').wait_for(timeout=10000)
  ck('written-phase-specific-text-'+str(width),'brief, neutral label' in pg.locator('.conditioning-instruction').inner_text())
  pg.locator('.conditioning-choices input[type=radio]').first.check()
  pg.locator('.conditioning-writing textarea').first.fill('Private browser scenario note')
  pg.get_by_role('button',name='Next step').click()
  pg.get_by_role('heading',name='Choose a neutral cue').wait_for(timeout=10000)
  ck('different-phase-rendered-'+str(width),'Write the cue' in pg.locator('.conditioning-instruction').inner_text())
  pg.get_by_role('button',name='Pause & save').click()
  pg.get_by_role('button',name='Resume practice').wait_for(timeout=8000)
  ck('pause-controls-'+str(width),'PAUSED' in pg.locator('.conditioning-mode').inner_text())
  pg.get_by_role('button',name='Resume practice').click()
  pg.get_by_role('button',name='Skip step').click()
  pg.get_by_role('heading',name='Return without judgment').wait_for(timeout=8000)
  pg.get_by_role('button',name='Next step').click()
  pg.get_by_role('heading',name='Choose one next action').wait_for(timeout=8000)
  pg.get_by_role('button',name='Finish & save').click()
  pg.locator('.conditioning-history').first.wait_for(timeout=8000)
  ck('completed-session-reappears-'+str(width),pg.locator('.conditioning-history').count()==1 and 'completed' in pg.locator('.conditioning-history').first.inner_text())
  ck('completion-card-counter-'+str(width),'1 completed on this device' in pg.locator('.conditioning-card').first.inner_text())
  pg.locator('.conditioning-rate select').select_option('4')
  pg.wait_for_timeout(180)
  ck('usefulness-rating-saved-'+str(width),pg.locator('.conditioning-rate select').input_value()=='4')
  pg.locator('.conditioning-card').nth(1).get_by_role('button',name='Start practice').click()
  pg.get_by_role('heading',name='Find a supported position').wait_for(timeout=8000)
  pg.get_by_role('button',name='Save draft & exit').click()
  pg.locator('.conditioning-card').nth(1).get_by_role('button',name='Resume saved').wait_for(timeout=8000)
  ck('draft-resume-action-'+str(width),pg.locator('.conditioning-card').nth(1).get_by_role('button',name='Resume saved').count()==1)
  pg.locator('.conditioning-card').nth(1).get_by_role('button',name='Resume saved').click()
  pg.get_by_role('heading',name='Find a supported position').wait_for(timeout=8000)
  ck('resumed-same-phase-'+str(width),'Step 1 / 4' in pg.locator('.conditioning-progress').inner_text())
  pg.get_by_role('button',name='Save draft & exit').click()
  pg.evaluate('location.hash="#/feedback"');pg.get_by_role('heading',name='Observe. Adjust. Repeat.').wait_for(timeout=10000)
  ck('feedback-preserved-'+str(width),pg.locator('.cycle-root').count()==1)
  pg.evaluate('location.hash="#/scenarios"');pg.get_by_role('heading',name='Practice decisions, not predictions.').wait_for(timeout=9000)
  ck('scenario-preserved-'+str(width),pg.locator('.scenario-item').count()>=16)
  pg.evaluate('location.hash="#/knowledge"');pg.get_by_role('heading',name='Knowledge Vault').first.wait_for(timeout=9000) if pg.get_by_role('heading',name='Knowledge Vault').count() else pg.locator('.kv-root').first.wait_for(timeout=9000)
  ck('vault-preserved-'+str(width),pg.locator('.kv-root').count()>0)
  pg.evaluate('location.hash="#/conditioning"');pg.get_by_role('heading',name='Practice one response at a time.').wait_for(timeout=9000)
  ck('history-persists-on-route-return-'+str(width),pg.locator('.conditioning-history').count()==2)
  ck('no-overflow-'+str(width),pg.evaluate('document.documentElement.scrollWidth <= innerWidth + 2'))
  pg.close()
 b.close()
summary={'status':'PASS' if all(x['status']=='PASS' for x in results) else 'FAIL','passed':sum(x['status']=='PASS' for x in results),'failed':sum(x['status']=='FAIL' for x in results),'environment':'Chromium in-memory React16 compatibility with simulated IndexedDB, not real browser storage or a React18 production build','checks':results}
out=ROOT/'audit/checkpoint2';out.mkdir(exist_ok=True,parents=True);(out/'BROWSER_CHECKPOINT2_QA.json').write_text(json.dumps(summary,indent=2)+'\n')
print('CP2 BROWSER:',summary['status'],summary['passed'],'PASS',summary['failed'],'FAIL',flush=True)
raise SystemExit(summary['failed']!=0)
