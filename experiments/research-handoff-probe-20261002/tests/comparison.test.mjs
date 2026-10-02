import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {validateFixture,verifyRepresentation} from '../packet.mjs';
import {createController} from '../app.mjs';
const raw=JSON.parse(await readFile(new URL('../fixtures/packet.json',import.meta.url),'utf8'));
const last=views=>views.at(-1);
async function setup(mode='BASELINE') {const fixture=validateFixture(raw),access=structuredClone(fixture.access),verifications=Object.fromEntries(await Promise.all(fixture.sources.map(async s=>[s.id,await verifyRepresentation(s.representation)])));const views=[];const c=createController({fixture,access,verifications},v=>views.push(v));c.setMode(mode);return {c,views,access,verifications};}
test('model and fixture bytes remain exact across the bounded UI revision',async()=>{
 const expected={'packet.mjs':'a4ae48ec34d48f0d4729a7f55aa1fddad0caf68fe616c5bded743e08257c3412','fixtures/packet.json':'5c419ffbd2d78185cb2837f17b4f56865619800c1db1321db13af6238b244721'};
 for(const [name,digest] of Object.entries(expected)) assert.equal(createHash('sha256').update(await readFile(new URL('../'+name,import.meta.url))).digest('hex'),digest);
});
test('both modes complete the same fixed packet restore and checked proposal without switching',async()=>{
 const outputs=[];
 for(const mode of ['BASELINE','CANDIDATE']) {const {c,views}=await setup(mode);c.withholdSource('B');c.showPreview();assert.equal(last(views).preview.eligibility,'BLOCKED');c.restoreSource('B');c.showPreview();assert.equal(last(views).mode,mode);assert.equal(last(views).checkState,'CURRENT_FOR_FIXED_INPUTS');outputs.push(last(views).preview);}
 assert.deepEqual(outputs[0],outputs[1]);
});
test('observation evidence is exact filtered and keys remain internal',async()=>{
 const {c,views,access}=await setup();c.showPreview();let v=last(views);assert.equal(v.sourceObservations.B.currentRevisionToken,'fictional-B-revision-1');assert.equal(v.sourceObservations.B.freshness,'CURRENT');assert.equal(v.sourceObservations.B.effectiveAccess,'ALLOWED');assert.equal(JSON.stringify(v).includes('verificationProvenance'),false);
 access.sourceAccess.B='DENIED';c.closeSource();v=last(views);assert.equal('B' in v.sourceObservations,false);assert.equal(v.preview,null);assert.equal(v.checkState,'INVALIDATED');assert.equal(JSON.stringify(v).includes('PRIVATE_CANARY_B'),false);
});
test('every supplied-input gate remains independent in both modes including matching stale tokens',async()=>{
 const changes=[['SOURCE_REVISION_STALE',a=>a.revisionFreshnessBySourceId.A='STALE'],['DESTINATION_REVISION_UNKNOWN',a=>a.revisionFreshnessBySourceId.B='UNKNOWN'],['DESTINATION_REVISION_STALE',a=>a.currentRevisionTokenBySourceId.B='fictional-other-revision'],['OWNER_STALE',a=>a.workEvent.ownerFreshness='STALE'],['OWNER_UNKNOWN',a=>a.workEvent.ownerFreshness='UNKNOWN'],['OWNER_CONFLICT',a=>a.workEvent.ownerIds.push('researcher-beta')],['OWNER_NOT_PRINCIPAL',a=>a.workEvent.ownerIds=['researcher-beta']],['HOLD_ACTIVE',a=>a.workEvent.hold='ACTIVE'],['HOLD_UNKNOWN',a=>a.workEvent.hold='UNKNOWN'],['DESTINATION_AVAILABILITY_UNKNOWN',a=>a.sourceObservationState.B={availability:'UNKNOWN',reason:'HTTP_404'}],['DESTINATION_ACCESS_DENIED',a=>a.sourceAccess.B='DENIED'],['SOURCE_ACCESS_UNKNOWN',a=>a.sourceAccess.A='UNKNOWN']];
 for(const mode of ['BASELINE','CANDIDATE'])for(const [reason,edit] of changes){const {c,views,access}=await setup(mode);edit(access);c.withholdSource('B');c.restoreSource('B');c.showPreview();assert.ok(last(views).preview.blockReasons.includes(reason),mode+reason);assert.equal(last(views).preview.eligibility,'BLOCKED');assert.equal(last(views).preview.scientificEffect,'NONE');}
});
test('explicit requests are logged separately from source opens and benign renders',async()=>{
 const {c,views}=await setup();assert.equal(typeof c.startTrial,'function');c.withholdSource('B');c.startTrial();assert.equal(last(views).telemetry.events.length,0);c.openSource('B');c.openSource('B');c.closeSource();c.openSource('B');c.showPreview();c.showPreview();const t=last(views).telemetry;assert.equal(t.events.length,6);assert.equal(t.counts.sourceOpens,2);assert.equal(t.counts.sourceReopens,1);assert.equal(t.counts.recheckRequests,2);assert.equal(t.counts.previewPassportExposures,4);assert.equal(last(views).sourceOpenCounts.B,2);
});
test('disclosures survive benign rendering and scrub with all telemetry on access loss',async()=>{
 const {c,views,access}=await setup();assert.equal(typeof c.setDisclosure,'function');c.openSource('B');c.setDisclosure('raw-B',true);c.showPreview();assert.equal(last(views).disclosures['raw-B'],true);c.setMode('CANDIDATE');assert.equal(last(views).disclosures['raw-B'],true);access.sourceAccess.B='UNKNOWN';assert.throws(()=>c.openSource('B'));const v=last(views);assert.equal('raw-B' in v.disclosures,false);assert.equal('B' in v.sourceObservations,false);assert.equal(JSON.stringify(v.telemetry).includes('"B"'),false);assert.equal(JSON.stringify(v.telemetry).includes('fictional'),false);assert.equal(v.openSourceId,null);assert.equal(v.telemetry.comparisonEligible,false);
});
test('source focus records actual originating trigger equally for directory and contextual links',async()=>{
 const {c,views}=await setup('CANDIDATE');c.withholdSource('B');c.openSource('B','next-R1-B');assert.equal(last(views).focusTarget,'source-panel');c.closeSource();assert.equal(last(views).focusTarget,'next-R1-B');c.openSource('B','open-B');c.closeSource();assert.equal(last(views).focusTarget,'open-B');assert.throws(()=>c.openSource('B','unknown-trigger'));
});
test('bounded telemetry signals saturation and reset restores clean initial state',async()=>{
 const {c,views}=await setup();assert.equal(typeof c.startTrial,'function');c.startTrial();for(let i=0;i<105;i++)c.showPreview();assert.equal(last(views).telemetry.events.length,100);assert.equal(last(views).telemetry.saturated,true);assert.equal(last(views).telemetry.comparisonEligible,false);c.reset();assert.equal(last(views).telemetry.events.length,0);assert.equal(last(views).telemetry.saturated,false);assert.equal(last(views).preview,null);
});
test('common compact markup keeps critical evidence outside native raw disclosures',async()=>{
 const js=await readFile(new URL('../app.mjs',import.meta.url),'utf8');for(const word of ['Re-evaluate fixed-fixture checks and prepare preview','previously computed byte verification','sourceObservations','Observed current revision in this fixture','effectiveAccess',"node('details'", "node('summary'",'next-${r.id}-${id}'])assert.ok(js.includes(word),word);
 assert.equal(/live refresh|fresh digest|cryptographic recheck/.test(js),false);
});

