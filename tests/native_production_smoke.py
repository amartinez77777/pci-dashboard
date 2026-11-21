"""Real Chromium smoke on the React18/Vite dist/ site using native IndexedDB.
Fails on missing module UI, console JavaScript exceptions, source-data load failures,
mobile overflow and loss of a temporary v2 record after reload.
Does not replace physical iPhone Safari or comprehensive user-workflow QA.
"""
from __future__ import annotations
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
import json
import os
import sys
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
ROUTES = ['command-center','self-image','beliefs','theater','feedback','conditioning','scenarios','knowledge','academy','archive']

class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass

def main():
    if not (DIST / 'index.html').is_file():
        raise RuntimeError('No actual production dist/index.html; refuse synthetic or offline harness')
    handler = partial(QuietHandler, directory=str(DIST))
    httpd = ThreadingHTTPServer(('127.0.0.1', 0), handler)
    Thread(target=httpd.serve_forever, daemon=True).start()
    origin=f'http://127.0.0.1:{httpd.server_port}'
    errors=[]
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch(headless=True, executable_path=os.environ.get("PCI_CHROMIUM_PATH"))
            context=browser.new_context(viewport={'width':390,'height':844},device_scale_factor=2)
            page=context.new_page()
            page.on('pageerror',lambda err: errors.append(str(err)))
            for slug in ROUTES:
                page.goto(origin+'/#/'+slug,wait_until='domcontentloaded',timeout=20000)
                page.locator('.sidebar nav button').first.wait_for(timeout=20000)
                page.wait_for_function("""() => {
                  const main=document.querySelector('#main-content');
                  return main && !main.querySelector('.loading-page') &&
                         main.innerText.trim().length > 50;
                }""",timeout=20000)
                body=page.locator('#main-content').inner_text()
                if 'Research files could not load.' in body or 'This page does not exist' in body:
                    raise AssertionError(f'{slug}: UI load failed: {body[:250]}')
                if page.locator('.sidebar nav button').count()!=10:
                    raise AssertionError(f'{slug}: expected 10 module navigation buttons')
                dimensions=page.evaluate('({width:innerWidth,scroll:document.documentElement.scrollWidth})')
                if dimensions['scroll'] > dimensions['width']+3:
                    raise AssertionError(f'{slug}: mobile overflow {dimensions}')
            page.goto(origin+'/#/settings',wait_until='domcontentloaded')
            page.get_by_text('On-device storage is available').wait_for(timeout=20000)
            marker=page.evaluate("""async () => {
              const db=await new Promise((resolve,reject)=>{
                const req=indexedDB.open('pci-private-v1',2);
                req.onsuccess=()=>resolve(req.result);req.onerror=()=>reject(req.error);
              });
              if(!db.objectStoreNames.contains('profile_preferences'))throw new Error('Missing preferences store');
              const now=new Date().toISOString(),id=crypto.randomUUID();
              const record={id,store:'profile_preferences',created_at:now,updated_at:now,
                owner:'user',privacy_mode:'device_local',schema_version:'2.0.0',
                data:{smoke_test:true},refs:[],sensitive:false};
              await new Promise((resolve,reject)=>{
                const tx=db.transaction('profile_preferences','readwrite');
                tx.objectStore('profile_preferences').put(record);
                tx.oncomplete=resolve;tx.onerror=()=>reject(tx.error);
              });
              db.close();return id;
            }""")
            page.reload(wait_until='domcontentloaded')
            page.get_by_text('On-device storage is available').wait_for(timeout=20000)
            found=page.evaluate("""async id => {
              const db=await new Promise((resolve,reject)=>{
                const req=indexedDB.open('pci-private-v1',2);
                req.onsuccess=()=>resolve(req.result);req.onerror=()=>reject(req.error);
              });
              const found=await new Promise((resolve,reject)=>{
                const tx=db.transaction('profile_preferences','readwrite');
                const os=tx.objectStore('profile_preferences');
                const get=os.get(id);
                get.onsuccess=()=>{const present=!!get.result;os.delete(id);resolve(present)};
                get.onerror=()=>reject(get.error);
              });
              db.close();return found;
            }""",marker)
            if not found:raise AssertionError('Native IndexedDB record disappeared after page reload')
            if errors:raise AssertionError('Uncaught browser errors: '+'; '.join(errors[:8]))
            context.close();browser.close()
        print(json.dumps({'status':'PASS','production_routes_tested':len(ROUTES),'viewport_px':390,
                          'indexeddb_v2_reload':'PASS','source':'real HTTP origin / real Chromium',
                          'not_verified':['physical iPhone Safari','full UI backup recovery','multi-tab conflicts']},indent=2))
    finally:
        httpd.shutdown()
        httpd.server_close()

if __name__ == '__main__':
    try:main()
    except Exception as exc:
        print('NATIVE PRODUCTION SMOKE FAILED:',repr(exc),file=sys.stderr)
        sys.exit(1)
