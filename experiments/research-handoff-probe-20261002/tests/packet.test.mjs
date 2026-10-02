import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {validateFixture,resolveKnownKey,verifyRepresentation,classifyByteRelation,projectPacket,previewHandoff,makeReplayKey} from '../packet.mjs';
const raw=JSON.parse(await readFile(new URL('../fixtures/packet.json',import.meta.url),'utf8'));
const copy=x=>structuredClone(x);
const scenario={withheldSourceIds:[]};
const req={sourceId:'A',destinationSourceId:'B',purpose:'explanatory_update',workEventId:'W1'};
const hashes=async f=>Object.fromEntries(await Promise.all(f.sources.map(async s=>[s.id,await verifyRepresentation(s.representation)])));
const setup=async()=>{const f=validateFixture(raw);assert.ok(f,'validated frozen fixture required');return [f,copy(f.access),await hashes(f)];};
const revisedRep=(rep,body)=>({...copy(rep),body,byteCount:Buffer.byteLength(body),claimedDigest:createHash('sha256').update(body).digest('hex')});

test('test_withhold_b_changes_only_r1_membership',async()=>{
 const [f,a,v]=await setup(),before=JSON.stringify(f),accessBefore=JSON.stringify(a);
 const initial=projectPacket(f,scenario,a,v),out=projectPacket(f,{withheldSourceIds:['B']},a,v);
 assert.deepEqual(out.routes.map(r=>r.missingSourceIds),[['B'],[],[]]);
 assert.deepEqual(out.routes.map(r=>r.applicationState),['NOT_EVALUATED','NOT_EVALUATED','NOT_EVALUATED']);
 assert.deepEqual(out.targets,initial.targets);assert.deepEqual(out.workEvent,initial.workEvent);
 assert.equal(out.recordedRoutesComplete,false);assert.match(out.coverageNotice,/incomplete/i);
 assert.equal(JSON.stringify(f),before);assert.equal(JSON.stringify(a),accessBefore);
 assert.deepEqual(projectPacket(f,scenario,a,v),initial);assert.ok(Object.isFrozen(f.sources[0].representation));
});
test('test_topology_and_unknown_key_refusals',()=>{
 const edits=[f=>f.routes[0].operator='ANY',f=>f.routes[0].sourceIds.pop(),f=>f.routes.push({...f.routes[0],id:'R4'}),f=>f.sources[1].resourceId=f.sources[0].resourceId,f=>f.targets.push({...f.targets[0],id:'V'}),f=>f.routes[0].accepted=true,f=>f.sources[0].url='javascript:alert(1)',f=>f.authority='invented'];
 for(const edit of edits){const f=copy(raw);edit(f);assert.throws(()=>validateFixture(f));}
 const f=validateFixture(raw);assert.ok(f);assert.deepEqual(resolveKnownKey(f,'A'),{state:'LINKED',sourceId:'A'});assert.deepEqual(resolveKnownKey(f,'invented'),{state:'UNLINKED'});
 assert.throws(()=>projectPacket(f,{withheldSourceIds:['Z']},f.access,{}));assert.throws(()=>projectPacket(f,{withheldSourceIds:['B','B']},f.access,{}));
});
test('computed verification refuses forged digest and wrong byte count',async()=>{
 const rep=raw.sources[0].representation;assert.equal((await verifyRepresentation(rep))?.state,'VERIFIED');
 for(const [patch,reason] of [[{claimedDigest:'0'.repeat(64)},'DIGEST_MISMATCH'],[{byteCount:1},'BYTE_COUNT_MISMATCH'],[{digestAlgorithm:'dropbox-content-hash'},'UNSUPPORTED_ALGORITHM']]){
  const result=await verifyRepresentation({...rep,...patch});assert.equal(result.state,'UNVERIFIED');assert.equal(result.failureReason,reason);
 }
});
test('eight identity traps preserve resources review and ownership',async()=>{
 const original=copy(raw.sources[0]);
 const cases=[['same title different bytes',s=>s.representation=revisedRep(s.representation,'FICTIONAL different bytes'),'DIFFERENT_BYTES'],['rename same resource',s=>s.title='Fictional renamed source','EXACT_BYTE_REPLICA'],['copy new resource',s=>{s.resourceId='fictional:copy:new';s.reviewRef='review-copy';s.ownerRef='other-fictional-owner';},'EXACT_BYTE_REPLICA'],['original vs extraction',s=>s.representation.kind='text-extraction','DIFFERENT_REPRESENTATION'],['same digest different algorithm',s=>s.representation.digestAlgorithm='dropbox-content-hash','NOT_COMPARABLE'],['metadata edit',s=>s.sourceDate='2026-10-02T11:00:00Z','EXACT_BYTE_REPLICA'],['changed revision same bytes',s=>s.revisionToken='fictional-revision-2','EXACT_BYTE_REPLICA'],['archive vs member',s=>s.representation.kind='archive-member','DIFFERENT_REPRESENTATION']];
 for(const [name,edit,expected] of cases){const other=copy(original);edit(other);const before=JSON.stringify([original,other]);const left={source:original,representation:original.representation,verification:await verifyRepresentation(original.representation)},right={source:other,representation:other.representation,verification:await verifyRepresentation(other.representation)};assert.equal(classifyByteRelation(left,right),expected,name);assert.equal(JSON.stringify([original,other]),before,name);}
 const forged={representation:original.representation,verification:{state:'VERIFIED',computedDigest:original.representation.claimedDigest,algorithm:'sha256',encoding:'hex',byteCount:original.representation.byteCount,verificationMethod:'WEB_CRYPTO_SHA256_UTF8'}};
 assert.equal(classifyByteRelation(forged,forged),'NOT_COMPARABLE');
});
test('test_preview_is_proposed_only',async()=>{
 const [f,a,v]=await setup();const p=previewHandoff(f,scenario,a,req,v);
 assert.equal(p.status,'PROPOSED');assert.equal(p.eligibility,'PREVIEW_ONLY');assert.equal(p.scientificEffect,'NONE');assert.equal('resultProviderId' in p,false);
 assert.equal(p.input.resourceId,f.sources[0].resourceId);assert.equal(p.input.observationId,f.sources[0].observationId);assert.equal(p.input.revisionToken,f.sources[0].revisionToken);assert.equal(p.input.representation.id,f.sources[0].representation.id);
 assert.equal(p.destination.resourceId,f.sources[1].resourceId);assert.equal(p.purpose,'explanatory_update');assert.equal(p.workEvent.id,'W1');assert.deepEqual(p.workEvent.ownerIds,['researcher-alpha']);assert.equal(p.workEvent.hold,'CLEAR');assert.equal(p.audience,'OWNER');
 assert.ok(previewHandoff(f,{withheldSourceIds:['B']},a,req,v).blockReasons.includes('DESTINATION_CONTEXT_EXCLUDED_FROM_PACKET'));
 assert.deepEqual(previewHandoff(f,scenario,a,req,v),p);
 for(const patch of [{sourceId:'D'},{workEventId:'W2'},{purpose:'accept_theorem'},{destinationSourceId:'C'},{resultProviderId:'invented'}])assert.throws(()=>previewHandoff(f,scenario,a,{...req,...patch},v));
});
test('test_preview_blocks_each_independent_gate',async()=>{
 const [f,a,v]=await setup();
 const cases=[['SOURCE_REVISION_STALE',a=>a.revisionFreshnessBySourceId.A='STALE'],['DESTINATION_REVISION_STALE',a=>a.currentRevisionTokenBySourceId.B='fictional-new'],['OWNER_UNKNOWN',a=>a.workEvent.ownerFreshness='UNKNOWN'],['OWNER_STALE',a=>a.workEvent.ownerFreshness='STALE'],['HOLD_ACTIVE',a=>a.workEvent.hold='ACTIVE'],['HOLD_UNKNOWN',a=>a.workEvent.hold='UNKNOWN'],['OWNER_CONFLICT',a=>a.workEvent.ownerIds.push('researcher-beta')],['SOURCE_ACCESS_DENIED',a=>a.sourceAccess.A='DENIED'],['DESTINATION_ACCESS_UNKNOWN',a=>a.sourceAccess.B='UNKNOWN'],['OWNER_UNKNOWN',a=>a.workEvent.ownerIds=[]]];
 for(const [reason,edit] of cases){const access=copy(a);edit(access);for(const sc of [scenario,{withheldSourceIds:['B']}]){const p=previewHandoff(f,sc,access,req,v);assert.ok(p.blockReasons.includes(reason),reason);assert.equal(p.status,'PROPOSED');assert.equal(p.eligibility,'BLOCKED');assert.equal('resultProviderId' in p,false);}}
 const vv={...v,B:await verifyRepresentation({...f.sources[1].representation,claimedDigest:'0'.repeat(64)})};assert.ok(previewHandoff(f,scenario,a,req,vv).blockReasons.includes('DESTINATION_BYTES_UNVERIFIED'));
});
test('test_access_projection_precedes_payload_and_counts',async()=>{
 const [f,a,v]=await setup();assert.equal(projectPacket(f,scenario,a,v).sources.length,5);
 const publicAccess={...a,audience:'PUBLIC'};const publicView=projectPacket(f,scenario,publicAccess,v),text=JSON.stringify(publicView);
 for(const hidden of ['PRIVATE_CANARY_B','PRIVATE_CANARY_C',f.sources[1].resourceId,f.sources[2].resourceId,'R1'])assert.equal(text.includes(hidden),false,hidden);
 assert.deepEqual(publicView.sources.map(s=>s.id),['A','D','E']);assert.deepEqual(publicView.routes.map(r=>r.id),['R2','R3']);assert.equal(publicView.sourceCount,3);assert.equal(publicView.routeCount,2);
 for(const value of ['DENIED','UNKNOWN']){const access=copy(a);access.sourceAccess.B=value;const dto=JSON.stringify(projectPacket(f,scenario,access,v));assert.equal(dto.includes('PRIVATE_CANARY_B'),false);assert.equal(dto.includes('R1'),false);assert.equal(JSON.stringify(previewHandoff(f,scenario,access,req,v)).includes(f.sources[1].resourceId),false);}
 for(const reason of ['PARTIAL_LISTING','HTTP_404']){const changed=copy(a);changed.sourceObservationState.A={availability:'UNKNOWN',reason};const view=projectPacket(f,scenario,changed,v);assert.equal(view.sources[0].availability,'UNKNOWN');assert.equal(JSON.stringify(view).includes('TOMBSTONE'),false);}
 const wrongOwner=copy(a);wrongOwner.principalId='researcher-beta';assert.equal(JSON.stringify(projectPacket(f,scenario,wrongOwner,v)).includes('PRIVATE_CANARY_B'),false);
});
test('test_replay_includes_policy_and_access',async()=>{
 const [f,a,v]=await setup();const key=makeReplayKey(f.fixtureVersion,{withheldSourceIds:['B','C']},a,v);assert.equal(typeof key,'string');assert.equal(key,makeReplayKey(f.fixtureVersion,{withheldSourceIds:['C','B']},a,v));
 for(const edit of [x=>x.audience='PUBLIC',x=>x.policyVersion='unknown-policy',x=>x.sourceAccess.B='DENIED',x=>x.workEvent.hold='ACTIVE',x=>x.principalId='someone-else']){const aa=copy(a);edit(aa);assert.notEqual(key,makeReplayKey(f.fixtureVersion,{withheldSourceIds:['C','B']},aa,v));}
 assert.throws(()=>makeReplayKey(f.fixtureVersion,{withheldSourceIds:['Z']},a,v));assert.throws(()=>makeReplayKey(f.fixtureVersion,{withheldSourceIds:['B','B']},a,v));assert.deepEqual(projectPacket(f,scenario,a,v),projectPacket(f,scenario,a,v));
});
test('verification snapshots input before asynchronous digest and refuses later body mutation',async()=>{
 const rep=structuredClone(raw.sources[0].representation),pending=verifyRepresentation(rep);rep.body=rep.body.replace('GitHub','GotHub');const v=await pending,original=raw.sources[0].representation;
 assert.equal(classifyByteRelation({representation:rep,verification:v},{representation:original,verification:await verifyRepresentation(original)}),'NOT_COMPARABLE');
});
test('replay key distinguishes computed provenance from a JSON lookalike',async()=>{
 const [f,a,v]=await setup(),forged=structuredClone(v);assert.notEqual(makeReplayKey(f.fixtureVersion,scenario,a,v),makeReplayKey(f.fixtureVersion,scenario,a,forged));
});
test('access denial hides destination freshness and private Work Event decisions',async()=>{
 const [f,a,v]=await setup();a.audience='PUBLIC';a.sourceAccess.B='DENIED';const baseline=previewHandoff(f,scenario,a,req,v);a.revisionFreshnessBySourceId.B='STALE';a.workEvent.hold='ACTIVE';a.workEvent.ownerIds.push('researcher-beta');assert.deepEqual(previewHandoff(f,scenario,a,req,v),baseline);
});

test('current availability changes replay and blocks preview without asserting deletion',async()=>{const [f,a,v]=await setup();const initial=makeReplayKey(f.fixtureVersion,scenario,a,v);a.sourceObservationState.B={availability:'UNKNOWN',reason:'HTTP_404'};assert.notEqual(makeReplayKey(f.fixtureVersion,scenario,a,v),initial);assert.ok(previewHandoff(f,scenario,a,req,v).blockReasons.includes('DESTINATION_AVAILABILITY_UNKNOWN'));assert.equal(projectPacket(f,scenario,a,v).sources[1].availability,'UNKNOWN');});