test('renderer exposes the real injectable mount seam without a global QA state',async()=>{const app=await import('../app.mjs');assert.equal(typeof app.mountProbe,'function');const js=await readFile(new URL('../app.mjs',import.meta.url),'utf8');assert.equal(/window\.(model|controller|testModel)/.test(js),false);});
test('every invalid or no-op disclosure flushes access scrubbing before returning',async()=>{
 for(const which of ['raw-close','metrics-close','invalid']){const {c,views,access}=await setup();c.openSource('B');c.setDisclosure('raw-B',true);c.setDisclosure('instrumentation',true);c.showPreview();access.sourceAccess.B='DENIED';if(which==='raw-close')assert.throws(()=>c.setDisclosure('raw-B',false));else if(which==='invalid')assert.throws(()=>c.setDisclosure('unknown',true));else c.setDisclosure('instrumentation',false);assert.equal(last(views).openSourceId,null,which);assert.equal(JSON.stringify(last(views)).includes('PRIVATE_CANARY_B'),false,which);assert.equal(last(views).preview,null,which);}
});
test('invalid controller requests cannot return a stale permitted projection after access loss',async()=>{
 for(const action of [c=>c.openSource('Z'),c=>c.openSource('A','unknown-origin'),c=>c.setMode('UNKNOWN'),c=>c.withholdSource('Z'),c=>c.restoreSource('Z')]){const {c,views,access}=await setup();c.openSource('B');access.sourceAccess.B='UNKNOWN';assert.throws(()=>action(c));assert.equal(JSON.stringify(last(views)).includes('PRIVATE_CANARY_B'),false);assert.equal(last(views).openSourceId,null);}
});
test('closing an already-open source returns to its most recent actual trigger',async()=>{const {c,views}=await setup('CANDIDATE');c.withholdSource('B');c.openSource('B','next-R1-B');c.openSource('B','open-B');c.closeSource();assert.equal(last(views).focusTarget,'open-B');assert.equal(last(views).sourceOpenCounts.B,1);});
test('closed-panel focus references are scrubbed when their source loses access',async()=>{const {c,views,access}=await setup('CANDIDATE');c.withholdSource('B');c.openSource('B','next-R1-B');c.closeSource();access.sourceAccess.B='DENIED';c.setDisclosure('instrumentation',false);assert.equal(last(views).focusTarget,'content');assert.equal(JSON.stringify(last(views)).includes('next-R1-B'),false);});
test('no-op disclosure publishes invalidation of nonvisibility fixture checks',async()=>{const {c,views,access}=await setup();c.showPreview();access.workEvent.hold='ACTIVE';c.setDisclosure('raw-A',false);assert.equal(last(views).preview,null);assert.equal(last(views).checkState,'INVALIDATED');assert.equal(last(views).packet.workEvent.hold,'ACTIVE');});
