"""Hosted-only browser evidence for the isolated fictional handoff experiment.

Serve only fixed synthetic assets. Keep the runner's packaged Chrome sandbox.
This is a correctness gate, not human usability or a timing benchmark.
"""
from contextlib import contextmanager
from hashlib import sha256, file_digest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import argparse
import importlib.metadata
import json
import os
from pathlib import Path
import subprocess
import threading
import traceback
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
ASSETS = {'index.html': 'text/html', 'app.mjs': 'text/javascript', 'packet.mjs': 'text/javascript', 'style.css': 'text/css', 'fixtures/packet.json': 'application/json'}
SOURCE_COMMIT = '5fea8d741a571d001a3556b765a360d5a3c04906'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate_requests(requests, origin):
    require(bool(requests), 'No browser request evidence recorded')
    allowed = {'', *ASSETS, 'synthetic-away', 'favicon.ico'}
    for item in requests:
        require(item['url'].startswith(origin), 'Non-local browser request')
        path = item['url'][len(origin):]
        require(path in allowed, f'Unexpected local asset request: {path}')
        require(item['method'] == 'GET' and not item['has_post_data'], 'Browser mutation request')


def validate_storage(snapshot):
    require(set(snapshot) == {'local', 'session', 'cookies', 'indexedDB', 'caches', 'serviceWorkers'}, 'Incomplete storage evidence')
    require(not any(snapshot.values()), f'Unexpected browser persistence: {snapshot}')


def report_passes(report):
    return report.get('browser_run_started') is True and len(report.get('cases', [])) == 8 and all(case.get('passed') is True for case in report['cases'])


