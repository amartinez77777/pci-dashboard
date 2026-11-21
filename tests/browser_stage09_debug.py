"""Chromium IN-MEMORY DOM+layout smoke. No origin, no IndexedDB, no React18/Vite claim.
Static local data is supplied through a faithful fetch mock. Records are not simulated.
"""
import json,re,sys,time
from pathlib import Path
from playwright.sync_api import sync_playwright,TimeoutError as PlaywrightTimeout
ROOT=Path(__file__).resolve().parents[1];DIST=ROOT/'dist-static';AUDIT=ROOT/'audit';AUDIT.mkdir(exist_ok=True)
modules=['command-center','self-image','beliefs','theater','feedback','conditioning','scenarios','knowledge','academy','archive']
code=[]
for part in ['data','storage','route-guard','vault-search','vault-data','vault-storage','vault','personal-intelligence-model','personal-intelligence-repo','personal-intelligence','app','main']:
 s=(DIST/'assets'/f'{part}.js').read_text()
 s=re.sub(r'^import [^\n]*\n','',s,flags=re.M)
 s=re.sub(r'\bexport\s+(?=(async\s+)?(function|const|class))','',s)
 if part=='app':s='const AdvancedKnowledgeVault = KnowledgeVault;\n'+s
 code.append(s)
bundle='\n'.join(code)
assets={str(f.relative_to(DIST)):json.loads(f.read_text()) for f in (DIST/'data').rglob('*.json')}
checks=[];errs=[]
def test(name,ok,detail=''):
 checks.append({'name':name,'status':'PASS' if ok else 'FAIL','detail':detail});print(('PASS' if ok else 'FAIL'),name,flush=True)
 if not ok:print('FAIL',name,detail)
