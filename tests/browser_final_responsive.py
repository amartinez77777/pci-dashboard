"""Real Chromium renderer, IN-MEMORY React16 bridge and synthetic IDB; NOT production Vite/native IDB."""
import json,re,traceback
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];DIST=ROOT/'dist-static';OUT=ROOT/'audit/final';OUT.mkdir(parents=True,exist_ok=True)
modules=['data','storage','route-guard','personal-labs-model','personal-labs-repo','personal-labs','vault-search','vault-data','vault-storage','vault','theater-model','theater-guidance','theater-repo','theater','feedback-model','learning-events','feedback-repo','feedback','scenario-model','scenario-repo','scenarios','conditioning-model','conditioning-repo','conditioning','academy-model','academy-repo','academy','personal-intelligence-model','personal-intelligence-repo','personal-intelligence','app','main']
parts=[]
for part in modules:
 s=(DIST/'assets'/f'{part}.js').read_text();s=re.sub(r'^import [^\n]*\n','',s,flags=re.M);s=re.sub(r'\bexport\s+(?=(async\s+)?(function|const|class))','',s)
 if part=='app':s='const AdvancedKnowledgeVault = KnowledgeVault;\n'+s
 parts.append(s)
assets={str(f.relative_to(DIST)):json.loads(f.read_text()) for f in (DIST/'data').rglob('*.json')}
css='\n'.join((DIST/f).read_text() for f in ['styles.css','vault.css','stage12.css','conditioning.css','academy.css','personal-intelligence.css'])
checks=[];route_expected={'command-center':'Continue from where you are.','self-image':'Self-Image','beliefs':'Belief','theater':'Theater','feedback':'Feedback','conditioning':'Conditioning','scenarios':'Scenario','knowledge':'Knowledge','academy':'21 days','archive':'Your own record'}
def check(label,condition,detail=''):
 checks.append({'check':label,'result':'PASS' if condition else 'FAIL','detail':str(detail)[:250]})
 if not condition:print('FAIL',label,detail,flush=True)
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage','--disable-gpu'])
 for width in [320,375,390,430,768,1440]:
  page=browser.new_page(viewport={'width':width,'height':810},reduced_motion='reduce');page.set_default_timeout(12000);errors=[];page.on('pageerror',lambda err:errors.append(str(err)))
  try:
   page.set_content('<html><head><style>'+css+'</style></head><body><div id="root"></div></body></html>')
   for f in ['react.production.min.js','react-dom.production.min.js','react16-hooks-bridge.js']:page.add_script_tag(content=(DIST/'vendor'/f).read_text())
   page.add_script_tag(content=(ROOT/'tests/idb_test_facade.js').read_text())
   page.evaluate('data=>{window.__research=data;window.fetch=(path)=>Promise.resolve({ok:true,json:()=>Promise.resolve(window.__research[String(path).replace(/^\\.\\//,"")])});window.confirm=()=>true}',assets)
   page.add_script_tag(content='\n'.join(parts))
   page.get_by_role('heading',name='Continue from where you are.').wait_for(timeout=20000)
   for route,needle in route_expected.items():
    page.evaluate('(route)=>{location.hash="#/"+route}',route)
    # Dynamic module mount; rendering may need the next task tick.
    page.wait_for_function('(term)=>document.querySelector("main")?.innerText.toLowerCase().includes(term.toLowerCase())',arg=needle,timeout=14000)
    check(f'{width}px_{route}_render',True)
    if route in ['command-center','archive','theater','feedback','conditioning','academy','knowledge']:
     size=page.evaluate('({doc:document.documentElement.scrollWidth,viewport:window.innerWidth})')
     check(f'{width}px_{route}_no_overflow',size['doc']<=size['viewport']+2,size)
   check(f'{width}px_no_unhandled_js_errors',len(errors)==0,errors[:3])
   check(f'{width}px_visible_focus_element',page.evaluate('()=>{const b=document.querySelector("nav button");b.focus();return document.activeElement===b}'))
  except Exception as e:
   check(f'{width}px_render_setup_or_navigation',False,str(e));traceback.print_exc(limit=1)
  finally:page.close()
 browser.close()
results={'status':'PASS' if all(c['result']=='PASS' for c in checks) else 'PARTIAL','passed':sum(c['result']=='PASS' for c in checks),'failed':sum(c['result']=='FAIL' for c in checks),'conditions':'Chromium real rendering with React16 offline compatibility bridge, synthetic IndexedDB, in-memory about:blank, not hosted origin / React18 / Safari','checks':checks}
(OUT/'RESPONSIVE_CHROMIUM_QA.json').write_text(json.dumps(results,indent=2)+'\n')
print(results['status'],results['passed'],'PASSED',results['failed'],'FAILED')
raise SystemExit(results['failed']!=0)
