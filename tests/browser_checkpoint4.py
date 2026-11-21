"""In-memory React16 compatibility + synthetic IndexedDB smoke (NOT native HTTPS persistence)."""
import json,re
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];DIST=ROOT/'dist-static'
modules=['data','storage','route-guard','personal-labs-model','personal-labs-repo','personal-labs','vault-search','vault-data','vault-storage','vault','theater-model','theater-guidance','theater-repo','theater','feedback-model','learning-events','feedback-repo','feedback','scenario-model','scenario-repo','scenarios','conditioning-model','conditioning-repo','conditioning','academy-model','academy-repo','academy','personal-intelligence-model','personal-intelligence-repo','personal-intelligence','app','main']
code=[]
for part in modules:
 s=(DIST/'assets'/f'{part}.js').read_text();s=re.sub(r'^import [^\n]*\n','',s,flags=re.M);s=re.sub(r'\bexport\s+(?=(async\s+)?(function|const|class))','',s)
 if part=='app':s='const AdvancedKnowledgeVault = KnowledgeVault;\n'+s
 code.append(s)
assets={str(f.relative_to(DIST)):json.loads(f.read_text()) for f in (DIST/'data').rglob('*.json')}
results=[]
def check(label,val):
 results.append({'label':label,'status':'PASS' if val else 'FAIL'})
 if not val:print('FAIL:',label,flush=True)
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage','--disable-gpu'])
 for width in (390,1440):
  page=browser.new_page(viewport={'width':width,'height':830});page.set_default_timeout(15000)
  css='\n'.join((DIST/f).read_text() for f in ['styles.css','vault.css','stage12.css','conditioning.css','academy.css','personal-intelligence.css'])
  page.set_content('<html><head><style>'+css+'</style></head><body><div id="root"></div></body></html>')
  for f in ['react.production.min.js','react-dom.production.min.js','react16-hooks-bridge.js']:page.add_script_tag(content=(DIST/'vendor'/f).read_text())
  page.add_script_tag(content=(ROOT/'tests/idb_test_facade.js').read_text())
  page.evaluate('data=>{window.__research=data;window.fetch=(path)=>Promise.resolve({ok:true,json:()=>Promise.resolve(window.__research[String(path).replace(/^\\.\\//,"")])});window.confirm=()=>true}',assets)
  page.add_script_tag(content='\n'.join(code))
  page.get_by_role('heading',name='Continue from where you are.').wait_for(timeout=20000)
  page.get_by_text('Academy days attempted').first.wait_for()
  check(f'empty-real-progress-{width}',page.locator('.intel-metric strong').first.inner_text().strip()=='0')
  check(f'first-run-next-step-{width}','Choose a small goal or belief' in page.locator('.intel-two').first.inner_text())
  check(f'no-horizontal-overflow-home-{width}',page.evaluate('document.documentElement.scrollWidth<=window.innerWidth+2'))
  page.evaluate('location.hash="#/archive"')
  page.get_by_role('heading',name='Your own record of practice.').wait_for()
  page.locator('#archive-title').fill('Synthetic local lesson')
  page.locator('#archive-entry').fill('Observed a concrete attempt')
  page.locator('#archive-tags').fill('practice, test')
  page.get_by_role('button',name='Save reflection').click()
  page.get_by_text('Reflection saved on this device.').wait_for()
  check(f'archive-saved-{width}',page.locator('.intel-timeline-item').count()>0)
  page.locator('#archive-search').fill('practice')
  check(f'archive-search-title-tag-{width}',page.locator('.intel-timeline-item').count()>0)
  page.locator('#archive-search').fill('Observed a concrete attempt')
  check(f'archive-search-excludes-body-{width}',page.locator('.intel-timeline-item').count()==0)
  page.locator('#archive-search').fill('')
  page.locator('.intel-timeline-item').first.click()
  page.get_by_role('button',name='Edit note').click()
  page.locator('#archive-entry').fill('Edited body with a safe <b>tag</b>')
  page.get_by_role('button',name='Save changes').click()
  page.get_by_text('Reflection saved on this device.').wait_for()
  check(f'archive-edit-{width}','Edited body' in page.locator('.intel-detail').inner_text())
  page.get_by_role('button',name='Delete note').click()
  page.get_by_role('button',name='Undo last deletion').click()
  page.locator('.intel-timeline-item').first.wait_for()
  check(f'archive-undo-{width}',page.locator('.intel-timeline-item').count()>0)
  page.locator('#archive-title').fill('Unsaved draft')
  page.evaluate('window.confirm=()=>false')
  page.evaluate('location.hash="#/knowledge"')
  page.wait_for_timeout(120)
  check(f'route-guard-stays-archive-{width}',page.locator('#archive-title').count()==1 and page.locator('#archive-title').input_value()=='Unsaved draft')
  page.evaluate('window.confirm=()=>true')
  page.evaluate('location.hash="#/knowledge"')
  page.locator('.kv-root').first.wait_for()
  page.evaluate('location.hash="#/feedback"');page.locator('.cycle-root').first.wait_for()
  page.evaluate('location.hash="#/scenarios"');page.locator('.scenario-item').first.wait_for()
  page.evaluate('location.hash="#/conditioning"');page.locator('.conditioning-card').first.wait_for()
  page.evaluate('location.hash="#/academy"');page.get_by_role('heading',name='21 days of deliberate learning').wait_for()
  check(f'preserved-module-routes-{width}',True)
  page.evaluate('location.hash="#/command-center"');page.get_by_role('heading',name='Continue from where you are.').wait_for()
  page.get_by_text('Notes and reflections').first.wait_for()
  check(f'live-count-after-archive-save-{width}',page.locator('.intel-metric strong').last.inner_text().strip()=='1')
  check(f'no-horizontal-overflow-after-{width}',page.evaluate('document.documentElement.scrollWidth<=window.innerWidth+2'))
  page.close()
 browser.close()
summary={'status':'PASS' if all(x['status']=='PASS' for x in results) else 'FAIL','passed':sum(x['status']=='PASS' for x in results),'failed':sum(x['status']=='FAIL' for x in results),'environment':'In-memory Chromium with React16 compatibility bridge and simulated IndexedDB; NOT native HTTPS-origin or Safari','checks':results}
out=ROOT/'audit/checkpoint4';out.mkdir(parents=True,exist_ok=True);(out/'BROWSER_CHECKPOINT4_QA.json').write_text(json.dumps(summary,indent=2)+'\n')
print('CP4 browser',summary['status'],summary['passed'],'passed',summary['failed'],'failed',flush=True)
raise SystemExit(summary['failed']!=0)
