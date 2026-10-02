import {validateFixture, verifyRepresentation, projectPacket, previewHandoff, makeReplayKey} from './packet.mjs';
const REQUEST = Object.freeze({sourceId: 'A', destinationSourceId: 'B', purpose: 'explanatory_update', workEventId: 'W1'});
export function createController(model, render) {
  let mode = 'BASELINE', withheld = [], openSourceId = null, sourceOpenCounts = {}, preview = null;
  let disclosures = {}, events = [], saturated = false, comparisonEligible = true, previous = null;
  let lastInputKey = null, checkedKey = null, visibleIds = null, checkState = 'NOT_REQUESTED';
  let sourceOrigin = null, focusTarget = null, focusVersion = 0;
  function snapshot() {
    const access = structuredClone(model.access), verifications = {...model.verifications};
    const scenario = {withheldSourceIds: [...withheld]};
    const packet = projectPacket(model.fixture, scenario, access, verifications);
    const key = makeReplayKey(model.fixture.fixtureVersion, scenario, access, verifications);
    const ids = packet.sources.map(s => s.id);
    if (visibleIds && JSON.stringify(ids) !== JSON.stringify(visibleIds)) {
      events = []; sourceOpenCounts = {}; disclosures = {}; saturated = false; comparisonEligible = false; focusTarget = 'content'; focusVersion++; sourceOrigin = null;
    }
    visibleIds = ids;
    if (lastInputKey && key !== lastInputKey && checkedKey) { preview = null; checkedKey = null; checkState = 'INVALIDATED'; delete disclosures['raw-preview']; }
    lastInputKey = key;
    if (openSourceId && !ids.includes(openSourceId)) { openSourceId = null; sourceOrigin = null; focusTarget = 'content'; focusVersion++; }
    for (const id of Object.keys(disclosures)) if (id.startsWith('raw-') && id !== 'raw-preview' && !ids.includes(id.slice(4))) delete disclosures[id];
    return {access, verifications, scenario, packet, key, ids};
  }
  function record(type, target, outcome, extra = {}) {
    if (events.length >= 100) { saturated = true; comparisonEligible = false; return; }
    events.push({ordinal: events.length + 1, mode, type, target, outcome, ...extra});
  }
  function emit(sample = snapshot()) {
    const sourceObservations = Object.fromEntries(sample.packet.sources.map(s => [s.id, {
      currentRevisionToken: sample.access.currentRevisionTokenBySourceId[s.id],
      freshness: sample.access.revisionFreshnessBySourceId[s.id], effectiveAccess: 'ALLOWED',
      availability: sample.access.sourceObservationState[s.id].availability
    }]));
    const counts = {sourceOpens: 0, sourceReopens: 0, rawEvidenceExpansions: 0, recheckRequests: 0, previewPassportExposures: 0};
    for (const e of events) {
      if (e.type === 'OPEN_SOURCE' && e.outcome !== 'ALREADY_OPEN' && e.outcome !== 'REFUSED') { counts.sourceOpens++; if (e.outcome === 'REOPENED') counts.sourceReopens++; }
      if (e.type === 'EXPAND_RAW') counts.rawEvidenceExpansions++;
      if (e.type === 'RECHECK_PREVIEW') { counts.recheckRequests++; counts.previewPassportExposures += e.passportExposures; }
    }
    const view = {mode, packet: sample.packet, sourceObservations, preview, checkState, openSourceId,
      sourceOpenCounts: {...sourceOpenCounts}, disclosures: {...disclosures}, focusTarget, focusVersion,
      telemetry: {events: [...events], counts, saturated, comparisonEligible: comparisonEligible && !saturated}};
    const encoded = JSON.stringify(view);
    if (encoded !== previous) { previous = encoded; render(structuredClone(view)); }
  }
  function known(id, sample) { if (!model.fixture.sources.some(s => s.id === id)) { emit(sample); throw new TypeError('Unknown source'); } }
  function clearTrial() { openSourceId = null; sourceOrigin = null; sourceOpenCounts = {}; preview = null; checkedKey = null; checkState = 'NOT_REQUESTED'; disclosures = {}; events = []; saturated = false; comparisonEligible = true; focusTarget = null; focusVersion = 0; }
  const controller = Object.freeze({
    setMode(next) { const sample = snapshot(); if (!['BASELINE', 'CANDIDATE'].includes(next)) { emit(sample); throw new TypeError('Unknown mode'); } const changed = mode !== next; mode = next; if (changed) record('MODE', null, 'CHANGED'); emit(sample); },
    openSource(id, origin = `open-${id}`) {
      const sample = snapshot(); known(id, sample);
      if (!sample.ids.includes(id)) { record('OPEN_SOURCE', null, 'REFUSED'); emit(sample); throw new TypeError('Source access unavailable'); }
      const contextual = mode === 'CANDIDATE' && sample.packet.routes.some(r => r.missingSourceIds.includes(id) && origin === `next-${r.id}-${id}`);
      if (origin !== `open-${id}` && !contextual) { emit(sample); throw new TypeError('Unknown source trigger'); }
      const already = openSourceId === id, prior = sourceOpenCounts[id] ?? 0;
      if (!already) { openSourceId = id; sourceOpenCounts[id] = Math.min(100, prior + 1); } sourceOrigin = origin;
      focusTarget = 'source-panel'; focusVersion++;
      record('OPEN_SOURCE', id, already ? 'ALREADY_OPEN' : prior ? 'REOPENED' : 'OPENED'); emit(sample);
    },
    closeSource() { const sample = snapshot(); const id = openSourceId; if (id) { focusTarget = sourceOrigin; focusVersion++; } openSourceId = null; sourceOrigin = null; if (id) record('CLOSE_SOURCE', id, 'CLOSED'); emit(sample); },
    withholdSource(id) { known(id, snapshot()); const changed = !withheld.includes(id); if (changed) withheld = [...withheld, id].sort(); const sample = snapshot(); record('WITHHOLD', sample.ids.includes(id) ? id : null, changed ? 'CHANGED' : 'UNCHANGED'); emit(sample); },
    restoreSource(id) { known(id, snapshot()); const changed = withheld.includes(id); if (changed) withheld = withheld.filter(x => x !== id); const sample = snapshot(); record('RESTORE', sample.ids.includes(id) ? id : null, changed ? 'CHANGED' : 'UNCHANGED'); emit(sample); },
    setDisclosure(id, expanded) {
      const sample = snapshot(); const valid = id === 'instrumentation' || (id === 'raw-preview' && preview) || sample.ids.some(source => id === `raw-${source}`);
      if (!valid || typeof expanded !== 'boolean') { emit(sample); throw new TypeError('Unknown disclosure'); }
      if (!!disclosures[id] !== expanded) { disclosures[id] = expanded; if (expanded) record(id === 'instrumentation' ? 'EXPAND_METRICS' : 'EXPAND_RAW', id === 'raw-preview' || id === 'instrumentation' ? null : id.slice(4), 'EXPANDED'); } emit(sample);
    },
    startTrial() { clearTrial(); emit(snapshot()); },
    reset() { mode = 'BASELINE'; withheld = []; clearTrial(); lastInputKey = null; visibleIds = null; emit(snapshot()); },
    showPreview() {
      const sample = snapshot(); preview = previewHandoff(model.fixture, sample.scenario, sample.access, REQUEST, sample.verifications);
      checkedKey = sample.key; checkState = 'CURRENT_FOR_FIXED_INPUTS';
      record('RECHECK_PREVIEW', null, preview.eligibility, {passportExposures: Number(!!preview.input) + Number(!!preview.destination)}); emit(sample);
    }
  });
  emit(); return controller;
}
function node(tag, text, className) {
  const el = document.createElement(tag); if (text !== undefined) el.textContent = text; if (className) el.className = className; return el;
}
function paragraph(parent, text) { parent.append(node('p', text)); }
function button(parent, id, text, action) { const el = node('button', text); el.id = id; el.type = 'button'; el.addEventListener('click', action); parent.append(el); return el; }
function section(parent, title, id) { const el = node('section', undefined, 'card'); if (id) el.id = id; el.append(node('h2', title)); parent.append(el); return el; }
function sourceBody(parent, source) { parent.append(node('pre', source.representation.body, 'source-body')); }
function coreEvidence(parent, sources, observations) {
  const box = node('div', undefined, 'core-evidence');
  for (const s of sources) {
    const o = observations[s.id], entry = node('article', undefined, 'evidence-source');
    entry.append(node('h3', `${s.id} · ${s.id === 'A' ? 'Input' : s.id === 'B' ? 'Destination' : 'Source'}`));
    paragraph(entry, `Resource: ${s.resourceId}`);
    const recorded = s.revisionToken, observed = o.currentRevisionToken;
    paragraph(entry, recorded === observed ? `Revision (recorded = observed): ${recorded}; freshness ${o.freshness}` : `Recorded revision: ${recorded}; observed revision: ${observed}; freshness ${o.freshness}`);
    paragraph(entry, `Representation: ${s.representation.id}; ${s.representation.kind}`);
    paragraph(entry, `Byte evidence: ${s.verification.state}${s.verification.failureReason ? ` (${s.verification.failureReason})` : ''}`);
    box.append(entry);
  }
  for (const [label, get] of [
    ['Source date', s => s.sourceDate], ['Observation date', s => s.observedAt], ['Scope', s => s.scope],
    ['Effective access / availability', s => `${observations[s.id].effectiveAccess} / ${observations[s.id].availability}`]
  ]) {
    const groups = new Map(); for (const s of sources) { const value = get(s); groups.set(value, [...(groups.get(value) ?? []), s.id]); }
    for (const [value, ids] of groups) paragraph(box, `${label} ${ids.join('/')}${ids.length > 1 ? ' (shared)' : ''}: ${value}`);
  }
  parent.append(box);
}
function rawEvidence(parent, sources) {
  for (const s of sources) paragraph(parent, `${s.id}: observation ${s.observationId}; source owner reference ${s.ownerRef}; review reference ${s.reviewRef}; ${s.representation.digestAlgorithm}/${s.representation.digestEncoding}; ${s.representation.byteCount} UTF-8 bytes; computed digest ${s.verification.computedDigest ?? s.verification.failureReason}.`);
}
let activeMount;
export function mountProbe(model) {
  activeMount?.abort(); const shell = new AbortController(); activeMount = shell;
  const content = document.getElementById('content'), live = document.getElementById('status');
  let controller, lastFocusVersion = 0, lastOpenId = null;
  function disclosure(parent, id, label, view, fill) {
    const details = node('details'), summary = node('summary', label); details.id = id; summary.id = `summary-${id}`;
    details.open = !!view.disclosures[id]; details.append(summary); fill(details); parent.append(details);
    details.addEventListener('toggle', () => { if (details.isConnected) controller.setDisclosure(id, details.open); });
    return details;
  }
  function render(view) {
    const activeId = document.activeElement?.id, priorOpenId = lastOpenId; lastOpenId = view.openSourceId;
    document.getElementById('baseline').setAttribute('aria-pressed', String(view.mode === 'BASELINE'));
    document.getElementById('candidate').setAttribute('aria-pressed', String(view.mode === 'CANDIDATE'));
    content.replaceChildren();
    const intro = section(content, view.mode === 'BASELINE' ? 'Baseline · common workflow' : 'Candidate · common workflow', 'workflow-controls');
    paragraph(intro, 'Same records, controls and evidence in both modes. Candidate adds contextual route cues only. Exclusion changes this hypothetical packet, never a provider file or permission.');
    const controls = node('div', undefined, 'controls'); intro.append(controls);
    const B = view.packet.sources.find(s => s.id === 'B');
    if (B) { const toggle = button(controls, 'toggle-B', B.included ? 'Withhold B from packet' : 'Restore B to packet', () => B.included ? controller.withholdSource('B') : controller.restoreSource('B')); toggle.setAttribute('aria-pressed', String(!B.included)); }
    button(controls, 'preview-button', 'Re-evaluate fixed-fixture checks and prepare preview', () => controller.showPreview());
    paragraph(intro, 'Uses previously computed byte verification and frozen observations. No live service is contacted and no new digest is computed. Observed current revision in this fixture is a supplied observation.');
    if (view.checkState === 'INVALIDATED') paragraph(intro, 'Supplied inputs changed. Re-evaluate the fixed-fixture checks before using a preview.');
    const routes = section(content, 'Recorded route sheets', 'route-sheets');
    for (const r of view.packet.routes) {
      const card = node('article', undefined, 'source'); card.id = `route-${r.id}`; card.append(node('h3', `${r.id} → ${r.targetId}`));
      paragraph(card, `Recorded rule: ALL of ${r.sourceIds.join(', ')}. Application: ${r.applicationState}. Observation: ${r.observationId}.`);
      if (view.mode === 'CANDIDATE') {
        paragraph(card, r.missingSourceIds.length ? `Required source excluded from this hypothetical packet: ${r.missingSourceIds.join(', ')}` : 'All recorded inputs included in this hypothetical packet');
        for (const id of r.missingSourceIds) { const trigger = `next-${r.id}-${id}`; button(card, trigger, `Read required source ${id}`, () => controller.openSource(id, trigger)); }
      }
      paragraph(card, r.id === 'R2' ? 'Separately recorded, unassessed route. No scientific acceptance is implied.' : 'Membership does not determine target truth or review.');
      routes.append(card);
    }
    for (const t of view.packet.targets) paragraph(routes, `Target ${t.id}: ${t.truthLabel} / ${t.reviewLabel}; observation ${t.observationId}.`);
    paragraph(routes, `Engineering ${view.packet.engineering.id}: ${view.packet.engineering.state}. ${view.packet.engineering.scope}.`);
    const directory = section(content, 'Source directory', 'source-directory');
    for (const s of view.packet.sources) {
      const row = node('article', undefined, 'source'); row.append(node('h3', `${s.id} · ${s.title}`));
      paragraph(row, `${s.included ? 'Included' : 'Excluded'} in this hypothetical packet; source ${s.sourceDate}; observed ${s.observedAt}. Scope: ${s.scope}`);
      button(row, `open-${s.id}`, `Read source ${s.id} and evidence`, () => controller.openSource(s.id, `open-${s.id}`)); directory.append(row);
    }
    if (view.openSourceId) {
      const s = view.packet.sources.find(s => s.id === view.openSourceId), panel = section(content, `Source ${s.id} · exact fictional snapshot`, 'source-panel');
      panel.tabIndex = -1; panel.setAttribute('aria-label', `Source ${s.id} details`);
      button(panel, 'close-source', `Close source ${s.id}`, () => controller.closeSource());
      coreEvidence(panel, [s], view.sourceObservations); sourceBody(panel, s);
      disclosure(panel, `raw-${s.id}`, 'Raw digest and provenance', view, details => rawEvidence(details, [s]));
    }
    const coordination = section(content, 'Work Event and proposed handoff', 'handoff-sheet');
    const w = view.packet.workEvent;
    if (w) paragraph(coordination, `${w.id}: owner ${w.ownerIds.join(', ') || 'unknown'}; ownership ${w.ownerFreshness}; HOLD ${w.hold}; observed ${w.observedAt}. Observation ${w.observationId}.`);
    else paragraph(coordination, 'Work Event context is not visible under the supplied access decisions.');
    paragraph(coordination, 'A → B; explanatory_update; W1; OWNER audience. A complete proposal is PROPOSED / PREVIEW_ONLY, with scientific effect NONE and no resulting provider identity.');
    if (view.preview) {
      const p = view.preview, preview = section(content, `PROPOSED · ${p.eligibility}`, 'preview-section');
      paragraph(preview, `Purpose ${p.purpose}; audience ${p.audience}; scientific effect ${p.scientificEffect}; no resulting provider identity.`);
      if (p.blockReasons.length) { const list = node('ul'); list.id = 'block-reasons'; for (const reason of p.blockReasons) list.append(node('li', reason)); preview.append(list); }
      const identities = [p.input, p.destination].filter(Boolean); coreEvidence(preview, identities, view.sourceObservations);
      paragraph(preview, 'Fixed-fixture re-evaluation only. No action or completed receipt. W1 ownership and HOLD are shown above; restoring B cannot clear another block.');
      disclosure(preview, 'raw-preview', 'Raw input/destination digest and provenance', view, details => rawEvidence(details, identities));
    }
    const instrumentation = section(content, 'Optional interaction record', 'interaction-record');
    paragraph(instrumentation, 'Actions and evidence exposures are not proof of reading or comprehension. Repeated checks may be necessary.');
    if (view.telemetry.saturated) paragraph(instrumentation, 'Interaction record saturated. This incomplete record cannot support a comparison.');
    disclosure(instrumentation, 'instrumentation', 'Show local interaction counts and sequence', view, details => {
      details.append(node('pre', JSON.stringify(view.telemetry, null, 2), 'source-body'));
      button(details, 'start-trial', 'Clear measurements and close evidence for this task', () => controller.startTrial());
    });
    const membership = !B ? 'B is not visible under current fixture access; membership not disclosed' : B.included ? 'B included' : 'B excluded from hypothetical packet';
    live.textContent = `${view.mode}. ${membership}. ${view.preview ? `Proposed preview ${view.preview.eligibility}.` : ''}`;
    if (view.focusVersion !== lastFocusVersion) {
      lastFocusVersion = view.focusVersion;
      (document.getElementById(view.focusTarget) ?? document.getElementById(`open-${priorOpenId}`) ?? content).focus();
    } else if (activeId) document.getElementById(activeId)?.focus();
  }
  controller = createController(model, render);
  for (const [id, action] of [['baseline', () => controller.setMode('BASELINE')], ['candidate', () => controller.setMode('CANDIDATE')], ['reset', () => controller.reset()]]) document.getElementById(id).addEventListener('click', action, {signal: shell.signal});
  window.addEventListener('pagehide', () => controller.reset(), {signal: shell.signal});
  window.addEventListener('pageshow', event => { if (event.persisted) controller.reset(); }, {signal: shell.signal});
  return controller;
}
async function start() {
  const response = await fetch('./fixtures/packet.json'); if (!response.ok) throw new Error('Local fixture unavailable');
  const fixture = validateFixture(await response.json());
  const verifications = Object.fromEntries(await Promise.all(fixture.sources.map(async s => [s.id, await verifyRepresentation(s.representation)])));
  mountProbe({fixture, access: structuredClone(fixture.access), verifications});
}
if (typeof document !== 'undefined') start().catch(() => { document.getElementById('status').textContent = 'Local fictional fixture could not be verified. The probe is unavailable; no action was performed.'; });
