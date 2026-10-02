import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {validateFixture,verifyRepresentation} from '../packet.mjs';
import {createController} from '../app.mjs';
const raw=JSON.parse(await readFile(new URL('../fixtures/packet.json',import.meta.url),'utf8'));
async function setup(){const fixture=validateFixture(raw),access=structuredClone(fixture.access),verifications=Object.fromEntries(await Promise.all(fixture.sources.map(async s=>[s.id,await verifyRepresentation(s.representation)])));const views=[];const c=createController({fixture,access,verifications},v=>views.push(v));assert.ok(c,'controller required');return {c,views,fixture,access};}
const last=views=>views.at(-1);
test('controller preserves fixture states and renders once per actual membership transition',async()=>{
 const {c,views,fixture,access}=await setup(),before=JSON.stringify([fixture,access]);assert.equal(views.length,1);assert.equal(last(views).mode,'BASELINE');
 c.withholdSource('B');assert.equal(views.length,2);assert.deepEqual(last(views).packet.routes[0].missingSourceIds,['B']);c.withholdSource('B');assert.equal(views.length,3);
 c.restoreSource('B');assert.equal(views.length,4);c.restoreSource('B');assert.equal(views.length,5);assert.deepEqual(last(views).packet.routes.map(r=>r.applicationState),['NOT_EVALUATED','NOT_EVALUATED','NOT_EVALUATED']);assert.equal(JSON.stringify([fixture,access]),before);assert.throws(()=>c.withholdSource('Z'));
});
test('mode switches expose same underlying facts and body text',async()=>{
 const {c,views}=await setup(),baseline=last(views).packet;c.setMode('CANDIDATE');assert.deepEqual(last(views).packet,baseline);assert.equal(views.length,2);c.setMode('CANDIDATE');assert.equal(views.length,2);assert.throws(()=>c.setMode('UNKNOWN'));c.setMode('BASELINE');assert.deepEqual(last(views).packet,baseline);
});
test('source opens count once per closed-to-open transition and denied access refuses bodies',async()=>{
 const {c,views,access}=await setup();c.openSource('B');assert.equal(last(views).sourceOpenCounts.B,1);assert.equal(last(views).openSourceId,'B');const n=views.length;c.openSource('B');assert.equal(views.length,n+1);c.closeSource();c.openSource('B');assert.equal(last(views).sourceOpenCounts.B,2);c.closeSource();access.sourceAccess.B='DENIED';assert.throws(()=>c.openSource('B'));c.setMode('CANDIDATE');assert.equal(JSON.stringify(last(views)).includes('PRIVATE_CANARY_B'),false);assert.throws(()=>c.openSource('Z'));
});
test('preview invalidates on changes and reset returns exact initial state with counters cleared',async()=>{
 const {c,views}=await setup(),initial=structuredClone(last(views));c.setMode('CANDIDATE');c.openSource('A');c.showPreview();assert.equal(last(views).preview.eligibility,'PREVIEW_ONLY');const n=views.length;c.showPreview();assert.equal(views.length,n+1);c.withholdSource('B');assert.equal(last(views).preview,null);c.showPreview();assert.equal(last(views).preview.eligibility,'BLOCKED');c.restoreSource('B');assert.equal(last(views).preview,null);c.reset();assert.deepEqual(last(views),initial);const count=views.length;c.reset();assert.equal(views.length,count);
});
test('page contract includes permanent scope notice semantic controls and CSP',async()=>{
 const html=await readFile(new URL('../index.html',import.meta.url),'utf8'),js=await readFile(new URL('../app.mjs',import.meta.url),'utf8');
 for(const required of ['Fictional','hypothetical','incomplete','NOT_EVALUATED','Content-Security-Policy','<button','id="baseline"','id="candidate"','aria-pressed','id="scope-notice"'])assert.ok(html.includes(required),required);
 for(const required of ['textContent','sourceDate','observedAt','scope','PROPOSED','PREVIEW_ONLY','closeSource','sourceOpenCounts'])assert.ok(js.includes(required),required);
 assert.equal(/\.innerHTML|\.outerHTML|insertAdjacentHTML|document\.write/.test(js),false);
 assert.match(html,/object-src 'none'/);assert.match(html,/form-action 'none'/);
});
test('application has only fixed same-origin fixture fetch and no storage URL state external calls',async()=>{
 const js=await readFile(new URL('../app.mjs',import.meta.url),'utf8'),model=await readFile(new URL('../packet.mjs',import.meta.url),'utf8');
 assert.deepEqual([...js.matchAll(/fetch\(([^)]*)\)/g)].map(m=>m[1]),["'./fixtures/packet.json'"]);
 for(const forbidden of [/localStorage/,/sessionStorage/,/indexedDB/,/serviceWorker/,/XMLHttpRequest/,/WebSocket/,/sendBeacon/,/history\.(pushState|replaceState)/,/location\.(search|hash)/,/https?:\/\//,/new Date\(/,/Date\.now\(/])assert.equal(forbidden.test(js+model),false,String(forbidden));
});
test('responsive contract wraps identities and honors reduced motion without claiming browser proof',async()=>{
 const css=await readFile(new URL('../style.css',import.meta.url),'utf8');assert.match(css,/overflow-wrap:\s*anywhere/);assert.match(css,/prefers-reduced-motion/);assert.match(css,/:focus-visible/);assert.match(css,/min-width:\s*0/);assert.match(css,/@media/);
});
test('denied or unknown warm-open source is scrubbed before controller refusal returns',async()=>{
 for(const decision of ['DENIED','UNKNOWN']){const {c,views,access}=await setup();c.openSource('B');c.showPreview();assert.equal(JSON.stringify(last(views)).includes('PRIVATE_CANARY_B'),true);access.sourceAccess.B=decision;assert.throws(()=>c.openSource('B'));assert.equal(last(views).openSourceId,null);assert.equal(JSON.stringify(last(views)).includes('PRIVATE_CANARY_B'),false);assert.equal(last(views).preview,null);assert.equal('B' in last(views).sourceOpenCounts,false);}
});
test('status explicitly separates access-unavailable B from packet exclusion',async()=>{
 const js=await readFile(new URL('../app.mjs',import.meta.url),'utf8');assert.ok(js.includes('B is not visible under current fixture access; membership not disclosed'));assert.ok(js.includes('B excluded from hypothetical packet'));
});
test('switching modes preserves the common exact proposal meaning',async()=>{
 const {c,views}=await setup();c.setMode('CANDIDATE');c.showPreview();assert.equal(last(views).preview.eligibility,'PREVIEW_ONLY');const expected=last(views).preview;c.setMode('BASELINE');assert.deepEqual(last(views).preview,expected);
});
test('page lifecycle reset is wired for BFCache restoration with no browser-proof claim',async()=>{
 const js=await readFile(new URL('../app.mjs',import.meta.url),'utf8');assert.match(js,/addEventListener\('pagehide',\s*\(\)\s*=>\s*controller.reset\(\)/);assert.match(js,/addEventListener\('pageshow',\s*event\s*=>\s*\{\s*if\s*\(event.persisted\)\s*controller.reset\(\)/);
});
