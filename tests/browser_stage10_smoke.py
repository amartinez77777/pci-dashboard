"""Stage 10 in-memory Chromium React16 compatibility UI + SYNTHETIC IDB facade.
No hosted origin, actual React18, real IndexedDB, or iPhone device assertions.
"""
import json,re,traceback
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];DIST=ROOT/'dist-static';AUDIT=ROOT/'audit';AUDIT.mkdir(exist_ok=True)
parts=['data','storage','route-guard','personal-labs-model','personal-labs-repo','personal-labs','theater-model','theater-repo','theater','vault-search','vault-data','vault-storage','vault','personal-intelligence-model','personal-intelligence-repo','personal-intelligence','app','main']
code=[]
for part in parts:
 s=(DIST/'assets'/f'{part}.js').read_text()
 s=re.sub(r'^import [^\n]*\n','',s,flags=re.M)
 s=re.sub(r'\bexport\s+(?=(async\s+)?(function|const|class))','',s)
 if part=='app':s='const AdvancedKnowledgeVault = KnowledgeVault;\n'+s
 code.append(s)
bundle='\n'.join(code)
assets={str(f.relative_to(DIST)):json.loads(f.read_text()) for f in (DIST/'data').rglob('*.json')}
checks=[];issues=[]
def check(name,ok,desc=''):
 checks.append({'name':name,'status':'PASS' if ok else 'FAIL','detail':str(desc)[:700]})
 if not ok:print('FAIL',name,desc)
