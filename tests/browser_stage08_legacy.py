"""Real Chromium DOM smoke via in-memory assets. Does NOT test hosted HTTP or IndexedDB.
The container's managed Chromium policy blocks localhost/file navigation; we use
about:blank with trusted local assets and a fetch mock, and label scope explicitly.
"""
import json,re,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT/'dist-static'
AUDIT=ROOT/'audit'
AUDIT.mkdir(exist_ok=True)
modules=['command-center','self-image','beliefs','theater','feedback','conditioning','scenarios','knowledge','academy','archive']
code=[]
for part in ['data','storage','route-guard','personal-labs-model','personal-labs-repo','personal-labs','personal-intelligence-model','personal-intelligence-repo','personal-intelligence','app','main']:
 s=(DIST/'assets'/f'{part}.js').read_text()
 s=re.sub(r'^import [^\n]*\n','',s,flags=re.M)
 s=re.sub(r'\bexport\s+(?=(async\s+)?(function|const|class))','',s)
 code.append(s)
bundle='\n'.join(code)
assets={str(f.relative_to(DIST)):json.loads(f.read_text()) for f in (DIST/'data').rglob('*.json')}
checks=[];screens={}
def test(name,passed,detail=''):
 checks.append({'name':name,'status':'PASS' if passed else 'FAIL','detail':detail})
 if not passed:print('FAIL',name,detail)
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 for width,height in [(1440,900),(390,844),(320,700)]:
  page=b.new_page(viewport={'width':width,'height':height},device_scale_factor=1)
  errs=[];page.on('pageerror',lambda e: errs.append(str(e)));page.on('console',lambda m: errs.append(m.text) if m.type=='error' else None)
  page.set_content('<!doctype html><html lang="en"><head><meta name="viewport" content="width=device-width,initial-scale=1"><style>'+ (DIST/'styles.css').read_text()+'</style></head><body><div id="root"></div></body></html>')
  for name in ['react.production.min.js','react-dom.production.min.js','react16-hooks-bridge.js']:
   page.add_script_tag(content=(DIST/'vendor'/name).read_text())
  page.evaluate('data => {window.__research=data;window.fetch=(path)=>Promise.resolve({ok:true,json:()=>Promise.resolve(window.__research[String(path).replace(/^\\.\\//,"")])})}',assets)
  page.add_script_tag(content=bundle)
  page.locator('h1').wait_for(timeout=10000)
  test(f'first-launch-h1-{width}',page.locator('h1').count()==1)
  test(f'canonical-count-{width}', '201' in page.locator('.metrics').inner_text())
  ov=page.evaluate('({scroll:document.documentElement.scrollWidth,inner:innerWidth,body:document.body.scrollWidth})')
  test(f'no-horizontal-overflow-{width}',ov['scroll']<=ov['inner']+1,str(ov))
  if width==1440:
   page.screenshot(path=str(AUDIT/'desktop_command_center.png'),full_page=True)
   for name in modules:
    page.evaluate('slug=>{location.hash="#/"+slug}',name)
    page.wait_for_timeout(95)
    test('route-'+name,page.locator('#main-content').inner_text().strip()!='' and 'This page does not exist' not in page.locator('#main-content').inner_text(),page.locator('#main-content').inner_text()[:85])
   # knowledge resolves a full concept, displays separate page systems
   page.evaluate('location.hash="#/knowledge"');page.wait_for_timeout(240)
   test('knowledge-results-populated',page.locator('.result-row').count()>=50, str(page.locator('.result-row').count()))
   page.locator('.result-row').first.click();page.wait_for_timeout(240)
   test('concept-detail-source', page.locator('.vault-detail').get_by_text('PDF p.',exact=False).count()>0)
   page.screenshot(path=str(AUDIT/'desktop_knowledge_vault.png'),full_page=True)
   page.evaluate('location.hash="#/academy"');page.wait_for_timeout(190)
   test('21-authored-days',page.locator('.curriculum-day').count()==21,str(page.locator('.curriculum-day').count()))
   page.evaluate('location.hash="#/not-a-route"');page.wait_for_timeout(170)
   test('unknown-route-safe-recovery',page.get_by_text('This page does not exist').count()==1)
   page.get_by_role('button',name='Return to Command Center').click();page.wait_for_timeout(100)
   test('404-return-home',page.locator('h1').count()==1)
  else:
   test('mobile-navigation-button-'+str(width),page.get_by_role('button',name='Open navigation').count()==1)
   page.get_by_role('button',name='Open navigation').click();page.wait_for_timeout(60)
   test('mobile-menu-opens-'+str(width),page.locator('.sidebar.open').count()==1)
   page.locator('.sidebar .nav-item').filter(has_text='Knowledge Vault').click();page.wait_for_timeout(140)
   test('mobile-menu-route-'+str(width),'Knowledge Vault' in page.locator('.breadcrumb').inner_text())
   page.screenshot(path=str(AUDIT/f'mobile_{width}_knowledge.png'),full_page=True)
   overflow=page.evaluate('({scroll:document.documentElement.scrollWidth,inner:innerWidth})')
   test('mobile-knowledge-no-overflow-'+str(width),overflow['scroll']<=overflow['inner']+1,str(overflow))
  test('no-console-errors-'+str(width),not errs,str(errs)[:600])
  page.close()
 b.close()
report={'status':'PASS' if all(x['status']=='PASS' for x in checks) else 'FAIL','scope':'Chromium in-memory React-16 compatibility bridge; no HTTP hosting and no actual IndexedDB, modern React18 Vite untested','tests':checks,'passed':sum(c['status']=='PASS' for c in checks),'failed':sum(c['status']=='FAIL' for c in checks)}
(AUDIT/'PCI_BROWSER_IN_MEMORY_QA.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:report[k] for k in ['status','passed','failed']},indent=2))
sys.exit(0 if report['status']=='PASS' else 1)
