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
SOURCE_COMMIT = '3d4faaca4a0f95f070815f655fb6631c57633eee'


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
    return report.get('browser_run_started') is True and len(report.get('cases', [])) == 16 and all(case.get('passed') is True for case in report['cases'])


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


def comparison_summary(rows):
    conditions = ['desktop', 'mobile390', 'mobile320', 'large390', 'large320']
    require(len(rows) == 10, 'Missing comparison rows')
    pairs = []
    for condition in conditions:
        matches = [r for r in rows if r['condition'] == condition]
        require(len(matches) == 2 and {r['mode'] for r in matches} == {'BASELINE', 'CANDIDATE'}, 'Missing or duplicate mode')
        baseline = next(r for r in matches if r['mode'] == 'BASELINE')
        candidate = next(r for r in matches if r['mode'] == 'CANDIDATE')
        for row in matches:
            require(row['task_correct'] and not row['telemetry']['saturated'] and row['telemetry']['comparisonEligible'], 'Ineligible comparison record')
        require(baseline['semantic_output'] == candidate['semantic_output'], 'Different semantic end states')
        exposure = lambda r: r['telemetry']['counts']['sourceOpens'] + r['telemetry']['counts']['previewPassportExposures']
        pairs.append({'condition': condition, 'same_semantic_output': True,
                      'baseline_actions': len(baseline['ui_activations']), 'candidate_actions': len(candidate['ui_activations']),
                      'action_difference_candidate_minus_baseline': len(candidate['ui_activations'])-len(baseline['ui_activations']),
                      'baseline_identity_exposures': exposure(baseline), 'candidate_identity_exposures': exposure(candidate),
                      'identity_exposure_difference_candidate_minus_baseline': exposure(candidate)-exposure(baseline),
                      'baseline_geometry_default': baseline['geometry_default'], 'candidate_geometry_default': candidate['geometry_default'],
                      'baseline_geometry_expanded': baseline['geometry_expanded'], 'candidate_geometry_expanded': candidate['geometry_expanded']})
    return {'status': 'COMPARABLE_DESCRIPTIVE_ONLY', 'pairs': pairs,
            'limits': 'One deterministic path per condition and mode. No timing, human, comprehension, causal-efficiency or scientific claim.'}


def activate(page, selector, label, record=None):
    page.locator(selector).focus()
    page.locator(selector).press('Enter')
    if record is not None:
        record.append({'action': label, 'selector': selector, 'input': 'keyboard Enter'})


def telemetry(page):
    return json.loads(page.locator('#instrumentation pre').text_content())


def geometry(page):
    return page.evaluate('''() => ({preview_height_px: document.querySelector('#preview-section').getBoundingClientRect().height,
      preview_width_px: document.querySelector('#preview-section').getBoundingClientRect().width,
      document_height_px: document.documentElement.scrollHeight, viewport_width_px: innerWidth,
      root_font_px: parseFloat(getComputedStyle(document.documentElement).fontSize)})''')


def ready(page, expect):
    expect(page.locator('#status')).to_have_text('BASELINE. B included. ')
    expect(page.locator('#baseline')).to_have_attribute('aria-pressed', 'true')
    expect(page.locator('#open-A')).to_be_visible()
    expect(page.locator('#toggle-B')).to_be_visible()
    expect(page.locator('#preview-button')).to_be_visible()


def check_core(page, expect, selector, ids):
    core = page.locator(selector + ' > .core-evidence')
    expect(core).to_be_visible()
    for source in ids:
        expect(core).to_contain_text(f'fictional:{source.lower()}:resource-001')
        expect(core).to_contain_text(f'Revision (recorded = observed): fictional-{source}-revision-1; freshness CURRENT')
        expect(core).to_contain_text(f'fictional-{source}-representation-1')
    for text in ['2026-10-01T09:00:00Z', '2026-10-02T12:00:00Z', 'Fictional finite packet; application not evaluated', 'ALLOWED / AVAILABLE', 'Byte evidence: VERIFIED']:
        expect(core).to_contain_text(text)
    require(core.locator('details').count() == 0, 'Mandatory evidence was moved into disclosure')


