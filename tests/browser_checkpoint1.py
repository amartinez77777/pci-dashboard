"""Actual in-memory Chromium UI test with React16 bridge and synthetic IndexedDB.
Not a React18/Vite or persistent native IndexedDB test.
"""
import json,re
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];DIST=ROOT/'dist-static'
parts=['data','storage','route-guard','personal-labs-model','personal-labs-repo','personal-labs','vault-search','vault-data','vault-storage','vault','theater-model','theater-guidance','theater-repo','theater','feedback-model','learning-events','feedback-repo','feedback','scenario-model','scenario-repo','scenarios','personal-intelligence-model','personal-intelligence-repo','personal-intelligence','app','main']
code=[]
for part in parts:
 s=(DIST/'assets'/f'{part}.js').read_text()
 s=re.sub(r'^import [^\n]*\n','',s,flags=re.M)
 s=re.sub(r'\bexport\s+(?=(async\s+)?(function|const|class))','',s)
 if part=='app':s='const AdvancedKnowledgeVault = KnowledgeVault;\n'+s
 code.append(s)
assets={str(f.relative_to(DIST)):json.loads(f.read_text()) for f in (DIST/'data').rglob('*.json')}
results=[]
def ck(label,cond):
 results.append({'check':label,'status':'PASS' if cond else 'FAIL'})
 if not cond: print('FAIL',label,flush=True)
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-gpu','--disable-dev-shm-usage'])
 for width in [390,1440]:
  page=b.new_page(viewport={'width':width,'height':844});page.set_default_timeout(6000)
  decisions={'accept':False,'count':0}
  def on_dialog(d):
   decisions['count']+=1
   d.accept() if decisions['accept'] else d.dismiss()
  page.on('dialog',on_dialog)
  css='\n'.join((DIST/x).read_text() for x in ['styles.css','vault.css','stage12.css'])
  page.set_content(f'<!doctype html><html><head><style>{css}</style></head><body><div id="root"></div></body></html>')
  for name in ['react.production.min.js','react-dom.production.min.js','react16-hooks-bridge.js']:
   page.add_script_tag(content=(DIST/'vendor'/name).read_text())
  page.add_script_tag(content=(ROOT/'tests/idb_test_facade.js').read_text())
  page.evaluate('data=>{window.__research=data;window.fetch=(path)=>Promise.resolve({ok:true,json:()=>Promise.resolve(window.__research[String(path).replace(/^\\.\\//,"")])})}',assets)
  page.add_script_tag(content='\n'.join(code))
  page.locator('h1').first.wait_for(timeout=7000)
  # Navigate directly via hash (same event as sidebar and browser Back).
  page.evaluate('location.hash="#/self-image"');page.wait_for_timeout(330)
  page.get_by_role('button',name='Continue').click();page.wait_for_timeout(120)
  txt=page.locator('.lab-root textarea').first
  ck(f'self-image-form-present-{width}',txt.count()==1)
  txt.fill('This remains my unsaved wording');page.wait_for_timeout(100)
  ck(f'dirty-editor-registers-{width}',page.evaluate('hasDirtyEditors()'))
  page.evaluate('location.hash="#/knowledge"');page.wait_for_timeout(230)
  ck(f'cancel-keeps-route-{width}',page.evaluate('location.hash')=='#/self-image')
  ck(f'cancel-keeps-input-{width}',page.locator('.lab-root textarea').first.input_value()=='This remains my unsaved wording')
  ck(f'cancel-prompts-once-{width}',decisions['count']==1)
  decisions['accept']=True
  page.evaluate('location.hash="#/knowledge"');page.wait_for_timeout(330)
  ck(f'accepted-route-works-{width}',page.evaluate('location.hash')=='#/knowledge' and page.locator('.lab-root').count()==0)
  ck(f'accepted-prompts-only-once-{width}',decisions['count']==2)
  # Theater private scene editor should retain its draft after a cancelled navigation.
  decisions['accept']=False
  page.evaluate('location.hash="#/theater"');page.wait_for_timeout(310)
  page.get_by_role('button',name='Private scene builder').click();page.wait_for_timeout(90)
  scene=page.locator('.theater-builder input').first
  scene.fill('An unsaved stage checkpoint scene');page.wait_for_timeout(110)
  page.evaluate('location.hash="#/feedback"');page.wait_for_timeout(220)
  ck(f'theater-cancel-keeps-route-{width}',page.evaluate('location.hash')=='#/theater')
  ck(f'theater-cancel-keeps-scene-{width}',page.locator('.theater-builder input').first.input_value()=='An unsaved stage checkpoint scene')
  decisions['accept']=True
  page.evaluate('location.hash="#/feedback"');page.wait_for_timeout(350)
  ck(f'feedback-still-loads-{width}',page.get_by_role('heading',name='Observe. Adjust. Repeat.').count()==1)
  decisions['accept']=False
  goal=page.locator('.cycle-panel').first.locator('input').first
  goal.fill('Unsaved test feedback goal');page.wait_for_timeout(100)
  ck(f'feedback-registers-unsaved-{width}',page.evaluate('hasDirtyEditors()'))
  page.evaluate('location.hash="#/knowledge"');page.wait_for_timeout(180)
  ck(f'feedback-cancel-preserves-route-{width}',page.evaluate('location.hash')=='#/feedback')
  ck(f'feedback-cancel-preserves-goal-{width}',goal.input_value()=='Unsaved test feedback goal')
  decisions['accept']=True
  page.evaluate('location.hash="#/scenarios"');page.wait_for_timeout(390)
  ck(f'scenarios-still-load-{width}',page.get_by_role('heading',name='Practice decisions, not predictions.').count()==1)
  ck(f'no-horizontal-overflow-{width}',page.evaluate('document.documentElement.scrollWidth <= innerWidth + 2'))
  page.close()
 b.close()
summary={'status':'PASS' if all(x['status']=='PASS' for x in results) else 'FAIL','passed':sum(x['status']=='PASS' for x in results),'failed':sum(x['status']=='FAIL' for x in results),'tests':results,'environment':'Chromium in-memory React16-compat with synthetic IndexedDB, not native browser storage'}
(ROOT/'audit/checkpoint1/BROWSER_GUARD_QA.json').write_text(json.dumps(summary,indent=2)+'\n')
print('CHECKPOINT BROWSER',summary['status'],summary['passed'],summary['failed'],flush=True)
raise SystemExit(summary['failed']!=0)
