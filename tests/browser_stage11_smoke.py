"""Stage11 Chromium IN-MEMORY compatibility + SYNTHETIC IndexedDB only.
This is not native-origin persistence or an installed React18/Vite test.
"""
import json,re,traceback
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];DIST=ROOT/'dist-static';AUDIT=ROOT/'audit';AUDIT.mkdir(exist_ok=True)
parts=['data','storage','route-guard','personal-labs-model','personal-labs-repo','personal-labs','vault-search','vault-data','vault-storage','vault','theater-model','theater-guidance','theater-repo','theater','feedback-model','learning-events','feedback-repo','feedback','scenario-model','scenario-repo','scenarios','personal-intelligence-model','personal-intelligence-repo','personal-intelligence','app','main']
code=[]
for part in parts:
 s=(DIST/'assets'/f'{part}.js').read_text();s=re.sub(r'^import [^\n]*\n','',s,flags=re.M);s=re.sub(r'\bexport\s+(?=(async\s+)?(function|const|class))','',s)
 if part=='app':s='const AdvancedKnowledgeVault = KnowledgeVault;\n'+s
 code.append(s)
bundle='\n'.join(code)
assets={str(f.relative_to(DIST)):json.loads(f.read_text()) for f in (DIST/'data').rglob('*.json')}
checks=[];issues=[]
def check(name,ok,detail=''):
 checks.append({'check':name,'status':'PASS' if ok else 'FAIL','detail':str(detail)[:250]})
 if not ok:print('FAIL',name,detail,flush=True)