def expand_raw(page, expect, name, count):
    activate(page, '#summary-' + name, 'Expand raw evidence')
    expect(page.locator('#' + name)).to_have_attribute('open', '')
    page.wait_for_function('(n) => JSON.parse(document.querySelector("#instrumentation pre").textContent).counts.rawEvidenceExpansions === n', arg=count)


def check_flow(page, origin, expect, result, output, scale, mode):
    page.goto(origin); ready(page, expect)
    if scale != 1:
        page.evaluate('(n) => document.documentElement.style.fontSize = `${100*n}%`', scale)
    require(page.evaluate("matchMedia('(prefers-reduced-motion: reduce)').matches"), 'Reduced motion not active')
    page.keyboard.press('Tab'); expect(page.locator('.skip')).to_be_focused()
    page.keyboard.press('Enter'); expect(page.locator('#content')).to_be_focused()
    setup = []
    activate(page, '#' + mode.lower(), 'Select mode', setup)
    activate(page, '#toggle-B', 'Withhold B', setup)
    expect(page.locator('#status')).to_contain_text(f'{mode}. B excluded from hypothetical packet')
    activate(page, '#summary-instrumentation', 'Open setup counts', setup)
    expect(page.locator('#start-trial')).to_be_visible()
    activate(page, '#start-trial', 'Clear setup counts and close evidence', setup)
    require(telemetry(page)['events'] == [], 'Setup counts were not cleared')
    actions = []; tasks = []
    expect(page.locator('#route-R1')).to_contain_text('Recorded rule: ALL of A, B, C. Application: NOT_EVALUATED')
    expect(page.locator('#open-B').locator('..')).to_contain_text('Excluded in this hypothetical packet')
    expect(page.locator('#scope-notice')).to_contain_text('Recorded route coverage is incomplete')
    tasks.append({'task': 1, 'correct': True})
    trigger = '#open-B' if mode == 'BASELINE' else '#next-R1-B'
    navigation = page.evaluate('''(selector) => ({route_top_px: document.querySelector('#route-R1').getBoundingClientRect().top + scrollY, trigger_top_px: document.querySelector(selector).getBoundingClientRect().top + scrollY})''', trigger)
    activate(page, trigger, 'Task 2 read B', actions)
    navigation['source_panel_top_px'] = page.locator('#source-panel').evaluate('el => el.getBoundingClientRect().top + scrollY')
    navigation['route_to_trigger_distance_px'] = navigation['trigger_top_px'] - navigation['route_top_px']
    navigation['trigger_to_panel_distance_px'] = navigation['source_panel_top_px'] - navigation['trigger_top_px']
    expect(page.locator('#source-panel')).to_be_focused(); check_core(page, expect, '#source-panel', ['B'])
    expect(page.locator('#source-panel')).to_contain_text('<img src=x onerror=alert(1)> PRIVATE_CANARY_B')
    expect(page.locator('img')).to_have_count(0)
    expect(page.locator('#raw-B')).not_to_have_attribute('open', '')
    check_layout(page, result, 'source-default')
    save_shot(page, output, result, 'source-default', '#source-panel')
    page.keyboard.press('Tab'); expect(page.locator('#close-source')).to_be_focused()
    focus_style = page.locator('#close-source').evaluate("el => ({style:getComputedStyle(el).outlineStyle,width:getComputedStyle(el).outlineWidth})")
    require(focus_style['style'] != 'none' and float(focus_style['width'].replace('px', '')) >= 2, 'Keyboard focus indicator missing')
    result['focus_style'] = focus_style
    page.keyboard.press('Enter'); actions.append({'action': 'Close B', 'selector': '#close-source', 'input': 'keyboard Enter'})
    expect(page.locator(trigger)).to_be_focused(); expect(page.locator('#source-panel')).to_have_count(0)
    tasks.append({'task': 2, 'correct': True})
    expect(page.locator('#route-R2')).to_contain_text('Recorded rule: ALL of A, D. Application: NOT_EVALUATED')
    expect(page.locator('#route-R2')).to_contain_text('Separately recorded, unassessed route. No scientific acceptance is implied.')
    tasks.append({'task': 3, 'correct': True})
    for text in ['Target T: UNASSESSED / NOT_REVIEWED', 'Target U: UNASSESSED / NOT_REVIEWED', 'Engineering G: PASS. Fictional syntax check only; unrelated to scientific support']:
        expect(page.locator('#route-sheets')).to_contain_text(text)
    expect(page.locator('#scope-notice')).to_contain_text('No theorem-wide conclusion')
    tasks.append({'task': 4, 'correct': True})
    activate(page, '#toggle-B', 'Task 5 restore B', actions)
    expect(page.locator('#preview-section')).to_have_count(0)
    activate(page, '#preview-button', 'Task 5 re-evaluate fixed inputs and prepare proposal', actions)
    expect(page.locator('#preview-section h2')).to_have_text('PROPOSED · PREVIEW_ONLY')
    check_core(page, expect, '#preview-section', ['A', 'B'])
    expect(page.locator('#preview-section')).to_contain_text('Purpose explanatory_update; audience OWNER; scientific effect NONE; no resulting provider identity.')
    expect(page.locator('#handoff-sheet')).to_contain_text('W1: owner researcher-alpha; ownership CURRENT; HOLD CLEAR; observed 2026-10-02T12:00:00Z')
    expect(page.locator('#workflow-controls')).to_contain_text('No live service is contacted and no new digest is computed')
    expect(page.locator('#' + mode.lower())).to_have_attribute('aria-pressed', 'true')
    tasks.append({'task': 5, 'correct': True})
    record = {'condition': result['condition'], 'mode': mode, 'task_correct': all(t['correct'] for t in tasks), 'tasks': tasks,
              'setup_activations': setup, 'source_navigation_geometry': navigation, 'ui_activations': actions, 'telemetry': telemetry(page),
              'semantic_output': {'preview': page.locator('#preview-section').inner_text(), 'work_event': page.locator('#handoff-sheet').inner_text()},
              'recheck_classification': {'fixed_fixture_recheck_requests': 1, 'live_rechecks': 0, 'source_reopens': 0, 'avoidable_repeats_observed': 0, 'human_reading_inferred': False}}
    require(len(actions) == 4, 'Unexpected task action count')
    require(record['telemetry']['counts'] == {'sourceOpens': 1, 'sourceReopens': 0, 'rawEvidenceExpansions': 0, 'recheckRequests': 1, 'previewPassportExposures': 2}, 'Unexpected task exposure counts')
    require([e['type'] for e in record['telemetry']['events']] == ['OPEN_SOURCE', 'CLOSE_SOURCE', 'RESTORE', 'RECHECK_PREVIEW'], 'Unexpected task events')
    record['geometry_default'] = geometry(page); check_layout(page, result, 'preview-default')
    save_shot(page, output, result, 'preview-default', '#preview-section')
    # Everything below is separate diagnostic work, not task-performance data.
    expand_raw(page, expect, 'raw-preview', 1)
    expect(page.locator('#raw-preview')).to_contain_text('sha256/hex')
    expect(page.locator('#raw-preview')).to_contain_text('computed digest a5c01f770a3bd0bce4672a3b41abc893fd4ca7d139a23c0f2eab7bba0220adc2')
    record['geometry_expanded'] = geometry(page); check_layout(page, result, 'preview-expanded')
    save_shot(page, output, result, 'preview-expanded', '#preview-section')
    activate(page, '#open-B', 'Diagnostic source read')
    expand_raw(page, expect, 'raw-B', 2)
    check_layout(page, result, 'source-expanded'); save_shot(page, output, result, 'source-expanded', '#source-panel')
    activate(page, '#preview-button', 'Diagnostic benign re-evaluation')
    expect(page.locator('#raw-B')).to_have_attribute('open', '')
    expect(page.locator('#raw-preview')).to_have_attribute('open', '')
    alternate = 'candidate' if mode == 'BASELINE' else 'baseline'
    activate(page, '#' + alternate, 'Diagnostic mode switch')
    expect(page.locator('#raw-B')).to_have_attribute('open', '')
    expect(page.locator('#raw-preview')).to_have_attribute('open', '')
    expect(page.locator('#preview-section h2')).to_have_text('PROPOSED · PREVIEW_ONLY')
    activate(page, '#close-source', 'Close diagnostic source'); expect(page.locator('#open-B')).to_be_focused()
    activate(page, '#reset', 'Reset'); ready(page, expect)
    require(telemetry(page)['events'] == [], 'Reset left telemetry')
    expect(page.locator('#preview-section')).to_have_count(0)
    activate(page, '#toggle-B', 'Prepare refresh test'); page.reload(); ready(page, expect)
    activate(page, '#toggle-B', 'Prepare navigation test')
    page.goto(origin + 'synthetic-away'); page.go_back(); ready(page, expect)
    result['pageshow_after_back'] = page.evaluate('window.__browserCheckPageShows')
    page.go_forward(); expect(page.get_by_role('heading', name='Synthetic away page')).to_be_visible()
    page.go_back(); ready(page, expect)
    result['pageshow_after_second_back'] = page.evaluate('window.__browserCheckPageShows')
    result['bfcache_observed'] = any(result['pageshow_after_back']) or any(result['pageshow_after_second_back'])
    result['navigation_scope'] = 'Observed navigation reset; BFCache only if persisted pageshow recorded'
    result['measurement'] = record
    result['steps'] = ['same-mode five-task completion', 'same complete semantic output scored before descriptive comparison', 'counted source and preview identity exposures', 'mandatory evidence visible with raw provenance collapsed', 'raw disclosures expanded and stable across benign renders', 'source panel focus and actual trigger return', 'default and expanded no-overflow checks', 'reset, refresh, Back/Forward, reduced motion']


