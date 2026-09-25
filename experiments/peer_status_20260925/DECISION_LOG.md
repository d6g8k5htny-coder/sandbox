# Decision log (eng; scientific effect NONE)

## 2026-09-25T18:04Z — after #98 allowlist absorb

**Facts:**
- #98 head `d765efa` includes `fix: allowlist scientific_state and claims_gate_adapter CI commands`
  → `pr98_ci_allowlist_fix.patch` absorbed; do not re-apply.
- #101 verify SUCCESS; tip still missing RESEARCH_INDEX/handoff APPLIED prose.
- #105 consumers absorbed @`54a8c59`; verify still in progress.
- Nav/handoff package still applies cleanly on tip `eeebb28`; composes with #101+#108.

**Peer model consultation:** launched (GPT + Claude Task votes) for next-step
confirmation; provisional local consensus matches expected votes.

**Decision (provisional → confirm after peer votes):**
1. Mark #98 package ABSORBED in COORDINATION.
2. Top main-write ask remains `pr97_followup_nav_and_handoff.patch`.
3. No new eng package unless #105/#98/#108 CI reveals a fresh machine fail.
4. Observe Math- #9/#14 (D5); do not duplicate.

**Sandbox next:** update absorb docs, refresh STATUS, push, keep PR/CI
subscriptions; wait for peer-model vote delivery then adjust if they disagree.

## 2026-09-25T18:05Z — peer vote received: claude-sonnet-5-thinking-medium

Confirmed absorb docs already match the new fact (COORDINATION.json,
NEXT_ACTIONS.md, PR98_CI_ALLOWLIST_APPLY.md all already show #98 @`d765efa`
absorbed from the prior commit); this vote ratifies that state rather than
introducing a change.

**Votes:**
- **A — Mark #98 absorbed, stop re-pushing that patch: YES.** Head
  `d765efa` contains the allowlist fix verbatim; re-pushing
  `pr98_ci_allowlist_fix.patch` would conflict/no-op. Keep it as historical
  recipe only, per `PR98_CI_ALLOWLIST_APPLY.md`.
- **B — Keep amplifying nav/handoff package as top main-write ask: YES.**
  `pr97_followup_nav_and_handoff.patch` still applies cleanly on tip
  `eeebb28`, composes with green `#101` and open `#108`, and is the only
  `ready_for_main_write` item with no absorb/parked blocker.
- **C — Attempt any other sandbox eng package now: NO.** `#105` verify is
  still pending (don't preempt), `#104`/`#106` are parked, Math- `#9`/`#14`
  are explicitly observe-only, and no fresh CI failure has surfaced on
  `#98`/`#105`/`#108` to justify a new package. Manufacturing a new package
  now would duplicate `COORDINATION_PROTOCOL.md` rule 6.

**Pending:** `gpt-5.6-terra-medium` vote still outstanding in
`COORDINATION.json.multi_model.pending_votes`.

**Sandbox next action:** no new patch — keep watching `#101`/`#105`/`#108`
CI and hold `pr97_followup_nav_and_handoff.patch` ready to amplify the
moment a main-write peer needs it; do not re-push `pr98_ci_allowlist_fix.patch`.

## 2026-09-25T18:06Z — tip advanced; #101/#102/#107 merged

**Facts:** Hardening tip now `848aea2` (#101 carrier-absent, #107 frozen errata,
#102 SIDE24 importers). Nav/handoff package **still applies** (RESEARCH_INDEX +
handoff APPLIED still absent). Composes with remaining open #108.

**Decision:** Keep `pr97_followup_nav_and_handoff.patch` as sole top main-write
ask against tip `848aea2`. No new package. Await peer-model vote delivery to
confirm; provisional consensus unchanged.

## 2026-09-25T18:08:33Z — live peer override on main #98

**Events:** Owner asked four #90 loss-only adapter cases on #98. Peer cursor
agent claimed ownership and pushed `fc6caf5` (`fix(#90): loss-only reverse-impact
cases on thin claims adapter`) with edge-only seeds, canonical snapshots,
self-hold, strict boolean required, duplicate-edge reject. Peer coordination
comment: defer inventable #105–#108 churn until #90 adapter CI green.

**Decision:**
1. **Yield** — sandbox does not race #98 adapter work; observe CI only.
2. **Defer** amplifying `pr97_followup_nav_and_handoff.patch` landing ask until
   #98 #90 criterion is green (package stays ready on tip `848aea2`).
3. Do not open a competing adapter patch from sandbox.

**Sandbox next:** refresh STATUS, watch #98/#105 CI, no new package unless
peer asks for a portable recipe or CI reveals a gap they are not covering.

## 2026-09-25T18:09:24Z — peer vote received: gpt-5.6-terra-medium (stale vs live)

[Alt model D7 priority](bc-39eac87c-ddc6-527e-ab18-a77e391df7b6) returned:
NEXT_SANDBOX revalidate `pr98_ci_allowlist_fix.patch` vs #98 `d765efa`;
ASK_MAIN_PEER apply allowlist; DO_NOT STATUS churn; RISK older-head apply.

**Disposition:** vote **recorded and superseded**. Allowlist already absorbed on
`d765efa` and #98 advanced to `fc6caf5` (#90 adapter, peer-owned). Do not
re-ask main peers to apply `pr98_ci_allowlist_fix.patch`. Claude vote
([Claude D7 next-step vote](bc-4853db45-e132-5daf-8467-544fceb86361)) remains
the standing A/B/C ratification, further overridden by live #98 ownership
(yield adapter; defer nav/handoff amplify).

**Pending votes:** none.

## 2026-09-25T18:12:19Z — package #98 hold_proposals unsatisfied fix for peer

**Facts:** Independent review of `fc6caf5` found aggregate `hold_proposals`
fail-open (drops `unsatisfied_required`). Peer still owns #98; sandbox does
not push main.

**Decision:** Ship portable `pr98_hold_proposals_unsatisfied_fix.patch` +
APPLY note (local 20/20 tests green). Do not race their branch beyond the
package. Nav/handoff remains deferred.

## 2026-09-25T18:13:38Z — #98 advanced to 4c8f4bf (#95 digests); hold fix still needed

Peer landed `feat(#95): v1.1 semantic_digest / evidence_digest`. Aggregate
`hold_proposals` fail-open **still present**. Sandbox
`pr98_hold_proposals_unsatisfied_fix.patch` still applies; 20/20 tests green
on `4c8f4bf`+patch. No competing work; keep package as top ask for #98 peer.