def wait(page,ms=120):page.wait_for_timeout(ms)
def field(page,text):return page.locator('.lab-field').filter(has_text=text).locator('textarea').first
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 for width,height in [(1440,900),(390,844),(320,700)]:
  page=b.new_page(viewport={'width':width,'height':height},device_scale_factor=1);page.set_default_timeout(5000)
  errors=[];page.on('pageerror',lambda e: errors.append(str(e)))
  page.on('dialog',lambda d:d.accept())
  css=(DIST/'styles.css').read_text()+'\n'+(DIST/'vault.css').read_text()
  page.set_content('<!doctype html><html lang="en"><head><meta name="viewport" content="width=device-width, initial-scale=1"><style>'+css+'</style></head><body><div id="root"></div></body></html>')
  for name in ['react.production.min.js','react-dom.production.min.js','react16-hooks-bridge.js']:
   page.add_script_tag(content=(DIST/'vendor'/name).read_text())
  page.add_script_tag(content=(ROOT/'tests/idb_test_facade.js').read_text())
  page.evaluate('data=>{window.__research=data;window.fetch=(path)=>Promise.resolve({ok:true,json:()=>Promise.resolve(window.__research[String(path).replace(/^\\.\\//,"")])})}',assets)
  try:
   page.add_script_tag(content=bundle)
   page.locator('h1').wait_for(timeout=9000)
   check(f'first-launch-{width}','A clearer way' in page.locator('h1').first.inner_text())
   page.evaluate('location.hash="#/self-image"');wait(page,340)
   check(f'self-image-route-{width}','Understand your working self-image' in page.locator('h1').inner_text())
   check(f'self-image-optional-skip-{width}',page.get_by_role('button',name='Skip this worksheet').count()==1)
   page.get_by_role('button',name='Continue').click();wait(page,50)
   field(page,'How do you currently describe').fill('I often hesitate before speaking')
   field(page,'When does that description').fill('Weekly group discussions')
   page.get_by_role('button',name='Continue').click();wait(page,70)
   field(page,'One observable experience').fill('I waited until the final minute to contribute.')
   field(page,'A realistic goal').fill('Contribute one question next time.')
   check(f'self-image-source-links-{width}',page.locator('.lab-source-row').count()>=3)
   page.get_by_role('button',name='Save inventory locally').click();wait(page,400)
   check(f'self-image-saved-map-{width}','I often hesitate before speaking' in page.locator('.lab-map').inner_text())
   if width==1440:
    page.get_by_role('button',name='Edit',exact=True).first.click();wait(page,50)
    page.get_by_role('button',name='Continue').click();wait(page,40)
    field(page,'One observable experience').fill('I contributed before the final minute this time.')
    page.get_by_role('button',name='Save inventory locally').click();wait(page,400)
    check('self-image-history-retained',page.get_by_text('1 previous snapshots').count()==1)
    page.get_by_role('button',name='Reflections').click();wait(page,120)
    field(page,'What actually happened?').fill('I made one observation in a meeting.')
    field(page,'How did you interpret').fill('I am learning to speak up.')
    page.get_by_role('button',name='Save reflection locally').click();wait(page,360)
    check('reflection-saved',page.get_by_text('I made one observation in a meeting.').count()>0)
    page.locator('.lab-saved-card').get_by_role('button',name='Edit reflection').first.click();wait(page,70)
    field(page,'How did you interpret').fill('A specific observation, not proof of personality.')
    page.get_by_role('button',name='Save reflection locally').click();wait(page,360)
    check('reflection-history',page.get_by_text('Review 1 earlier snapshots').count()==1)
   page.evaluate('location.hash="#/beliefs"');wait(page,330)
   check(f'belief-route-{width}','Test assumptions with real-world observations' in page.locator('h1').inner_text())
   field(page,'Specific belief').fill('I never communicate clearly.')
   field(page,'Where or when').fill('During monthly work reviews')
   page.get_by_role('button',name='2. Observe').click();wait(page,40)
   field(page,'Observable facts only').fill('I paused once while explaining a report')
   field(page,'What meaning').fill('I interpreted silence as disapproval')
   page.get_by_role('button',name='3. Test evidence').click();wait(page,40)
   page.get_by_role('button',name='+ Add supporting evidence').click();wait(page,30)
   page.locator('.lab-evidence-item textarea').first.fill('I hesitated during one presentation.')
   page.get_by_role('button',name='+ Add counterexample').click();wait(page,40)
   page.locator('.lab-evidence-item textarea').last.fill('I explained a project clearly last week.')
   field(page,'Alternative explanations').fill('I was tired and less prepared.')
   page.get_by_role('button',name='4. Plan').click();wait(page,45)
   field(page,'A testable working hypothesis').fill('Using notes may improve clarity.')
   field(page,'One small, safe').fill('Prepare a 2-sentence introduction.')
   field(page,'What observable outcome').fill('I will complete the introduction.')
   page.get_by_role('button',name='5. Review').click();wait(page,80)
   # exact source link must point to preserved canonical IDs
   check(f'belief-source-link-{width}',page.locator('a[href^="#/knowledge/concept/PCI-C-"]').count()>=3)
   page.get_by_role('button',name='Save belief and revision').click();wait(page,430)
   check(f'belief-created-{width}',page.locator('.lab-belief-card').count()==1)
   check(f'belief-revision-initial-{width}',page.locator('.lab-history').count()==1)
   if width==1440:
    page.get_by_role('button',name='4. Plan').click();wait(page,50)
    field(page,'One small, safe').fill('Ask one clarifying question before responding.')
    page.get_by_role('button',name='5. Review').click();wait(page,50)
    page.get_by_role('button',name='Save belief and revision').click();wait(page,500)
    check('belief-revision-after-update',page.locator('.lab-compare-select option').count()>=4)
    check('belief-experiment-followup',page.get_by_role('button',name='Record observed outcome').count()>=1)
    page.locator('.lab-saved-card').last.locator('textarea').last.fill('I asked one question during the review.')
    page.get_by_role('button',name='Record observed outcome').last.click();wait(page,350)
    check('experiment-outcome-stored',page.get_by_text('I asked one question during the review.').count()>0)
    check('compare-two-snapshots',page.locator('.lab-compare-card').count()==2)
    page.screenshot(path=str(AUDIT/'stage10_desktop_belief_studio.png'),full_page=False)
    page.get_by_role('button',name='Delete selected belief and history').click();wait(page,360)
    check('belief-delete-confirmed',page.locator('.lab-belief-card').count()==0)
    page.evaluate('location.hash="#/knowledge"');wait(page,220)
    check('stage09-vault-regression',page.locator('.kv-chapter-card').count()==16)
   else:
    overflow=page.evaluate('({scroll:document.documentElement.scrollWidth,inner:window.innerWidth})');
    check(f'mobile-belief-overflow-{width}',overflow['scroll']<=overflow['inner']+1,overflow)
    page.screenshot(path=str(AUDIT/f'stage10_mobile_{width}_belief_studio.png'),full_page=False)
    page.evaluate('location.hash="#/self-image"');wait(page,200)
    overflow=page.evaluate('({scroll:document.documentElement.scrollWidth,inner:window.innerWidth})');
    check(f'mobile-self-image-overflow-{width}',overflow['scroll']<=overflow['inner']+1,overflow)
   check(f'js-errors-{width}',not errors,errors)
  except Exception as e:
   issues.append({'width':width,'exception':str(e),'traceback':traceback.format_exc()[-2200:]})
   print('EXCEPTION',width,str(e)[:500]);check(f'flow-unhandled-{width}',False,str(e)[:500])
  page.close()
 b.close()
report={'scope':'In-memory Chromium / React16 compatibility, with synthetic IndexedDB facade. NO native-IDB reload persistence or React18/Vite browser claim.','passed':sum(x['status']=='PASS' for x in checks),'failed':sum(x['status']=='FAIL' for x in checks),'checks':checks,'issues':issues}
(AUDIT/'PCI_STAGE10_CHROMIUM_SYNTHETIC_IDB.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'status':'PASS' if not report['failed'] else 'FAIL','passed':report['passed'],'failed':report['failed'],'issues':issues},indent=2));raise SystemExit(1 if report['failed'] else 0)