def mount_synthetic(page, origin, expect):
    page.goto(origin); ready(page, expect)
    return page.evaluate_handle('''async () => {
      const packet = await import('./packet.mjs'); const app = await import('./app.mjs');
      const fixture = packet.validateFixture(await (await fetch('./fixtures/packet.json')).json());
      const verifications = Object.fromEntries(await Promise.all(fixture.sources.map(async s => [s.id, await packet.verifyRepresentation(s.representation)])));
      const model = {fixture, access: structuredClone(fixture.access), verifications};
      return {model, controller: app.mountProbe(model), packet};
    }''')


def check_warm(page, origin, expect, result, output, mode):
    handle = mount_synthetic(page, origin, expect)
    activate(page, '#' + mode.lower(), 'Diagnostic mode')
    activate(page, '#open-B', 'Open B'); expand_raw(page, expect, 'raw-B', 1)
    activate(page, '#preview-button', 'Checked preview'); expand_raw(page, expect, 'raw-preview', 2)
    activate(page, '#summary-instrumentation', 'Show instrumentation')
    expect(page.locator('#instrumentation')).to_have_attribute('open', '')
    refusal = handle.evaluate('''s => {s.model.access.sourceAccess.B = 'DENIED'; try {s.controller.openSource('B'); return null;} catch(e) {return e.message;}}''')
    require(refusal == 'Source access unavailable', 'Warm denial did not refuse')
    for selector in ['#source-panel', '#raw-B', '#raw-preview', '#open-B', '#next-R1-B', '#preview-section']:
        expect(page.locator(selector)).to_have_count(0)
    expect(page.locator('#status')).to_contain_text('B is not visible under current fixture access; membership not disclosed')
    text = page.locator('body').text_content()
    for hidden in ['PRIVATE_CANARY_B', 'fictional:b:resource-001', 'fictional-B-revision-1']:
        require(hidden not in text, 'Warm hidden identity/content remains in DOM')
    metrics = telemetry(page)
    require(not metrics['comparisonEligible'] and all(event['target'] is None for event in metrics['events']), 'Warm telemetry leaked target or stayed eligible')
    expect(page.locator('#content')).to_be_focused()
    activate(page, '#preview-button', 'Re-evaluate denied fixture')
    expect(page.locator('#block-reasons')).to_contain_text('DESTINATION_ACCESS_DENIED')
    before = page.locator('#preview-section').inner_text()
    handle.evaluate("s => {s.model.access.workEvent.hold='ACTIVE'; s.model.access.workEvent.ownerIds.push('researcher-beta'); s.model.access.revisionFreshnessBySourceId.B='STALE'; s.controller.showPreview();}")
    require(page.locator('#preview-section').inner_text() == before, 'Hidden destination/authority changes leaked')
    check_layout(page, result, 'warm-scrub'); save_shot(page, output, result, 'warm-scrub')
    result['steps'] = ['real renderer/controller mount seam; no product QA global', 'warm source/preview/raw/instrumentation scrub after access loss', 'snapshot invalidation and focus recovery', 'hidden freshness and authority changes do not leak']; handle.dispose()


