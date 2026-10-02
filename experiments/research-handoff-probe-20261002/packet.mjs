/** Pure fictional packet projection. No I/O, persistence, clock or write capability. */
const IDS = ['A', 'B', 'C', 'D', 'E'];
const POLICY = 'synthetic-owner-public-v1';
const fixtures = new WeakSet();
const computed = new WeakMap();
const clone = value => structuredClone(value);
const fail = message => { throw new TypeError(message); };
const freeze = value => { if (value && typeof value === 'object') { Object.values(value).forEach(freeze); Object.freeze(value); } return value; };
const exact = (value, keys, name) => {
  if (!value || typeof value !== 'object' || Array.isArray(value) || Object.getPrototypeOf(value) !== Object.prototype) fail(`${name}: object required`);
  if (Object.keys(value).sort().join('|') !== [...keys].sort().join('|')) fail(`${name}: unexpected or missing fields`);
};
const text = (value, name) => { if (typeof value !== 'string' || !value.trim()) fail(`${name}: nonempty string required`); };
const oneOf = (value, allowed, name) => { if (!allowed.includes(value)) fail(`${name}: invalid value`); };
const date = (value, name) => { text(value, name); if (!/^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$/.test(value) || !Number.isFinite(Date.parse(value))) fail(`${name}: ISO time required`); };
const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);
const unique = (values, name) => { if (new Set(values).size !== values.length) fail(`${name}: duplicate identity`); };
const sourceKeys = 'id title resourceId providerRole observationId revisionToken sourceDate observedAt scope audience ownerRef reviewRef representation'.split(' ');
const repKeys = 'id kind encoding digestAlgorithm digestEncoding byteCount claimedDigest body'.split(' ');
function validateRepresentation(rep) {
  exact(rep, repKeys, 'representation');
  for (const k of repKeys.filter(k => k !== 'byteCount')) text(rep[k], `representation.${k}`);
  if (!Number.isSafeInteger(rep.byteCount) || rep.byteCount < 0) fail('representation: byte count');
  oneOf(rep.encoding, ['utf-8'], 'encoding');
}
function validateAccess(access) {
  exact(access, 'principalId audience policyVersion sourceAccess currentRevisionTokenBySourceId revisionFreshnessBySourceId sourceObservationState workEvent'.split(' '), 'access');
  text(access.principalId, 'principal'); text(access.policyVersion, 'policy');
  oneOf(access.audience, ['OWNER', 'PUBLIC'], 'audience');
  for (const key of ['sourceAccess', 'currentRevisionTokenBySourceId', 'revisionFreshnessBySourceId', 'sourceObservationState']) exact(access[key], IDS, key);
  for (const id of IDS) {
    oneOf(access.sourceAccess[id], ['ALLOWED', 'DENIED', 'UNKNOWN'], 'access decision');
    text(access.currentRevisionTokenBySourceId[id], 'revision');
    oneOf(access.revisionFreshnessBySourceId[id], ['CURRENT', 'STALE', 'UNKNOWN'], 'freshness');
    const state = access.sourceObservationState[id];
    exact(state, state?.reason === undefined ? ['availability'] : ['availability', 'reason'], 'observation state');
    oneOf(state.availability, ['AVAILABLE', 'UNKNOWN'], 'availability');
    if (state.reason !== undefined) { oneOf(state.reason, ['HTTP_404', 'PARTIAL_LISTING'], 'availability reason'); if (state.availability !== 'UNKNOWN') fail('unknown availability required for gaps'); }
  }
  const w = access.workEvent;
  exact(w, ['id', 'ownerIds', 'ownerFreshness', 'hold', 'observedAt', 'observationId'], 'work event observation');
  if (w.id !== 'W1' || !Array.isArray(w.ownerIds)) fail('work event authority');
  w.ownerIds.forEach(id => text(id, 'owner')); unique(w.ownerIds, 'owners');
  oneOf(w.ownerFreshness, ['CURRENT', 'STALE', 'UNKNOWN'], 'owner freshness');
  oneOf(w.hold, ['CLEAR', 'ACTIVE', 'UNKNOWN'], 'hold'); date(w.observedAt, 'work event time'); text(w.observationId, 'work event observation');
}
export function validateFixture(input) {
  const f = clone(input);
  exact(f, ['fixtureVersion', 'synthetic', 'recordedRoutesComplete', 'ownerPrincipalId', 'sources', 'routes', 'targets', 'engineering', 'workEvent', 'access', 'benchmarks'], 'fixture');
  if (f.fixtureVersion !== 'handoff-probe-v1' || f.synthetic !== true || f.recordedRoutesComplete !== false || f.ownerPrincipalId !== 'researcher-alpha') fail('fixed fictional fixture required');
  if (!Array.isArray(f.sources) || !same(f.sources.map(s => s.id), IDS)) fail('fixed source IDs required');
  for (const s of f.sources) {
    exact(s, sourceKeys, 'source');
    for (const k of sourceKeys.filter(k => k !== 'representation')) text(s[k], `source.${k}`);
    if (!s.resourceId.startsWith('fictional:') || !s.observationId.startsWith('fictional-')) fail('fictional identity required');
    if (!s.representation.body.includes('FICTIONAL')) fail('fictional body required');
    oneOf(s.audience, ['OWNER', 'PUBLIC'], 'source audience');
    if (s.audience !== ('BC'.includes(s.id) ? 'OWNER' : 'PUBLIC')) fail('fixed source audience required');
    date(s.sourceDate, 'source date'); date(s.observedAt, 'observation date'); validateRepresentation(s.representation);
  }
  for (const field of ['resourceId', 'observationId']) unique(f.sources.map(s => s[field]), field);
  unique(f.sources.map(s => s.representation.id), 'representation IDs');
  const topology = [['R1', ['A', 'B', 'C'], 'T'], ['R2', ['A', 'D'], 'T'], ['R3', ['E'], 'U']];
  if (!Array.isArray(f.routes) || f.routes.length !== 3) fail('fixed routes required');
  f.routes.forEach((r, i) => {
    exact(r, ['id', 'sourceIds', 'targetId', 'operator', 'applicationState', 'observationId'], 'route');
    if (!same([r.id, r.sourceIds, r.targetId], topology[i]) || r.operator !== 'ALL' || r.applicationState !== 'NOT_EVALUATED') fail('fixed ALL topology and unevaluated application required');
    text(r.observationId, 'route observation');
  });
  if (!Array.isArray(f.targets) || !same(f.targets.map(t => t.id), ['T', 'U'])) fail('fixed targets required');
  for (const t of f.targets) {
    exact(t, ['id', 'truthLabel', 'reviewLabel', 'observationId'], 'target');
    if (t.truthLabel !== 'UNASSESSED' || t.reviewLabel !== 'NOT_REVIEWED') fail('target status promotion refused');
    text(t.observationId, 'target observation');
  }
  exact(f.engineering, ['id', 'state', 'scope', 'observationId'], 'engineering');
  if (f.engineering.id !== 'G' || f.engineering.state !== 'PASS') fail('fixed engineering record required');
  text(f.engineering.scope, 'engineering scope'); text(f.engineering.observationId, 'engineering observation');
  exact(f.workEvent, ['id', 'scope', 'observationId'], 'work event');
  if (f.workEvent.id !== 'W1') fail('fixed work authority required');
  text(f.workEvent.scope, 'work scope'); text(f.workEvent.observationId, 'work observation');
  validateAccess(f.access);
  if (!Array.isArray(f.benchmarks) || f.benchmarks.length !== 2) fail('two benchmark labels required');
  for (const b of f.benchmarks) { exact(b, ['id', 'label', 'sourceLabels', 'context'], 'benchmark'); text(b.id, 'benchmark ID'); text(b.label, 'label'); text(b.context, 'context'); exact(b.sourceLabels, IDS, 'benchmark labels'); Object.values(b.sourceLabels).forEach(v => text(v, 'source label')); }
  unique(f.benchmarks.map(b => b.id), 'benchmark IDs');
  freeze(f); fixtures.add(f); return f;
}
function requireFixture(f) { if (!fixtures.has(f)) fail('validated fixture required'); }
function normalizeScenario(scenario) {
  exact(scenario, ['withheldSourceIds'], 'scenario');
  if (!Array.isArray(scenario.withheldSourceIds)) fail('withheld IDs required');
  scenario.withheldSourceIds.forEach(id => oneOf(id, IDS, 'withheld ID'));
  unique(scenario.withheldSourceIds, 'withheld IDs'); return [...scenario.withheldSourceIds].sort();
}
export function resolveKnownKey(f, key) { requireFixture(f); return IDS.includes(key) ? { state: 'LINKED', sourceId: key } : { state: 'UNLINKED' }; }
const verificationBinding = rep => JSON.stringify([rep.body, rep.encoding, rep.digestAlgorithm, rep.digestEncoding, rep.byteCount, rep.claimedDigest]);
export async function verifyRepresentation(input) {
  const rep = clone(input);
  const base = { state: 'UNVERIFIED', algorithm: rep?.digestAlgorithm ?? null, encoding: rep?.digestEncoding ?? null, computedDigest: null, byteCount: null, verificationMethod: 'WEB_CRYPTO_SHA256_UTF8' };
  if (rep?.digestAlgorithm !== 'sha256') return freeze({ ...base, failureReason: 'UNSUPPORTED_ALGORITHM' });
  if (rep.encoding !== 'utf-8' || rep.digestEncoding !== 'hex' || typeof rep.body !== 'string') return freeze({ ...base, failureReason: 'UNSUPPORTED_ENCODING' });
  const bytes = new TextEncoder().encode(rep.body);
  const digest = [...new Uint8Array(await globalThis.crypto.subtle.digest('SHA-256', bytes))].map(b => b.toString(16).padStart(2, '0')).join('');
  const reason = bytes.length !== rep.byteCount ? 'BYTE_COUNT_MISMATCH' : digest !== rep.claimedDigest ? 'DIGEST_MISMATCH' : null;
  const result = freeze({ ...base, computedDigest: digest, byteCount: bytes.length, state: reason ? 'UNVERIFIED' : 'VERIFIED', ...(reason ? { failureReason: reason } : {}) });
  if (!reason) computed.set(result, verificationBinding(rep));
  return result;
}
const isVerified = (rep, v) => v?.state === 'VERIFIED' && computed.get(v) === verificationBinding(rep);
export function classifyByteRelation(left, right) {
  if (!isVerified(left.representation, left.verification) || !isVerified(right.representation, right.verification)) return 'NOT_COMPARABLE';
  if (left.representation.kind !== right.representation.kind) return 'DIFFERENT_REPRESENTATION';
  return left.verification.byteCount === right.verification.byteCount && left.verification.computedDigest === right.verification.computedDigest ? 'EXACT_BYTE_REPLICA' : 'DIFFERENT_BYTES';
}
function allowed(f, s, a) {
  return a.policyVersion === POLICY && a.sourceAccess[s.id] === 'ALLOWED' && (s.audience === 'PUBLIC' || (a.audience === 'OWNER' && a.principalId === f.ownerPrincipalId));
}
function passport(s, v, observation) {
  return { ...clone(s), availability: observation.availability, observationState: clone(observation), verification: isVerified(s.representation, v) ? clone(v) : { state: 'UNVERIFIED', failureReason: v?.failureReason ?? 'NO_BOUND_COMPUTED_VERIFICATION' } };
}
export function projectPacket(f, scenario, access, verifications) {
  requireFixture(f); const withheld = normalizeScenario(scenario); validateAccess(access);
  const visible = f.sources.filter(s => allowed(f, s, access));
  const ids = new Set(visible.map(s => s.id));
  const routes = f.routes.filter(r => r.sourceIds.every(id => ids.has(id))).map(r => ({ ...clone(r), missingSourceIds: r.sourceIds.filter(id => withheld.includes(id)), membershipState: r.sourceIds.some(id => withheld.includes(id)) ? 'REQUIRED_SOURCE_EXCLUDED_FROM_HYPOTHETICAL_PACKET' : 'RECORDED_INPUTS_INCLUDED' }));
  const targets = f.targets.filter(t => routes.some(r => r.targetId === t.id));
  const sources = visible.map(s => ({ ...passport(s, verifications[s.id], access.sourceObservationState[s.id]), included: !withheld.includes(s.id) }));
  return freeze({ fixtureVersion: f.fixtureVersion, synthetic: true, recordedRoutesComplete: false, coverageNotice: 'Recorded route coverage is incomplete. No theorem-wide conclusion; application remains NOT_EVALUATED.', sources, sourceCount: sources.length, routes, routeCount: routes.length, targets: clone(targets), engineering: clone(f.engineering), workEvent: ids.has('A') && ids.has('B') ? clone(access.workEvent) : null });
}
export function previewHandoff(f, scenario, access, request, verifications) {
  requireFixture(f); const withheld = normalizeScenario(scenario); validateAccess(access);
  exact(request, ['sourceId', 'destinationSourceId', 'purpose', 'workEventId'], 'handoff request');
  if (!same([request.sourceId, request.destinationSourceId, request.purpose, request.workEventId], ['A', 'B', 'explanatory_update', 'W1'])) fail('only fixed A to B explanatory W1 preview is supported');
  const reasons = [], A = f.sources[0], B = f.sources[1];
  for (const [s, prefix] of [[A, 'SOURCE'], [B, 'DESTINATION']]) {
    if (withheld.includes(s.id)) reasons.push(`${prefix}_CONTEXT_EXCLUDED_FROM_PACKET`);
    if (!allowed(f, s, access)) { reasons.push(`${prefix}_ACCESS_${access.sourceAccess[s.id] === 'UNKNOWN' ? 'UNKNOWN' : 'DENIED'}`); continue; }
    const freshness = access.revisionFreshnessBySourceId[s.id];
    if (freshness === 'UNKNOWN') reasons.push(`${prefix}_REVISION_UNKNOWN`);
    else if (freshness !== 'CURRENT' || access.currentRevisionTokenBySourceId[s.id] !== s.revisionToken) reasons.push(`${prefix}_REVISION_STALE`);
    if (access.sourceObservationState[s.id].availability !== 'AVAILABLE') reasons.push(`${prefix}_AVAILABILITY_UNKNOWN`);
    if (!isVerified(s.representation, verifications[s.id])) reasons.push(`${prefix}_BYTES_UNVERIFIED`);
  }
  const w = access.workEvent;
  if (allowed(f, A, access) && allowed(f, B, access)) {
  if (!w.ownerIds.length || w.ownerFreshness === 'UNKNOWN') reasons.push('OWNER_UNKNOWN');
  if (w.ownerFreshness === 'STALE') reasons.push('OWNER_STALE');
  if (w.ownerIds.length > 1) reasons.push('OWNER_CONFLICT');
  if (w.ownerIds.length === 1 && w.ownerIds[0] !== access.principalId) reasons.push('OWNER_NOT_PRINCIPAL');
  if (w.hold !== 'CLEAR') reasons.push(`HOLD_${w.hold}`);
  }
  const identity = s => { const p = passport(s, verifications[s.id], access.sourceObservationState[s.id]); delete p.representation.body; return p; };
  return freeze({ status: 'PROPOSED', eligibility: reasons.length ? 'BLOCKED' : 'PREVIEW_ONLY', blockReasons: reasons, scientificEffect: 'NONE', purpose: request.purpose, audience: access.audience, input: allowed(f, A, access) ? identity(A) : null, destination: allowed(f, B, access) ? identity(B) : null, workEvent: allowed(f, A, access) && allowed(f, B, access) ? clone(w) : null, limitation: 'Fictional preview only; no action, completed receipt or resulting provider identity. Recheck current source, destination, ownership and HOLD before any separately authorized real action.' });
}
function canonical(value) {
  if (Array.isArray(value)) return value.map(canonical);
  if (value && typeof value === 'object') return Object.fromEntries(Object.keys(value).sort().map(k => [k, canonical(value[k])]));
  return value;
}
export function makeReplayKey(fixtureVersion, scenario, access, verifications) {
  if (fixtureVersion !== 'handoff-probe-v1') fail('unknown fixture version'); validateAccess(access);
  const withheldSourceIds = normalizeScenario(scenario);
  exact(verifications, IDS, 'verification map');
  const verificationProvenance = Object.fromEntries(IDS.map(id => [id, computed.get(verifications[id]) ?? null]));
  return JSON.stringify(canonical({ fixtureVersion, scenario: { withheldSourceIds }, access, verifications, verificationProvenance }));
}