def wait(page,ms=250):page.wait_for_timeout(ms)
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-gpu','--disable-dev-shm-usage'])
 for width,height in [(1440,900),(390,844),(320,700)]:
  page=b.new_page(viewport={'width':width,'height':height});page.set_default_timeout(4500)
  errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.on('dialog',lambda dialog:dialog.accept())
  try:
   css=(DIST/'styles.css').read_text()+'\n'+(DIST/'vault.css').read_text()+'\n'+(DIST/'stage12.css').read_text()
   page.set_content('<!doctype html><html lang="en"><head><meta name="viewport" content="width=device-width, initial-scale=1"><style>'+css+'</style></head><body><div id="root"></div></body></html>',wait_until='domcontentloaded')
   for name in ['react.production.min.js','react-dom.production.min.js','react16-hooks-bridge.js']:page.add_script_tag(content=(DIST/'vendor'/name).read_text())
   page.add_script_tag(content=(ROOT/'tests/idb_test_facade.js').read_text())
   page.evaluate('data=>{window.__research=data;window.fetch=(path)=>Promise.resolve({ok:true,json:()=>Promise.resolve(window.__research[String(path).replace(/^\\.\\//,"")])})}',assets)
   page.add_script_tag(content=bundle)
   page.locator('h1').first.wait_for(timeout=7000)
   check(f'command-center-{width}',any(t in page.locator('h1').first.inner_text() for t in ['A clearer way','Continue from where you are.']))
   page.evaluate('location.hash="#/theater"');wait(page,550)
   check(f'theater-route-{width}',page.locator('h1').first.inner_text()=='Mental rehearsal, grounded in action.')
   check(f'12-real-templates-{width}',page.locator('.theater-template').count()==12)
   check(f'book-attribution-{width}',page.locator('.theater-template .theater-source').count()>=1)
   check(f'short-no-timer-options-{width}',page.get_by_role('option',name='Untimed · manual steps').count()==1)
   if width==1440:
    page.get_by_role('button',name='Private scene builder').click();wait(page,90)
    page.locator('.theater-builder input').first.fill('Synthetic meeting practice')
    page.locator('.theater-builder textarea').first.fill('A brief fictional meeting')
    page.get_by_role('button',name='Save private scene').click();wait(page,430)
    check('scene-saved',page.get_by_text('Private scene saved to this device.').count()>0)
    page.get_by_role('button',name='Guided templates').click();wait(page,100)
    check('saved-scene-listed',page.get_by_text('Synthetic meeting practice').count()>0)
    page.get_by_role('button',name='Rehearse').first.click();wait(page,380)
   else:
    page.locator('.theater-template').first.get_by_role('button',name='Begin').click();wait(page,370)
   check(f'player-start-{width}',page.locator('.theater-player').count()==1)
   check(f'player-guidance-{width}',page.get_by_role('heading',name='Introduce the scope').count()==1)
   check(f'controls-live-{width}',all(page.get_by_role('button',name=n).count()>0 for n in ['Pause','Next step','Skip step','Reset','Stop early']))
   page.get_by_role('button',name='Pause',exact=True).click();wait(page,200)
   check(f'pause-reveals-resume-{width}',page.get_by_role('button',name='Resume',exact=True).count()==1)
   page.get_by_role('button',name='Resume',exact=True).click();wait(page,150)
   page.get_by_role('button',name='Skip step').click();wait(page,190)
   check(f'skip-advances-{width}',page.get_by_role('heading',name='Build a realistic scene').count()==1)
   page.get_by_role('button',name='Previous').click();wait(page,140)
   check(f'rewind-works-{width}',page.get_by_role('heading',name='Introduce the scope').count()==1)
   page.get_by_role('button',name='Stop speech').click();wait(page,50)
   page.locator('.theater-aside textarea').fill('I practiced a short fictional opening.')
   page.locator('.theater-aside input:not([type="checkbox"])').first.fill('I will ask one question in a low-stakes context')
   page.get_by_role('button',name='Complete & save session').click();wait(page,370)
   check(f'completion-save-{width}',page.get_by_text('Session completion recorded once.').count()>0)
   page.get_by_role('button',name='Session history').click();wait(page,100)
   check(f'session-history-{width}',page.locator('.theater-history-item').count()==1)
   check(f'no-resume-completed-{width}',page.locator('.theater-history-item').get_by_role('button',name='Resume draft').count()==0)
   page.evaluate('location.hash="#/knowledge"');wait(page,380)
   check(f'knowledge-vault-preserved-{width}',page.locator('h1').count()>0 and 'Knowledge Vault' in page.locator('h1').first.inner_text(),str(page.locator('h1').all_text_contents())[:150])
   page.evaluate('location.hash="#/beliefs"');wait(page,320)
   check(f'belief-studio-preserved-{width}',page.get_by_role('heading',name='Test assumptions with real-world observations').count()==1)
   check(f'no-horizontal-overflow-{width}',page.evaluate('document.documentElement.scrollWidth <= innerWidth+1'),page.evaluate('({actual:document.documentElement.scrollWidth,viewport:innerWidth})'))
   check(f'no-fatal-js-errors-{width}',len(errors)==0,errors)
   if width==390:
    page.evaluate('location.hash="#/theater"');wait(page,250);None # screenshot captured in earlier manual audit; avoid blocking repeat
   if width==1440:
    page.evaluate('location.hash="#/theater"');wait(page,200);None # screenshot captured in earlier manual audit; avoid blocking repeat
  except Exception as exc:
   issues.append({'viewport':width,'issue':str(exc),'traceback':traceback.format_exc()[-1200:]});print('EXCEPTION',width,str(exc),flush=True)
  finally:page.close()
 b.close()
status='PASS' if not issues and all(x['status']=='PASS' for x in checks) else 'FAIL'
report={'suite':'Stage11 in-memory Chromium, synthetic storage only','status':status,'passed':sum(x['status']=='PASS' for x in checks),'failed':sum(x['status']=='FAIL' for x in checks),'checks':checks,'issues':issues,'limitations':['No real origin or native IndexedDB; React16 compatibility bridge not production React18; not physical iPhone']}
(AUDIT/'PCI_STAGE11_BROWSER_QA.json').write_text(json.dumps(report,indent=2))
print('Stage11 Chromium',status,'checks',report['passed'],'failed',report['failed'],'exceptions',len(issues),flush=True)
if status!='PASS':raise SystemExit(1)