def check_independent_gates(page, origin, expect, result, output):
    cases = [
      ('source-stale','SOURCE_REVISION_STALE'), ('destination-unknown','DESTINATION_REVISION_UNKNOWN'),
      ('revision-mismatch','DESTINATION_REVISION_STALE'), ('owner-stale','OWNER_STALE'), ('owner-unknown','OWNER_UNKNOWN'),
      ('owner-conflict','OWNER_CONFLICT'), ('owner-other','OWNER_NOT_PRINCIPAL'), ('hold-active','HOLD_ACTIVE'),
      ('hold-unknown','HOLD_UNKNOWN'), ('availability','DESTINATION_AVAILABILITY_UNKNOWN'),
      ('destination-denied','DESTINATION_ACCESS_DENIED'), ('source-unknown','SOURCE_ACCESS_UNKNOWN'), ('bytes','DESTINATION_BYTES_UNVERIFIED')]
    results = []
    for mode in ['BASELINE','CANDIDATE']:
        for kind, reason in cases:
            handle = mount_synthetic(page, origin, expect)
            activate(page, '#' + mode.lower(), 'Diagnostic mode')
            activate(page, '#preview-button', 'Initial checked preview')
            handle.evaluate('''async (s, kind) => {
              const a=s.model.access;
              if(kind==='source-stale') a.revisionFreshnessBySourceId.A='STALE';
              if(kind==='destination-unknown') a.revisionFreshnessBySourceId.B='UNKNOWN';
              if(kind==='revision-mismatch') a.currentRevisionTokenBySourceId.B='fictional-other-revision';
              if(kind==='owner-stale') a.workEvent.ownerFreshness='STALE';
              if(kind==='owner-unknown') a.workEvent.ownerFreshness='UNKNOWN';
              if(kind==='owner-conflict') a.workEvent.ownerIds.push('researcher-beta');
              if(kind==='owner-other') a.workEvent.ownerIds=['researcher-beta'];
              if(kind==='hold-active') a.workEvent.hold='ACTIVE';
              if(kind==='hold-unknown') a.workEvent.hold='UNKNOWN';
              if(kind==='availability') a.sourceObservationState.B={availability:'UNKNOWN',reason:'HTTP_404'};
              if(kind==='destination-denied') a.sourceAccess.B='DENIED';
              if(kind==='source-unknown') a.sourceAccess.A='UNKNOWN';
              if(kind==='bytes') s.model.verifications.B=await s.packet.verifyRepresentation({...s.model.fixture.sources[1].representation,claimedDigest:'0'.repeat(64)});
              s.controller.closeSource();
            }''', kind)
            expect(page.locator('#preview-section')).to_have_count(0)
            expect(page.locator('#workflow-controls')).to_contain_text('Supplied inputs changed')
            handle.evaluate("s => {s.controller.withholdSource('B');s.controller.restoreSource('B');}")
            activate(page, '#preview-button', 'Re-evaluate changed fixed inputs')
            expect(page.locator('#preview-section h2')).to_have_text('PROPOSED · BLOCKED')
            expect(page.locator('#block-reasons')).to_contain_text(reason)
            expect(page.locator('#preview-section')).to_contain_text('scientific effect NONE; no resulting provider identity')
            if kind == 'source-stale':
                expect(page.locator('#preview-section')).to_contain_text('Revision (recorded = observed): fictional-A-revision-1; freshness STALE')
            if kind == 'revision-mismatch':
                expect(page.locator('#preview-section')).to_contain_text('Recorded revision: fictional-B-revision-1; observed revision: fictional-other-revision; freshness CURRENT')
            results.append({'mode':mode,'mutation':kind,'expected_block':reason,'passed':True}); handle.dispose()
    handle = mount_synthetic(page, origin, expect)
    activate(page, '#toggle-B', 'Exclude B'); activate(page, '#preview-button', 'Check excluded context')
    expect(page.locator('#block-reasons')).to_contain_text('DESTINATION_CONTEXT_EXCLUDED_FROM_PACKET')
    handle.evaluate("s => {s.model.access.workEvent.hold='ACTIVE';s.model.access.revisionFreshnessBySourceId.A='STALE';s.controller.restoreSource('B');s.controller.showPreview();}")
    expect(page.locator('#block-reasons')).to_contain_text('HOLD_ACTIVE'); expect(page.locator('#block-reasons')).to_contain_text('SOURCE_REVISION_STALE')
    result['independent_controls'] = results; result['steps'] = ['26 independent blockers preserve refusal in both modes', 'warm input changes invalidate old previews', 'matching token still shows STALE; mismatched observed token shown explicitly', 'restoring B does not clear independent HOLD/revision blocks']
    check_layout(page,result,'independent-blocks');save_shot(page,output,result,'independent-blocks','#preview-section');handle.dispose()


