import {validateFixture, verifyRepresentation, projectPacket, previewHandoff, makeReplayKey} from './packet.mjs';
const REQUEST = Object.freeze({sourceId: 'A', destinationSourceId: 'B', purpose: 'explanatory_update', workEventId: 'W1'});
export function createController(model, render) {
  let mode = 'BASELINE', withheld = [], openSourceId = null, sourceOpenCounts = {}, preview = null, previous = null;
  const packet = () => projectPacket(model.fixture, {withheldSourceIds: withheld}, model.access, model.verifications);
  function emit() {
    const p = packet();
    if (openSourceId && !p.sources.some(s => s.id === openSourceId)) openSourceId = null;
    // Recheck all inputs; never replay a cached preview after access or ownership changes.
    if (preview) preview = previewHandoff(model.fixture, {withheldSourceIds: withheld}, model.access, REQUEST, model.verifications);
    makeReplayKey(model.fixture.fixtureVersion, {withheldSourceIds: withheld}, model.access, model.verifications);
    const allowedCounts = Object.fromEntries(Object.entries(sourceOpenCounts).filter(([id]) => p.sources.some(s => s.id === id)));
    const view = {mode, packet: p, preview, openSourceId, sourceOpenCounts: allowedCounts};
    const encoded = JSON.stringify(view);
    if (encoded !== previous) { previous = encoded; render(structuredClone(view)); }
  }
  function known(id) { if (!model.fixture.sources.some(s => s.id === id)) throw new TypeError('Unknown source'); }
  const controller = Object.freeze({
    setMode(next) { if (!['BASELINE', 'CANDIDATE'].includes(next)) throw new TypeError('Unknown mode'); mode = next; if (next === 'BASELINE') preview = null; emit(); },
    openSource(id) {
      known(id); if (!packet().sources.some(s => s.id === id)) { emit(); throw new TypeError('Source access unavailable'); }
      if (openSourceId !== id) { openSourceId = id; sourceOpenCounts[id] = (sourceOpenCounts[id] ?? 0) + 1; }
      emit();
    },
    closeSource() { openSourceId = null; emit(); },
    withholdSource(id) { known(id); if (!withheld.includes(id)) { withheld = [...withheld, id].sort(); preview = null; } emit(); },
    restoreSource(id) { known(id); if (withheld.includes(id)) { withheld = withheld.filter(x => x !== id); preview = null; } emit(); },
    reset() { mode = 'BASELINE'; withheld = []; openSourceId = null; sourceOpenCounts = {}; preview = null; emit(); },
    showPreview() { preview = previewHandoff(model.fixture, {withheldSourceIds: withheld}, model.access, REQUEST, model.verifications); emit(); }
  });
  emit(); return controller;
}
function node(tag, text, className) {
  const el = document.createElement(tag); if (text !== undefined) el.textContent = text; if (className) el.className = className; return el;
}
function paragraph(parent, text) { parent.append(node('p', text)); }
function button(parent, id, text, action) { const el = node('button', text); el.id = id; el.type = 'button'; el.addEventListener('click', action); parent.append(el); return el; }
function section(parent, title) { const el = node('section', undefined, 'card'); el.append(node('h2', title)); parent.append(el); return el; }
function sourceBody(parent, source) { const body = node('pre', source.representation.body, 'source-body'); parent.append(body); }
function sourcePassport(parent, s) {
  const lines = [
    ['Source date', s.sourceDate], ['Observed at', s.observedAt], ['Scope', s.scope],
    ['Resource identity', s.resourceId], ['Observation', s.observationId], ['Revision', s.revisionToken],
    ['Representation', `${s.representation.id} · ${s.representation.kind}`],
    ['Byte evidence', `${s.verification.state} · ${s.representation.digestAlgorithm}/${s.representation.digestEncoding} · ${s.representation.byteCount} UTF-8 bytes`],
    ['Computed digest', s.verification.computedDigest ?? s.verification.failureReason],
    ['Availability observation', s.availability], ['Source owner reference', s.ownerRef], ['Review reference', s.reviewRef]
  ];
  const list = node('dl'); for (const [label, value] of lines) { list.append(node('dt', label), node('dd', value)); } parent.append(list);
}
async function start() {
  const content = document.getElementById('content'), live = document.getElementById('status');
  const response = await fetch('./fixtures/packet.json');
  if (!response.ok) throw new Error('Local fixture unavailable');
  const fixture = validateFixture(await response.json());
  const verifications = Object.fromEntries(await Promise.all(fixture.sources.map(async s => [s.id, await verifyRepresentation(s.representation)])));
  const model = {fixture, access: structuredClone(fixture.access), verifications};
  let controller, lastOpen = null;
  function render(view) {
    const focusId = document.activeElement?.id;
    const returnId = !view.openSourceId && lastOpen ? `open-${lastOpen}` : focusId;
    lastOpen = view.openSourceId;
    document.getElementById('baseline').setAttribute('aria-pressed', String(view.mode === 'BASELINE'));
    document.getElementById('candidate').setAttribute('aria-pressed', String(view.mode === 'CANDIDATE'));
    content.replaceChildren();
    const intro = section(content, view.mode === 'BASELINE' ? 'Baseline · source reading sheets' : 'Candidate · hypothetical packet');
    paragraph(intro, 'Same fictional sources, routes and Work Event in both modes. Withholding changes only disposable packet membership. It does not change a provider file or permission.');
    paragraph(intro, 'The source snapshot dates and current observation dates are different facts. No live service is connected.');
    if (view.mode === 'CANDIDATE') {
      const controls = node('div', undefined, 'controls'); intro.append(controls);
      const B = view.packet.sources.find(s => s.id === 'B');
      if (B) { const toggle = button(controls, 'toggle-B', B.included ? 'Withhold B from packet' : 'Restore B to packet', () => B.included ? controller.withholdSource('B') : controller.restoreSource('B')); toggle.setAttribute('aria-pressed', String(!B.included)); }
      button(controls, 'preview-button', 'Prepare proposed preview', () => controller.showPreview());
    }
    const directory = section(content, 'Source directory');
    for (const s of view.packet.sources) {
      const card = node('article', undefined, 'source'); card.append(node('h3', `${s.id} · ${s.title}`));
      paragraph(card, `${s.included ? 'Included' : 'Excluded'} in this hypothetical packet · Source date ${s.sourceDate} · Observation ${s.observedAt}`);
      paragraph(card, `Scope: ${s.scope}`);
      button(card, `open-${s.id}`, `Read source ${s.id} and passport`, () => controller.openSource(s.id));
      paragraph(card, `Source opens: ${view.sourceOpenCounts[s.id] ?? 0}. These counts do not distinguish necessary rechecks from avoidable repetition.`);
      directory.append(card);
    }
    if (view.openSourceId) {
      const s = view.packet.sources.find(s => s.id === view.openSourceId), panel = section(content, `Source ${s.id} · exact fictional snapshot`);
      panel.id = 'source-panel'; panel.setAttribute('aria-label', `Source ${s.id} details`);
      button(panel, 'close-source', `Close source ${s.id}`, () => controller.closeSource()); sourcePassport(panel, s); sourceBody(panel, s);
    }
    const routes = section(content, 'Recorded route sheets');
    for (const r of view.packet.routes) {
      const card = node('article', undefined, 'source'); card.append(node('h3', `${r.id} → ${r.targetId}`));
      paragraph(card, `Recorded rule: ALL of ${r.sourceIds.join(', ')}. Application: ${r.applicationState}. Observation: ${r.observationId}.`);
      if (view.mode === 'CANDIDATE') paragraph(card, r.missingSourceIds.length ? `Required source excluded from this hypothetical packet: ${r.missingSourceIds.join(', ')}` : 'All recorded inputs included in this hypothetical packet');
      paragraph(card, r.id === 'R2' ? 'Separately recorded, unassessed route. No scientific acceptance is implied.' : 'Packet membership does not determine target truth or review.');
      routes.append(card);
    }
    for (const t of view.packet.targets) paragraph(routes, `Target ${t.id}: truth label ${t.truthLabel}; review label ${t.reviewLabel}; observation ${t.observationId}.`);
    paragraph(routes, `Engineering ${view.packet.engineering.id}: ${view.packet.engineering.state}. ${view.packet.engineering.scope}. Observation ${view.packet.engineering.observationId}.`);
    const coordination = section(content, 'Work Event and handoff reading sheet');
    if (view.packet.workEvent) {
      const w = view.packet.workEvent;
      paragraph(coordination, `${w.id}: owner ${w.ownerIds.join(', ') || 'unknown'}; ownership ${w.ownerFreshness}; HOLD ${w.hold}; observed ${w.observedAt}; observation ${w.observationId}.`);
    }
    paragraph(coordination, 'Single permitted fictional proposal: source A → narrative B; purpose explanatory_update; authority W1; audience OWNER; scientific effect NONE. Verify exact input/destination revisions, current ownership, HOLD and access independently.');
    paragraph(coordination, 'A complete proposal remains PROPOSED / PREVIEW_ONLY. It has no resulting provider identity and does not authorize an action. Restoring B changes membership only; every other block remains independent.');
    if (view.preview) {
      const p = view.preview, preview = section(content, `PROPOSED · ${p.eligibility}`);
      paragraph(preview, `Purpose ${p.purpose}; audience ${p.audience}; scientific effect ${p.scientificEffect}`);
      if (p.blockReasons.length) { const list = node('ul'); for (const reason of p.blockReasons) list.append(node('li', reason)); preview.append(list); }
      if (p.input) { preview.append(node('h3', 'Input A')); sourcePassport(preview, p.input); }
      if (p.destination) { preview.append(node('h3', 'Destination B')); sourcePassport(preview, p.destination); }
      if (p.workEvent) paragraph(preview, `${p.workEvent.id} owner ${p.workEvent.ownerIds.join(', ')}; ${p.workEvent.ownerFreshness}; HOLD ${p.workEvent.hold}; observation ${p.workEvent.observationId} at ${p.workEvent.observedAt}`);
      paragraph(preview, p.limitation);
    }
    const visibleB = view.packet.sources.find(s => s.id === 'B');
    const membership = !visibleB ? 'B is not visible under current fixture access; membership not disclosed' : visibleB.included ? 'B included' : 'B excluded from hypothetical packet';
    live.textContent = `${view.mode}. ${membership}. ${view.preview ? `Proposed preview ${view.preview.eligibility}.` : ''}`;
    if (returnId) document.getElementById(returnId)?.focus();
  }
  controller = createController(model, render);
  document.getElementById('baseline').addEventListener('click', () => controller.setMode('BASELINE'));
  document.getElementById('candidate').addEventListener('click', () => controller.setMode('CANDIDATE'));
  document.getElementById('reset').addEventListener('click', () => controller.reset());
  window.addEventListener('pagehide', () => controller.reset());
  window.addEventListener('pageshow', event => { if (event.persisted) controller.reset(); });
}
if (typeof document !== 'undefined') start().catch(() => { document.getElementById('status').textContent = 'Local fictional fixture could not be verified. The probe is unavailable; no action was performed.'; });