@contextmanager
def local_assets():
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_args):
            pass

        def do_GET(self):
            path = self.path[1:]
            if path == 'favicon.ico':
                self.send_response(204); self.end_headers(); return
            if path == 'synthetic-away':
                body = b'<!doctype html><html lang="en"><title>Synthetic away page</title><h1>Synthetic away page</h1><p>Navigation test only.</p></html>'
                content_type = 'text/html'
            else:
                path = path or 'index.html'
                if path not in ASSETS:
                    self.send_error(404); return
                body = (ROOT / path).read_bytes()
                content_type = ASSETS[path]
            self.send_response(200)
            self.send_header('Content-Type', content_type + '; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers(); self.wfile.write(body)
    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
    try:
        yield f'http://127.0.0.1:{server.server_port}/'
    finally:
        server.shutdown(); server.server_close(); thread.join()


def check_layout(page, result, label):
    sizes = page.evaluate('''() => ({viewport: innerWidth, document: document.documentElement.scrollWidth,
      overflowing: [...document.querySelectorAll('main *, header *, footer')].filter(el => {
        const rect = el.getBoundingClientRect(); return rect.width > 0 && (rect.right > innerWidth + 1 || rect.left < -1);
      }).map(el => ({tag: el.tagName, id: el.id, width: el.getBoundingClientRect().width}))})''')
    result.setdefault('layouts', {})[label] = sizes
    require(sizes['document'] <= sizes['viewport'] + 1 and not sizes['overflowing'], f'Overflow at {label}: {sizes}')


def save_shot(page, output, result, label, selector=None):
    path = output / f"{result['case']}-{label}.png"
    if selector:
        page.locator(selector).screenshot(path=str(path), timeout=15000)
    else:
        page.screenshot(path=str(path), full_page=False, timeout=15000)
    result.setdefault('screenshots', []).append({'path': path.name, 'sha256': sha256(path.read_bytes()).hexdigest()})


def storage_snapshot(context, page):
    snapshot = page.evaluate('''async () => ({local: Object.keys(localStorage), session: Object.keys(sessionStorage),
      indexedDB: (await indexedDB.databases()).map(x => x.name), caches: await caches.keys(),
      serviceWorkers: (await navigator.serviceWorker.getRegistrations()).map(x => x.scope)})''')
    snapshot['cookies'] = context.cookies()
    return snapshot


def check_flow(page, origin, expect, result, output, text_scale):
    def ready():
        expect(page.locator('#status')).to_have_text('BASELINE. B included. ')
        expect(page.locator('#open-A')).to_be_visible()
        expect(page.locator('#baseline')).to_have_attribute('aria-pressed', 'true')
        expect(page.locator('#source-panel')).to_have_count(0)
    page.goto(origin); ready()
    if text_scale != 1:
        page.evaluate('(n) => document.documentElement.style.fontSize = `${100*n}%`', text_scale)
    expect(page.locator('#scope-notice')).to_contain_text('Recorded route coverage is incomplete')
    expect(page.locator('#scope-notice')).to_contain_text('NOT_EVALUATED')
    require(page.evaluate("matchMedia('(prefers-reduced-motion: reduce)').matches"), 'Reduced motion not active')
    check_layout(page, result, 'baseline')
    save_shot(page, output, result, 'baseline')
    initial_url = page.url
    initial_history = page.evaluate('history.length')
    page.keyboard.press('Tab'); expect(page.locator('.skip')).to_be_focused()
    page.keyboard.press('Enter'); expect(page.locator('#content')).to_be_focused()
    page.locator('#baseline').focus()
    page.keyboard.press('Tab'); expect(page.locator('#candidate')).to_be_focused()
    page.keyboard.press('Enter'); expect(page.locator('#candidate')).to_have_attribute('aria-pressed', 'true')
    page.keyboard.press('Tab'); expect(page.locator('#reset')).to_be_focused()
    page.keyboard.press('Tab'); expect(page.locator('#toggle-B')).to_be_focused()
    focus_style = page.locator('#toggle-B').evaluate("el => ({style:getComputedStyle(el).outlineStyle,width:getComputedStyle(el).outlineWidth})")
    require(focus_style['style'] != 'none' and float(focus_style['width'].replace('px', '')) >= 2, 'Keyboard focus indicator missing')
    result['focus_style'] = focus_style
    page.keyboard.press('Enter'); expect(page.locator('#toggle-B')).to_be_focused()
    expect(page.locator('#status')).to_contain_text('B excluded from hypothetical packet')
    expect(page.get_by_text('Required source excluded from this hypothetical packet: B', exact=True)).to_be_visible()
    expect(page.get_by_text('Recorded rule: ALL of A, B, C.', exact=False)).to_contain_text('Application: NOT_EVALUATED')
    expect(page.get_by_text('Separately recorded, unassessed route. No scientific acceptance is implied.', exact=True)).to_be_visible()
    page.keyboard.press('Tab'); expect(page.locator('#preview-button')).to_be_focused()
    page.keyboard.press('Enter')
    expect(page.get_by_role('heading', name='PROPOSED · BLOCKED', exact=True)).to_be_visible()
    expect(page.get_by_text('DESTINATION_CONTEXT_EXCLUDED_FROM_PACKET', exact=True)).to_be_visible()
    check_layout(page, result, 'blocked')
    save_shot(page, output, result, 'blocked', 'main > section:last-child')
    page.locator('#toggle-B').click(); expect(page.locator('#toggle-B')).to_be_focused()
    expect(page.get_by_role('heading', name='PROPOSED · BLOCKED', exact=True)).to_have_count(0)
    page.locator('#preview-button').click(); page.locator('#preview-button').click()
    expect(page.get_by_role('heading', name='PROPOSED · PREVIEW_ONLY', exact=True)).to_have_count(1)
    preview = page.locator('main > section:last-child')
    for text in ['Purpose explanatory_update; audience OWNER; scientific effect NONE', 'fictional:a:resource-001', 'fictional:b:resource-001', 'fictional-A-revision-1', 'fictional-B-revision-1', 'W1 owner researcher-alpha; CURRENT; HOLD CLEAR', 'no action, completed receipt or resulting provider identity']:
        expect(preview).to_contain_text(text)
    check_layout(page, result, 'preview')
    save_shot(page, output, result, 'preview', 'main > section:last-child')
    page.locator('#open-B').focus(); page.keyboard.press('Enter')
    expect(page.locator('#open-B')).to_be_focused()
    panel = page.locator('#source-panel')
    for text in ['2026-10-01T09:00:00Z', '2026-10-02T12:00:00Z', 'Fictional finite packet; application not evaluated', 'fictional:b:resource-001', 'fictional-B-revision-1', 'VERIFIED', '<img src=x onerror=alert(1)> PRIVATE_CANARY_B']:
        expect(panel).to_contain_text(text)
    expect(page.locator('img')).to_have_count(0)
    page.keyboard.press('Enter')
    expect(page.locator('#open-B').locator('..')).to_contain_text('Source opens: 1.')
    tab_ids = []
    for _ in range(10):
        page.keyboard.press('Tab'); active = page.evaluate('document.activeElement.id'); tab_ids.append(active)
        if active == 'close-source':
            break
    require(tab_ids == ['open-C', 'open-D', 'open-E', 'close-source'], f'Unexpected source-panel keyboard path: {tab_ids}')
    check_layout(page, result, 'source')
    save_shot(page, output, result, 'source-B', '#source-panel')
    page.keyboard.press('Enter')
    expect(page.locator('#source-panel')).to_have_count(0); expect(page.locator('#open-B')).to_be_focused()
    page.locator('#open-C').click()
    expect(page.locator('#source-panel')).to_contain_text('2026-09-01T09:00:00Z')
    expect(page.locator('#source-panel')).to_contain_text('Archive representation, not an extracted member.')
    page.locator('#close-source').click(); expect(page.locator('#open-C')).to_be_focused()
    page.locator('#baseline').click()
    expect(page.get_by_role('heading', name='PROPOSED · PREVIEW_ONLY', exact=True)).to_have_count(0)
    expect(page.locator('#preview-button')).to_have_count(0)
    require(page.url == initial_url + '#content', 'Mode changed navigation URL')
    require(page.evaluate('history.length') == initial_history + 1, 'Mode changes added history beyond the skip anchor')
    page.locator('#candidate').click(); page.locator('#toggle-B').click(); page.locator('#open-A').click()
    page.locator('#reset').click(); ready()
    expect(page.locator('#open-A').locator('..')).to_contain_text('Source opens: 0.')
    page.locator('#candidate').click(); page.locator('#toggle-B').click(); page.locator('#preview-button').click()
    page.reload(); ready()
    expect(page.locator('#open-B').locator('..')).to_contain_text('Source opens: 0.')
    page.locator('#candidate').click(); page.locator('#toggle-B').click(); page.locator('#open-B').click()
    page.goto(origin + 'synthetic-away'); expect(page.get_by_role('heading', name='Synthetic away page')).to_be_visible()
    page.go_back(); ready()
    page.go_forward(); expect(page.get_by_role('heading', name='Synthetic away page')).to_be_visible()
    page.go_back(); ready()
    result['steps'] = ['baseline and candidate scope preserved', 'keyboard skip/control/source-close traversal and visible focus', 'withhold B blocks only fictional proposal and preserves ALL/NOT_EVALUATED', 'restore yields PROPOSED/PREVIEW_ONLY with identities, dates, owner and HOLD', 'repeated activation is idempotent', 'source dates, scope, archive identity and inert image-looking text', 'all measured views have no overflow', 'reset, refresh and real Back/Forward clear disposable state', 'reduced motion active']


def check_refusal(page, origin, expect, result, kind, output):
    fixture = json.loads((ROOT / 'fixtures/packet.json').read_text())
    if kind == 'public':
        fixture['access']['audience'] = 'PUBLIC'
    elif kind == 'denied':
        fixture['access']['sourceAccess']['B'] = 'DENIED'
    else:
        fixture = {'synthetic': True, 'unexpected': 'FICTIONAL invalid fixture'}
    page.route(origin + 'fixtures/packet.json', lambda route: route.fulfill(status=200, content_type='application/json', body=json.dumps(fixture)))
    page.goto(origin)
    if kind == 'invalid':
        expect(page.locator('#status')).to_have_text('Local fictional fixture could not be verified. The probe is unavailable; no action was performed.')
        expect(page.locator('main > *')).to_have_count(0)
        result['steps'] = ['invalid fixture refuses all reading/proposal output']
    else:
        expect(page.locator('#status')).to_contain_text('B is not visible under current fixture access; membership not disclosed')
        expect(page.locator('#open-B')).to_have_count(0)
        if kind == 'public':
            expect(page.locator('#open-C')).to_have_count(0)
        page.locator('#candidate').click()
        expect(page.locator('#toggle-B')).to_have_count(0)
        page.locator('#preview-button').click()
        expect(page.get_by_role('heading', name='PROPOSED · BLOCKED', exact=True)).to_be_visible()
        require('PRIVATE_CANARY_B' not in page.locator('body').inner_text(), 'B synthetic canary leaked into rendered refusal')
        require('fictional:b:resource-001' not in page.locator('body').inner_text(), 'B identity leaked into rendered refusal')
        require('R1 →' not in page.locator('body').inner_text(), 'Hidden-source route leaked into rendered refusal')
        if kind == 'public':
            require('PRIVATE_CANARY_C' not in page.locator('body').inner_text(), 'C canary leaked')
        result['steps'] = ['fixture access decision precedes rendered identities, counts, routes and proposal', 'synthetic canary absent from rendered output; static fixture is not a real access-control boundary']
    check_layout(page, result, kind); save_shot(page, output, result, kind)


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--output', type=Path, required=True)
    output = parser.parse_args().output; output.mkdir(parents=True, exist_ok=True)
    report = {'scientific_effect': 'NONE', 'browser_run_started': False, 'source_local_commit': SOURCE_COMMIT, 'cases': [], 'limitations': ['Headless packaged Chrome only; viewport emulation, not physical devices', 'Screenshots need independent visual inspection; not full accessibility certification', 'Synthetic static fixture only; access projection does not secure fixture bytes', 'No deployment, human usability pass, timing trial or efficiency claim']}
    try:
        report['checked_commit'] = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        report['tree'] = subprocess.check_output(['git', 'rev-parse', 'HEAD^{tree}'], cwd=ROOT, text=True).strip()
        require(not os.environ.get('GITHUB_SHA') or os.environ['GITHUB_SHA'] == report['checked_commit'], 'Runner source commit mismatch')
        report['run_id'] = os.environ.get('GITHUB_RUN_ID'); report['run_attempt'] = os.environ.get('GITHUB_RUN_ATTEMPT')
        report['source_sha256'] = {name: sha256((ROOT/name).read_bytes()).hexdigest() for name in ASSETS}
        report['playwright'] = importlib.metadata.version('playwright')
        from playwright.sync_api import sync_playwright, expect
        executable = Path('/opt/google/chrome/chrome'); require(executable.is_file(), 'Packaged Chrome missing')
        report['browser_executable'] = str(executable)
        with executable.open('rb') as binary:
            report['browser_executable_sha256'] = file_digest(binary, 'sha256').hexdigest()
        report['runner_image_os'] = os.environ.get('ImageOS'); report['runner_image_version'] = os.environ.get('ImageVersion')
        with local_assets() as origin, sync_playwright() as playwright:
            browser = playwright.chromium.launch(channel='chrome', chromium_sandbox=True)
            try:
                report['browser_run_started'] = True; report['browser'] = browser.version; report['chromium_sandbox'] = True
                cases = [('desktop', 1200, 900, 1, None), ('mobile390', 390, 844, 1, None), ('mobile320', 320, 844, 1, None), ('large390', 390, 844, 2, None), ('large320', 320, 844, 2, None), ('public', 390, 844, 1, 'public'), ('denied', 390, 844, 1, 'denied'), ('invalid', 320, 844, 1, 'invalid')]
                for label, width, height, scale, kind in cases:
                    result = {'case': label, 'viewport': {'width': width, 'height': height}, 'text_scale': scale, 'reduced_motion': 'reduce', 'passed': False, 'steps': []}; report['cases'].append(result)
                    context = browser.new_context(viewport=result['viewport'], reduced_motion='reduce')
                    requests, console, errors, dialogs = [], [], [], []
                    context.on('request', lambda request: requests.append({'url': request.url, 'method': request.method, 'resource_type': request.resource_type, 'has_post_data': request.post_data is not None}))
                    page = context.new_page(); page.set_default_timeout(15000)
                    page.on('console', lambda message: console.append({'type': message.type, 'text': message.text}))
                    page.on('pageerror', lambda error: errors.append(str(error)))
                    def on_dialog(dialog):
                        dialogs.append({'type': dialog.type, 'message': dialog.message}); dialog.dismiss()
                    page.on('dialog', on_dialog)
                    try:
                        if kind:
                            check_refusal(page, origin, expect, result, kind, output)
                        else:
                            check_flow(page, origin, expect, result, output, scale)
                        result['storage'] = storage_snapshot(context, page); validate_storage(result['storage'])
                        validate_requests(requests, origin)
                        require(not errors and not dialogs, 'Page script errors or dialogs')
                        require(not [x for x in console if x['type'] == 'error'], 'Console errors')
                        result['passed'] = True
                    except Exception:
                        result['error'] = traceback.format_exc()
                        try:
                            save_shot(page, output, result, 'failure')
                        except Exception:
                            result['screenshot_error'] = traceback.format_exc()
                    finally:
                        result['requests'] = requests; result['console'] = console; result['page_errors'] = errors; result['dialogs'] = dialogs
                        context.close()
            finally:
                browser.close()
        report['passed'] = report_passes(report)
    except Exception:
        report['passed'] = False; report['error'] = traceback.format_exc()
    finally:
        (output/'report.json').write_text(json.dumps(report, indent=2, sort_keys=True)+'\n')
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report['passed'] else 1

if __name__ == '__main__':
    raise SystemExit(main())