def check_refusal(page, origin, expect, result, kind, output):
    fixture = json.loads((ROOT/'fixtures/packet.json').read_text())
    if kind == 'public': fixture['access']['audience']='PUBLIC'
    elif kind == 'denied': fixture['access']['sourceAccess']['B']='DENIED'
    else: fixture={'synthetic':True,'unexpected':'FICTIONAL invalid fixture'}
    page.route(origin+'fixtures/packet.json',lambda route:route.fulfill(status=200,content_type='application/json',body=json.dumps(fixture)))
    page.goto(origin)
    if kind == 'invalid':
        expect(page.locator('#status')).to_have_text('Local fictional fixture could not be verified. The probe is unavailable; no action was performed.')
        expect(page.locator('main > *')).to_have_count(0)
    else:
        expect(page.locator('#status')).to_contain_text('B is not visible under current fixture access; membership not disclosed')
        expect(page.locator('#open-B')).to_have_count(0)
        activate(page,'#candidate','Diagnostic mode');expect(page.locator('#toggle-B')).to_have_count(0)
        activate(page,'#preview-button','Check denied proposal')
        expect(page.locator('#preview-section h2')).to_have_text('PROPOSED · BLOCKED')
        for hidden in ['PRIVATE_CANARY_B','fictional:b:resource-001','R1 →']:
            require(hidden not in page.locator('body').text_content(), 'Denied output leaked')
        if kind == 'public':
            expect(page.locator('#open-C')).to_have_count(0);require('PRIVATE_CANARY_C' not in page.locator('body').text_content(),'Public C leak')
    result['steps']=['fixed fixture refusal/redaction; static fixture is not a real access boundary']
    check_layout(page,result,kind);save_shot(page,output,result,kind)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    output=parser.parse_args().output;output.mkdir(parents=True,exist_ok=True)
    protocol_path=ROOT/'verification/comparison-protocol.json'
    report={'scientific_effect':'NONE','browser_run_started':False,'source_local_commit':SOURCE_COMMIT,'cases':[],
            'protocol':json.loads(protocol_path.read_text()),'protocol_sha256':sha256(protocol_path.read_bytes()).hexdigest(),
            'limitations':['Headless packaged Chrome and viewport/text-size simulation only','No timing, human usability, comprehension or speedup inference','Static synthetic fixture is not a security boundary','Navigation reset does not prove BFCache without persisted pageshow','Historical 9070px is a preview-section height, not page height']}
    try:
        report['checked_commit']=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
        report['tree']=subprocess.check_output(['git','rev-parse','HEAD^{tree}'],cwd=ROOT,text=True).strip()
        require(not os.environ.get('GITHUB_SHA') or os.environ['GITHUB_SHA']==report['checked_commit'],'Runner commit mismatch')
        report['run_id']=os.environ.get('GITHUB_RUN_ID');report['run_attempt']=os.environ.get('GITHUB_RUN_ATTEMPT')
        report['source_sha256']={name:sha256((ROOT/name).read_bytes()).hexdigest() for name in ASSETS}
        report['playwright']=importlib.metadata.version('playwright')
        from playwright.sync_api import sync_playwright,expect
        executable=Path('/opt/google/chrome/chrome');require(executable.is_file(),'Packaged Chrome missing')
        report['browser_executable']=str(executable)
        with executable.open('rb') as binary:report['browser_executable_sha256']=file_digest(binary,'sha256').hexdigest()
        report['runner_image_os']=os.environ.get('ImageOS');report['runner_image_version']=os.environ.get('ImageVersion')
        with local_assets() as origin,sync_playwright() as playwright:
            browser=playwright.chromium.launch(channel='chrome',chromium_sandbox=True)
            try:
                report['browser_run_started']=True;report['browser']=browser.version;report['chromium_sandbox']=True
                conditions=[('desktop',1200,900,1),('mobile390',390,844,1),('mobile320',320,844,1),('large390',390,844,2),('large320',320,844,2)]
                cases=[(f'{condition}-{mode.lower()}',condition,width,height,scale,mode,'flow') for condition,width,height,scale in conditions for mode in ['BASELINE','CANDIDATE']]
                cases += [(kind,kind,390,844,1,None,kind) for kind in ['public','denied','invalid']]
                cases += [(f'warm-{mode.lower()}','warm',390,844,1,mode,'warm') for mode in ['BASELINE','CANDIDATE']]
                cases += [('independent-gates','independent',390,844,1,None,'gates')]
                for label,condition,width,height,scale,mode,kind in cases:
                    result={'case':label,'condition':condition,'viewport':{'width':width,'height':height},'text_scale':scale,'mode':mode,'reduced_motion':'reduce','passed':False,'steps':[]};report['cases'].append(result)
                    context=browser.new_context(viewport=result['viewport'],reduced_motion='reduce')
                    requests,console,errors,dialogs=[],[],[],[]
                    context.on('request',lambda request:requests.append({'url':request.url,'method':request.method,'resource_type':request.resource_type,'has_post_data':request.post_data is not None}))
                    page=context.new_page();page.set_default_timeout(15000)
                    page.add_init_script("window.__browserCheckPageShows=[];window.addEventListener('pageshow',event=>window.__browserCheckPageShows.push(event.persisted));")
                    page.on('console',lambda message:console.append({'type':message.type,'text':message.text}))
                    page.on('pageerror',lambda error:errors.append(str(error)))
                    def on_dialog(dialog):dialogs.append({'type':dialog.type,'message':dialog.message});dialog.dismiss()
                    page.on('dialog',on_dialog)
                    try:
                        if kind=='flow':check_flow(page,origin,expect,result,output,scale,mode)
                        elif kind=='warm':check_warm(page,origin,expect,result,output,mode)
                        elif kind=='gates':check_independent_gates(page,origin,expect,result,output)
                        else:check_refusal(page,origin,expect,result,kind,output)
                        result['storage']=storage_snapshot(context,page);validate_storage(result['storage']);validate_requests(requests,origin)
                        require(not errors and not dialogs,'Page errors or dialogs');require(not [x for x in console if x['type']=='error'],'Console errors')
                        result['passed']=True
                    except Exception:
                        result['error']=traceback.format_exc()
                        try:save_shot(page,output,result,'failure')
                        except Exception:result['screenshot_error']=traceback.format_exc()
                    finally:
                        result['requests']=requests;result['console']=console;result['page_errors']=errors;result['dialogs']=dialogs;context.close()
            finally:browser.close()
        report['passed']=report_passes(report)
        if report['passed']:
            rows=[case['measurement'] for case in report['cases'] if 'measurement' in case]
            report['comparison']=comparison_summary(rows)
            report['historical_preview_geometry']=[{'mode':row['mode'],'old_preview_section_height_px':9070,'new_default_preview_section_height_px':row['geometry_default']['preview_height_px'],'new_expanded_preview_section_height_px':row['geometry_expanded']['preview_height_px'],'new_document_height_px':row['geometry_default']['document_height_px'],'scope':'320px viewport and 200% root text; geometric observation only'} for row in rows if row['condition']=='large320']
    except Exception:
        report['passed']=False;report['error']=traceback.format_exc()
    finally:(output/'report.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps(report,indent=2,sort_keys=True));return 0 if report['passed'] else 1

if __name__=='__main__':raise SystemExit(main())
