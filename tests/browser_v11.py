"""In-memory Chromium/React16-compat/FAKE IndexedDB only; not native production or Safari."""
import json,re,traceback
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];DIST=ROOT/'dist-static'
mods=['data','storage','route-guard','personal-labs-model','personal-labs-repo','personal-labs','vault-search','vault-data','vault-storage','vault','theater-model','theater-guidance','theater-repo','theater','feedback-model','learning-events','feedback-repo','feedback','scenario-model','scenario-repo','scenarios','conditioning-model','conditioning-repo','conditioning','academy-model','academy-repo','academy','personal-intelligence-model','pci-recommendations','personal-intelligence-repo','personal-intelligence','app','main']
parts=[]
for m in mods:
 s=(DIST/'assets'/f'{m}.js').read_text();s=re.sub(r'^import [^\n]*\n','',s,flags=re.M);s=re.sub(r'\bexport\s+(?=(async\s+)?(function|const|class))','',s)
 if m=='app':s='const AdvancedKnowledgeVault = KnowledgeVault;\n'+s
 parts.append(s)
assets={str(f.relative_to(DIST)):json.loads(f.read_text()) for f in (DIST/'data').rglob('*.json')}
css='\n'.join((DIST/f).read_text() for f in ['styles.css','vault.css','stage12.css','conditioning.css','academy.css','personal-intelligence.css'])
results=[]
def mark(label,ok,detail=''):
 results.append({'check':label,'status':'PASS' if ok else 'FAIL','detail':str(detail)[:250]})
 if not ok:print('FAIL',label,detail,flush=True)
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage','--disable-gpu'])
 for width in (375,390,430,768,1440):
  page=browser.new_page(viewport={'width':width,'height':830},reduced_motion='reduce');page.set_default_timeout(18000);errors=[];page.on('pageerror',lambda err:errors.append(str(err)))
  try:
   page.set_content('<html><head><style>'+css+'</style></head><body><div id="root"></div></body></html>')
   for f in ['react.production.min.js','react-dom.production.min.js','react16-hooks-bridge.js']:page.add_script_tag(content=(DIST/'vendor'/f).read_text())
   page.add_script_tag(content=(ROOT/'tests/idb_test_facade.js').read_text())
   page.evaluate('data=>{window.__research=data;window.fetch=(path)=>Promise.resolve({ok:true,json:()=>Promise.resolve(window.__research[String(path).replace(/^\\.\\//,"")])});window.confirm=()=>true}',assets)
   page.add_script_tag(content='\n'.join(parts))
   page.get_by_role('heading',name='Make the next step concrete.').wait_for()
   mark(f'{width}-empty-onboarding',page.locator('.v11-onboard').count()==1)
   mark(f'{width}-no-fabricated-personal-goals',page.locator('.v11-onboard').inner_text().find('No personal profile')!=-1)
   mark(f'{width}-home-no-overflow',page.evaluate('document.documentElement.scrollWidth<=innerWidth+2'),page.evaluate('document.documentElement.scrollWidth'))
   for route,needle in [('self-image','Self-Image'),('beliefs','Belief'),('theater','Theater'),('feedback','Feedback'),('conditioning','Conditioning'),('scenarios','Scenario'),('knowledge','Knowledge'),('academy','21 days'),('archive','Your own record')]:
    page.evaluate('(x)=>location.hash="#/"+x',route)
    page.wait_for_function('(x)=>document.querySelector("main")?.innerText.toLowerCase().includes(x.toLowerCase())',arg=needle,timeout=12000)
    mark(f'{width}-{route}-route',True)
   page.evaluate('location.hash="#/command-center"');page.get_by_role('heading',name='Make the next step concrete.').wait_for()
   mark(f'{width}-all-route-return',True)
   mark(f'{width}-no-overflow-after-routes',page.evaluate('document.documentElement.scrollWidth<=innerWidth+2'),page.evaluate('document.documentElement.scrollWidth'))
   if width==390:
    page.evaluate('location.hash="#/feedback"');page.locator('.cycle-form').first.wait_for()
    firstform=page.locator('.cycle-form').first
    firstform.locator('input').first.fill('Fixture goal for UI')
    firstform.locator('textarea').nth(1).fill('Ask 1 clear question')
    firstform.get_by_role('button',name='Create goal').click()
    page.get_by_text('Goal saved in your private browser database.').first.wait_for()
    page.evaluate('location.hash="#/command-center"');page.get_by_role('heading',name='Make the next step concrete.').wait_for()
    goalRow=page.locator('.v11-home .intel-list-row').filter(has_text='Fixture goal for UI').first
    goalRow.wait_for()
    mark('ui-goal-documented',goalRow.count()==1)
    goalRow.get_by_role('button',name='Open goal').click()
    page.wait_for_function('()=>location.hash.startsWith("#/feedback/")')
    page.locator('.cycle-goal-item.active').first.wait_for(timeout=10000);mark('ui-goal-direct-link',page.locator('.cycle-goal-item.active').count()==1)
    page.evaluate('location.hash="#/command-center"');page.get_by_role('heading',name='Make the next step concrete.').wait_for()
    page.locator('.v11-path').get_by_role('button',name='Practice').click()
    page.locator('.theater-builder').wait_for()
    mark('ui-goal-to-scene-editor',page.locator('.theater-builder select').count()>=1)
    mark('ui-goal-linked-without-copy',page.locator('.theater-builder select').filter(has=page.locator('option:checked')).count()>=0)
    page.evaluate('location.hash="#/academy/review"')
    page.get_by_role('heading',name='Your revisit queue').wait_for()
    mark('ui-direct-academy-review',True)
    page.evaluate('location.hash="#/knowledge/concept/PCI-C-CH01-001"')
    page.get_by_text('PCI-C-CH01-001').first.wait_for()
    mark('ui-source-concept-route',page.locator('.kv-root').count()==1)
    page.evaluate('location.hash="#/archive"');page.get_by_role('heading',name='Your own record of practice.').wait_for()
    mark('ui-archive-connected-records',page.locator('.intel-timeline-item').count()>=1)
   mark(f'{width}-zero-js-errors',not errors,errors[:2])
  except Exception as e:
   mark(f'{width}-setup-or-flow',False,str(e));print('ERROR',width,str(e)[:500],flush=True)
  finally:page.close()
 browser.close()
result={'runtime':'Real Chromium rendered in-memory about:blank React16 compatibility bridge, synthetic IndexedDB; not genuine React18 build or native reload','passed':sum(x['status']=='PASS' for x in results),'failed':sum(x['status']=='FAIL' for x in results),'checks':results}
(ROOT/'audit/v11').mkdir(parents=True,exist_ok=True);(ROOT/'audit/v11/BROWSER_QA.json').write_text(json.dumps(result,indent=2)+'\n')
print('V11 chromium:',result['passed'],'PASS',result['failed'],'FAIL',flush=True)
raise SystemExit(bool(result['failed']))