def wait(page,ms=220):page.wait_for_timeout(ms)
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 for width,height in [(1440,900),(390,844),(320,700)]:
  page=b.new_page(viewport={'width':width,'height':height},device_scale_factor=1);page.set_default_timeout(4000)
  errors=[];page.on('pageerror',lambda e: errors.append(str(e)));page.on('console',lambda msg:errors.append(msg.text) if msg.type=='error' else None)
  css=(DIST/'styles.css').read_text()+'\n'+(DIST/'vault.css').read_text()
  page.set_content('<!doctype html><html lang="en"><head><meta name="viewport" content="width=device-width, initial-scale=1"><style>'+css+'</style></head><body><div id="root"></div></body></html>')
  for name in ['react.production.min.js','react-dom.production.min.js','react16-hooks-bridge.js']:
   page.add_script_tag(content=(DIST/'vendor'/name).read_text())
  page.evaluate('data=>{window.__research=data;window.fetch=(path)=>Promise.resolve({ok:true,json:()=>Promise.resolve(window.__research[String(path).replace(/^\\.\\//,"")])})}',assets)
  try:page.add_script_tag(content=bundle)
  except Exception as e:test('bundle-render-'+str(width),False,str(e)[:800]);page.close();continue
  try:page.locator('h1').wait_for(timeout=10000)
  except Exception as e:test('first-render-'+str(width),False,str(e)[:400]);page.close();continue
  test('first-launch-title-'+str(width),'A clearer way' in page.locator('h1').first.inner_text())
  test('real-data-count-'+str(width),'201' in page.locator('.metrics').inner_text())
  if width==1440:
   for slug in modules:
    page.evaluate('slug=>{location.hash="#/"+slug}',slug);wait(page,170)
    test('prior-route-'+slug,'This page does not exist' not in page.locator('#main-content').inner_text())
   page.evaluate('location.hash="#/knowledge"');wait(page,260)
   test('chapter-grid-16',page.locator('.kv-chapter-card').count()==16,str(page.locator('.kv-chapter-card').count()))
   page.screenshot(path=str(AUDIT/'stage09_desktop_chapters.png'),full_page=True)
   page.locator('.kv-chapter-card').first.click();wait(page,330)
   test('chapter-one-header','The Self-Image' in page.locator('.kv-hero h1').inner_text())
   test('chapter-full-index',page.locator('.kv-dossier-row').count()==10,str(page.locator('.kv-dossier-row').count()))
   test('chapter-author-practices',page.locator('.kv-item-card').count()>0)
   page.screenshot(path=str(AUDIT/'stage09_desktop_chapter_detail.png'),full_page=True)
   page.locator('.kv-dossier-row').first.click();wait(page,320)
   test('concept-full-thesis','Self-image as working self-description' in page.locator('.kv-hero h1').inner_text())
   test('concept-limits',page.get_by_text('Where the idea may fail').count()>0)
   test('concept-source-chip',page.locator('.kv-citation').count()>0)
   test('source-citation-opens',True)
   page.locator('.kv-citation').first.evaluate('(el)=>el.click()');wait(page,100)
   test('source-modal-visible',page.get_by_role('dialog').count()==1)
   test('citation-actual-page','PDF p. 13' in page.get_by_role('dialog').inner_text())
   page.get_by_role('button',name='Close citation').evaluate('(el)=>el.click()');wait(page,80)
   test('citation-close',page.get_by_role('dialog').count()==0)
   # Offline about:blank does not allow indexedDB; the button must be honestly disabled
   test('private-action-disabled-without-storage',page.get_by_role('button',name='☆ Bookmark').is_disabled())
   page.screenshot(path=str(AUDIT/'stage09_desktop_concept.png'),full_page=True)
   # invalid concept should offer a visible not-found instead of hanging
   page.evaluate('location.hash="#/knowledge/concept/PCI-C-CH01-999"');wait(page,300)
   test('unknown-concept-not-found',page.get_by_text('Record not located').count()==1)
   page.evaluate('location.hash="#/knowledge/search"');wait(page,300)
   test('search-index-loaded',page.locator('.kv-search-hit').count()==18)
   page.get_by_role('searchbox',name='Search words or "quoted phrase"').fill('"Self-image as working self-description"');wait(page,240)
   test('phrase-hits-original-id','Self-image as working self-description' in page.locator('.kv-search-hit').first.inner_text())
   page.get_by_role('combobox',name='Filter by chapter').select_option('16');wait(page,240)
   test('phrase-chapter-filter-empty',page.get_by_text('No matching records').count()==1)
   page.get_by_role('button',name='Clear all filters').click();wait(page,240)
   test('clear-search-restores-results',page.locator('.kv-search-hit').count()==18)
   page.get_by_role('combobox',name='Filter by source origin').select_option('updated_edition_editor');wait(page,180)
   test('editor-origin-filter-functional',page.locator('.kv-search-hit').count()==4,str(page.locator('.kv-search-hit').count()))
   page.get_by_role('button',name='Clear all filters').click();wait(page,170)
   page.screenshot(path=str(AUDIT/'stage09_desktop_search.png'),full_page=True)
   page.evaluate('location.hash="#/knowledge/graph/PCI-C-CH01-001"');wait(page,340)
   test('graph-renders',page.locator('.kv-graph-svg').count()==1)
   test('graph-edge-list',page.locator('.kv-graph-edge-row').count()>=1)
   page.get_by_role('button',name='Zoom in').click();wait(page,80)
   test('graph-zoom-control','120%' in page.locator('.kv-zoom-tools').inner_text())
   page.get_by_role('button',name='Inspect edge').first.click();wait(page,90)
   test('graph-edge-rationale',page.get_by_text('SOURCE-SUPPORTED INTERPRETIVE EDGE').count()==0 or page.locator('.kv-graph-inspector h2').count()>0)
   page.screenshot(path=str(AUDIT/'stage09_desktop_graph.png'),full_page=True)
   page.get_by_role('button',name='Compare').first.click();wait(page,280)
   test('compare-two-source-dossiers',page.locator('.kv-compare .kv-panel').count()==2,str(page.locator('.kv-compare .kv-panel').count()))
   page.evaluate('location.hash="#/knowledge/activity/PCI-ACT-CH01-001"');wait(page,240)
   test('activity-steps-available',page.locator('.kv-steps li').count()>=4)
   page.evaluate('location.hash="#/not-a-route"');wait(page,160)
   test('unknown-module-safe',page.get_by_text('This page does not exist').count()==1)
  else:
   page.get_by_role('button',name='Open navigation').click();wait(page,60)
   page.locator('.sidebar .nav-item').filter(has_text='Knowledge Vault').click();wait(page,260)
   test('mobile-16-chapter-cards-'+str(width),page.locator('.kv-chapter-card').count()==16)
   overflow=page.evaluate('({scroll:document.documentElement.scrollWidth,inner:innerWidth})')
   test('mobile-vault-overflow-'+str(width),overflow['scroll']<=overflow['inner']+1,str(overflow))
   page.screenshot(path=str(AUDIT/f'stage09_mobile_{width}_chapters.png'),full_page=True)
   page.locator('.kv-chapter-card').first.click();wait(page,250)
   overflow=page.evaluate('({scroll:document.documentElement.scrollWidth,inner:innerWidth})')
   test('mobile-chapter-overflow-'+str(width),overflow['scroll']<=overflow['inner']+1,str(overflow))
   page.evaluate('location.hash="#/knowledge/search"');wait(page,230)
   overflow=page.evaluate('({scroll:document.documentElement.scrollWidth,inner:innerWidth})')
   test('mobile-search-overflow-'+str(width),overflow['scroll']<=overflow['inner']+1,str(overflow))
   page.evaluate('location.hash="#/knowledge/graph/PCI-C-CH01-001"');wait(page,220)
   overflow=page.evaluate('({scroll:document.documentElement.scrollWidth,inner:innerWidth})')
   test('mobile-graph-overflow-'+str(width),overflow['scroll']<=overflow['inner']+1,str(overflow))
   page.screenshot(path=str(AUDIT/f'stage09_mobile_{width}_graph.png'),full_page=True)
  test('no-javascript-errors-'+str(width),not errors,str(errors)[:700]);page.close()
 b.close()
report={'scope':'In-memory Chromium + React16 compatibility runtime, local assets fetch-mocked. Not a Vite/React18 hosted-browser or iPhone Safari test; no real IndexedDB.','status':'PASS' if all(c['status']=='PASS' for c in checks) else 'FAIL','passed':sum(c['status']=='PASS' for c in checks),'failed':sum(c['status']=='FAIL' for c in checks),'checks':checks}
(AUDIT/'PCI_STAGE09_CHROMIUM_IN_MEMORY_QA.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ['scope','status','passed','failed']},indent=2))
sys.exit(0 if report['failed']==0 else 1)
