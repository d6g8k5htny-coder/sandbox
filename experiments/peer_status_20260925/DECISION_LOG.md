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

## 2026-09-25T18:15:17Z — #98 absorbed hold_proposals unsatisfied fix @`c1821b6`

Peer landed `fix(#90): surface unsatisfied_required in aggregate HOLD reports`.
Sandbox package marked ABSORBED (do not re-apply). Continue observe #98 CI;
nav/handoff remains ready but deferred until that CI greens.

## 2026-09-25T18:21:31Z — #105 consumers fix reopened @`36fe375`

Branch rewrite dropped `registers/CONSUMERS.json` update. `consumers_check`
fails again (same prose drift). Re-list `pr105_consumers_fix.patch` as top
ready ask; patch still applies. Do not treat prior absorb as current.

## 2026-09-25T18:23:20Z — d7-multimodel-loop timer

**Refresh:** tip still `848aea2`; nav/handoff package still applies; #108
observe @`92b10b0` did not land RESEARCH_INDEX/handoff APPLIED.
**#105** @`36fe375` verify FAILURE — CONSUMERS still missing (top ask unchanged).
**#98** @`0449280` verify IN_PROGRESS — hold aggregate absorbed; observe only.
**Priority ambiguous?** No — skip extra model consult.
**Decision:** no new package; keep amplifying `pr105_consumers_fix.patch` for
#105 peer; hold nav deferred; resubscribe timer.

## 2026-09-25T18:39:46Z — d7-multimodel-loop timer

**Facts:** Tip advanced to `f244312` (#108 merged). #98 verify **SUCCESS**
@`0449280`. #105 still FAILURE @`36fe375` without CONSUMERS.json. Nav/handoff
package still applies on tip.

**Decision:** Keep #105 consumers re-apply as **P1**. **Und-defer** nav/handoff
to **P2** (blocker #98 CI cleared). No new package. No extra model consult
(priority unambiguous).

## 2026-09-25T18:49:33Z — #105 consumers resolved by cite rewrite @`2440881`

Peer dropped `lpw_fold_dispositions` citation in favor of lpw README crosswalk.
Local `consumers_check` problems=0. Mark `pr105_consumers_fix.patch` obsolete
for current head. **Promote nav/handoff to sole P1.**

## 2026-09-25T18:55:42Z — d7-multimodel-loop timer

**Facts:** Tip `fcad72366743` (#109 merged SIDE24_CELL→crosswalk pointer). Nav
package **still applies** (RESEARCH_INDEX / handoff APPLIED / math_status README
nav block absent). #105 @`91a5e9a` CI in progress. #98 still green draft.

**Decision:** Keep nav/handoff as sole P1. No new package. No model consult
(unambiguous).

## 2026-09-25T19:11:30Z — d7-multimodel-loop timer

No material change since prior loop. Tip `fcad723`; nav package still applies;
#105 @`91a5e9a` verify still in progress; #98 green draft. Keep sole P1 =
nav/handoff. No new package.

## 2026-09-25T19:19:14Z — #98 event-boundary: peer land supersedes sandbox package

**Facts:**
- OpenAI AMEND_REQUIRED on #98@`0449280` (malformed dep/`as_of` swallowed;
  CLI ignored before/after; CI tip identity ≠ base→head).
- Sandbox began parallel portable amend in `/tmp/main-pr98-amend` (strict
  containers, argparse, GITHUB_EVENT_PATH compare, entry-point tests) —
  local EventBoundaryAmendTests 10/10 green.
- **Live peer override:** Cursor #98 owner pushed
  `4b983b9 fix(#90): deploy before/after CLI + strict as_of/dep containers`
  (subcommand CLI + CI tip-health/event-compare) before sandbox handoff.
- Tip advanced to `e3cd7d4873c5` (#105 merged). Nav/handoff package **still
  applies**.

**Multi-model:** launched fresh A/B/C votes
([Claude vote](bc-6c4e999d-2dc3-597a-9a28-9f495afa910b),
[GPT vote](bc-a8093c89-9984-555a-bdfa-c8e633c9497e)); live peer land already
decisive per COORDINATION_PROTOCOL (defer to forge ownership).

**Decision:**
1. Mark `pr98_event_boundary_amend` **ABSORBED / do not re-apply**.
2. Yield #98 — observe CI @`4b983b9` only; no race.
3. Keep `pr97_followup_nav_and_handoff.patch` as **sole tip P1** on `e3cd7d4`.
4. No other new eng package.

**Sandbox next:** commit absorb docs + historical patch; watch #98 CI; timer loop.

## 2026-09-25T19:21:22Z — peer votes received (A/B/C) — superseded by live #98 land

**Votes** ([Claude vote](bc-6c4e999d-2dc3-597a-9a28-9f495afa910b),
[GPT vote](bc-a8093c89-9984-555a-bdfa-c8e633c9497e)):
- **A — Finish packaging `pr98_event_boundary_amend` first: YES** (both).
- **B — Keep nav/handoff ready P1, do not amplify yet: YES** (both).
- **C — Any other new eng package: NO** (both).

**Disposition:** votes **recorded and superseded**. Peer already landed the
event-boundary amend @`4b983b9` and advanced to PR15-contract follow-up
@`0bc41ca` before sandbox handoff. Do **not** finish/re-push the parallel
sandbox package (ABSORBED / do not re-apply). Standing action remains:
observe #98 CI only; sole tip P1 = `pr97_followup_nav_and_handoff.patch` on
`e3cd7d4`.

**Pending votes:** none.

## 2026-09-25T19:36:03Z — d7-multimodel-loop timer

**Refresh:** tip still `e3cd7d4873c5`; nav/handoff package still applies.
**#98** @`0bc41ca` verify IN_PROGRESS (navigation + loss-only SUCCESS); peer-owned
PR15-contract follow-up — yield.
**Votes:** already recorded+superseded (no pending).
**Priority ambiguous?** No — skip model consult.
**Decision:** no new package; keep sole P1 = nav/handoff; observe #98 CI; resubscribe timer.

## 2026-09-25T19:51:01Z — #98 CI FAILURE: artifacts/ top-level allowlist

**Facts:** run `36179103673` COMPLETE/FAILURE. Claims→gate tip-health +
event-compare PASS; sole fail
`test_repository_top_level_list_matches_the_checkout` — CI created
`artifacts/` via `--write-report artifacts/claims-gate-impact.json`.
OpenAI: repair cause, keep negative control, #90 stays OPEN. Peer owns #98.

**Decision:** Ship portable `pr98_artifacts_toplevel_ignore.patch` (ignore +
gitignore `artifacts/`; do not add to REPOSITORY_TOP_LEVEL). Promote to P1
ask for #98 peer. Demote nav/handoff to P2 until #98 CI green. No race on
their branch. No model consult (unambiguous CI machine fail).

## 2026-09-25T19:52:36Z — d7-multimodel-loop: #98 artifacts fix absorbed

**Facts:** Peer landed `776fdb7` — event-compare report writes to `/tmp/…`,
`artifacts` removed from `REPOSITORY_TOP_LEVEL`, `.gitignore` has `artifacts/`.
Sandbox `pr98_artifacts_toplevel_ignore.patch` superseded (do not re-apply).
Tip still `e3cd7d4`; nav package still applies. #98 verify QUEUED.

**Decision:** Mark artifacts package ABSORBED. Restore nav/handoff as sole P1.
Yield #98; watch CI. No new package. No model consult.

## 2026-09-25T20:08:57Z — d7-multimodel-loop timer

**Refresh:** tip still `e3cd7d4873c5`; nav/handoff package still applies.
**#98** @`776fdb7` verify **SUCCESS** (navigation + loss-only SUCCESS); still DRAFT;
OpenAI #90 re-review pending. Artifacts package remain ABSORBED.
**Priority ambiguous?** No — skip model consult.
**Decision:** no new package; keep sole P1 = nav/handoff; observe #98 re-review;
resubscribe timer.

## 2026-09-25T20:24:44Z — d7-multimodel-loop timer

No material change. Tip `e3cd7d4`; nav package still applies; #98@`776fdb7`
all CI SUCCESS (still DRAFT; no new OpenAI comment since artifacts follow-up).
Math- D5 surfaces #17/#19/#20/#21 active — observe only (do not duplicate).
**Decision:** no new package; sole P1 = nav/handoff; resubscribe timer.

## 2026-09-25T20:40:30Z — d7-multimodel-loop timer

No material change since prior loop. Tip `e3cd7d4`; nav still applies; #98
green draft @`776fdb7`; zero new #98 comments after artifacts follow-up.
**Decision:** no new package; sole P1 = nav/handoff; renew #98 PR subscription;
resubscribe timer.

## 2026-09-25T20:45:30Z — OA-RECIPROCAL-REVIEW-20260925-D7 accepted (bounded)

**Facts:** OpenAI claimed nonauthor review of main #98@`776fdb7` and assigned
Cursor the reciprocal translation review of Math- PR18@`0ae7e8f` + trial
PR121@`391f6a8` (MATCH/AMEND per obligation; read-only author branches).

**This agent:** [Collaborative work progress](bc-01a0d95c-b9ca-70ce-864d-99d51b2a8fb0)
on sandbox (cannot write main comments). Produced
`experiments/oa_reciprocal_review_20260925/{REVIEW,PASTE_FOR_MAIN98}.md`.

**Judgments (provisional pending spot-check vote):** six MATCH + one AMEND
(`F10_CLOSED_NONPOSITIVE` additive closed clarification). No theorem acceptance.

**Decision:** P1 = ask main-write peer to paste acknowledgment onto #98; nav
demoted P2 for lease duration; do not edit Math-/trial author branches; no
unbounded agent fan-out beyond one spot-check vote.

## 2026-09-25T20:47:30Z — reciprocal review published on main #98 by peer

Peer Cursor agent posted full MATCH/AMEND table on main #98 (lease
OA-RECIPROCAL-REVIEW-20260925-D7). Sandbox paste ask **ABSORBED / do not
repaste**. Substance aligns with sandbox `REVIEW.md` (F10_CLOSED labeled
MATCH-as-additive there vs our AMEND — same meaning). Restore nav/handoff
as sole tip P1. Continue observe OpenAI adapter review on #98@`776fdb7`.

## 2026-09-25T20:48:30Z — peer vote: Claude P15 MATCH/AMEND spot-check

**Vote** ([Claude spot-check](bc-6e5072b3-7e9d-589f-8ddc-59b567aa9441)):
all seven obligations **MATCH**; `F10_CLOSED_NONPOSITIVE` MATCH as additive
non-strict clarification (not a misquote of printed `<0`); trial PR121
crosswalk **YES** consistent. `scientific_effect: NONE`.

**Disposition:** recorded. Aligns with peer forge comment on main #98
(MATCH-as-additive). Update sandbox `REVIEW.md` label AMEND→MATCH (additive)
for consistency. No new eng package. Pending votes: none for this lease.

## 2026-09-25T21:02:00Z — #98 AMEND_REQUIRED: package enforcement boundary

**Facts:** OpenAI executed nonauthor review at `776fdb7` (trial PR124): 9
controls pass, 7 defects reproduced. Asked @cursor to repair five families
and return a new head. Peer has not pushed yet. Reciprocal PR18 review already
on-thread — scheduling: enforcement package takes priority over further
translation churn.

**Decision:** Ship portable `pr98_enforcement_boundary_amend.patch` (local
smoke: 8/8 PR124 scenario flips; existing adapter unit tests green). Yield
race on #98 branch. Nav demoted to P2. Do not close #90.

## 2026-09-25T21:06:30Z — peer vote: package #98 five-defect amend

**Vote** ([Claude vote](bc-23c66df2-8580-51b5-a3a1-7c30b7555c92)):
A **YES** package all five families; B **NO** idle wait; C **NO** other packages.

**Disposition:** recorded and **already satisfied** — `pr98_enforcement_boundary_amend.patch`
was shipped prior to vote delivery. Continue observe #98 peer land → absorb;
nav stays P2. No further package this cycle.

## 2026-09-25T21:07:30Z — yield F1 to OpenAI claim OA-PR98-F1-REPAIR-20260925

**Facts:** OpenAI claims bounded F1-only corrective candidate on a **NEW**
branch forked from `776fdb7` (refuse unsupported new controlling / retained
controlling; allow demotion). Cursor branch untouched. Explicit ask: do not
concurrently duplicate F1 without coordination. F2–F5 remain separate/open.

**Decision:** Yield F1. Do not land/re-push competing F1. Keep
`pr98_enforcement_boundary_amend` as historical full recipe; coordinate before
full apply; F2–F5 still usable for Cursor peer. No new package. Nav stays P2.

## 2026-09-25T21:08:30Z — #98 five-family enforcement absorbed @`ebd7450`

**Facts:** Cursor peer pushed `ebd7450 fix(#90): enforce five OpenAI boundary
families…` on the schema branch (parent `776fdb7`). Sandbox
`pr98_enforcement_boundary_amend` **ABSORBED / do not re-apply**. Near-simultaneous
OpenAI claim `OA-PR98-F1-REPAIR-20260925` (F1-only on a NEW branch) — observe;
do not duplicate F1. CI on `ebd7450` in progress.

**Decision:** Mark package absorbed; restore nav/handoff as sole tip P1; watch
#98 CI + any OA F1 PR for coordination conflicts.

## 2026-09-25T21:09:19Z — d7-multimodel-loop timer

No material change since absorb. Tip `e3cd7d4`; nav package still applies;
#98@`ebd7450` verify IN_PROGRESS (nav + loss-only SUCCESS). Enforcement
package remains ABSORBED. OA F1 claim observe-only. No new package. Sole P1 =
nav/handoff. Resubscribe timer.

## 2026-09-25T21:25:15Z — d7-multimodel-loop timer

**Refresh:** tip still `e3cd7d4`; nav package still applies.
**#98** @`ebd7450` verify **SUCCESS** (all checks green); still DRAFT; OpenAI
re-review pending; OA F1 claim not yet a visible separate PR.
**Priority ambiguous?** No.
**Decision:** no new package; sole P1 = nav/handoff; observe #98 re-review;
resubscribe timer.

## 2026-09-25T21:33:30Z — OA F1 candidate delivered (trial PR128); observe only

**Facts:** OpenAI released claim OA-PR98-F1-REPAIR with trial draft PR128
`d61ebd6` — isolated F1 patch vs `776fdb7` (+ demotion paths). Cursor tip
`ebd7450` already has F1–F5 and stays untouched. OA asks nonauthor review;
F2–F5 not fixed in that package.

**Decision:** No sandbox eng package / no silent apply. Observe trial#128 +
main#98 re-review. Sole tip P1 remains nav/handoff.

## 2026-09-25T21:36:30Z — #98 CI green + OA F1 ACCEPT; yield tip port

**Facts:** CI subscription delivered SUCCESS on `ebd7450`. Cursor nonauthor
review ACCEPT’d trial#128 F1 vs `776fdb7`; patch does not apply cleanly onto
`ebd7450`; integration = author-lane port preserving F2–F5.

**Decision:** Confirm CI green in STATUS. Yield F1-port to #98 Cursor peer
(they hold the lease). No sandbox package/race. Sole tip P1 = nav/handoff.

## 2026-09-25T21:38:30Z — #98 F1 port landed @`6e3f774`

Cursor author ported OA-ACCEPT’d F1 from trial#128 onto tip without dropping
F2–F5. New head `6e3f774`. Sandbox yields; sole tip P1 = nav/handoff; watch
hosted CI + OpenAI re-review of combined tip. #90 OPEN / DRAFT.

## 2026-09-25T21:41:17Z — multi-model consult after #98 F1 port

**Trigger:** User continuous multi-model coordination; peer #98 head moved to
combined tip `6e3f774` (verify still IN_PROGRESS).

**Facts:** Tip inventable still `e3cd7d4`; `pr97_followup_nav_and_handoff.patch`
still applies. #98 peer-owned. Math- #14 CLOSED; #9/#30/#31 D5 observe-only.
All sandbox #98 packages ABSORBED. trial#128 observe-only.

**Pending votes:**
- [GPT vote](bc-d5be2b0e-36e9-50da-9284-41c521ef75c3)
- [Claude vote](bc-279a081c-7ef1-5808-ac44-55c7d49000de)

**Provisional decision (act now; adjust if votes disagree):**
1. A — Observe #98 CI + OpenAI re-review only; do not race/re-package.
2. B — Keep nav/handoff as sole tip P1 ready (unamplified while verify pending).
3. C — No new sandbox eng package.

**Sandbox next:** subscribe CI on `cursor/scientific-state-schema-crosswalk-31c5`,
keep PR/#98 + timer watches, refresh STATUS, push coordination, await votes.

## 2026-09-25T21:43Z — #98 comment: trial#128 V4 ACCEPT (observe)

Peer cursor[bot] upgraded V4 to **ACCEPT** on trial PR128 successor
`d61ebd6` (YAML pip-quote fix only). V1–V3/V5 prior ACCEPT stands. Explicit:
do not merge/promote on V4 alone; combined tip `6e3f774` still awaits OpenAI
re-review + hosted CI on that SHA.

**Decision:** no sandbox eng change. Continue observe #98@`6e3f774` CI;
trial#128 observe-only; nav sole tip P1. Pending multi-model votes unchanged.

## 2026-09-25T21:44Z — peer votes confirm provisional consensus

**Votes:**
- [GPT vote](bc-d5be2b0e-36e9-50da-9284-41c521ef75c3): A **YES**, B **YES**, C **NO**.
- [Claude vote](bc-279a081c-7ef1-5808-ac44-55c7d49000de): A **YES**, B **YES**, C **NO**.

**Consensus (confirmed):** observe #98 CI/OA re-review only; keep
`pr97_followup_nav_and_handoff` sole tip P1 unamplified; no new package.

**Sandbox next:** no eng package; watches already live (CI/PR/timer).

## 2026-09-25T21:44:44Z — d7-multimodel-loop timer (stale prompt delivery)

**Refresh:** tip still `e3cd7d4`; RESEARCH_INDEX still absent → nav package still
needed. #98 still `@6e3f774` verify IN_PROGRESS (nav/loss-only green; long
verify job at Bernstein replay step). No tip absorb of nav. No new peer push.

**Priority ambiguous?** No — GPT+Claude consensus already confirmed this minute.

**Decision:** no new package; no fresh model consult; sole P1 = nav/handoff;
continue observe #98 CI + OA re-review. Replacement timer already armed
(21:42Z); CI/PR watches live.

## 2026-09-25T21:46Z — OpenAI combined-tip re-review: F2 AMEND_REQUIRED

**Event:** OA comment on main#98 exact head `6e3f774`. F1 ported OK; F2–F5
present; **AMEND_REQUIRED for F2 source coverage** before #90 can close.
Keep DRAFT/#90 OPEN. CI still in progress (no green-tip claim).

**Gap:** controlling-hint nodes `Q0-C101-QUALITATIVE-RATE` /
`D1-v2.2(1)` are unresolved_prose; `unresolved_controlling_sources` is
report-only (impact-gated); prose multi-source + ignored structured keys +
ignored `repo` field leave load-bearing sources unmonitored.

**Pending votes:** [GPT](bc-5c344912-c2b4-5db1-b2bc-8c3e446c94ab),
[Claude](bc-40e3af3f-17e6-545c-b526-33d0badb737b).

**Provisional:** package portable F2 fail-closed amend against `6e3f774` for
main-write peer (do not push #98). Nav stays ready tip P1. Yield branch race.

## 2026-09-25T21:57Z — peer landed F2 @`47ad537` (sandbox package superseded)

**Facts:** While sandbox drafted `pr98_f2_source_coverage_amend` vs `6e3f774`,
Cursor peer pushed `47ad537 fix(#90): F2 fail-closed unresolved controlling
sources + migrate tip bindings` — in-repo `drive/mirrors/…` bindings for
Q0-C101 + D1-v2.2(1), fail-closed unmonitorable controlling, repo validation,
CLI negatives. Sandbox parallel recipe (external_frozen HOLD) **ABSORBED /
do not re-apply**.

**Pending F2 votes** ([GPT](bc-5c344912-c2b4-5db1-b2bc-8c3e446c94ab),
[Claude](bc-40e3af3f-17e6-545c-b526-33d0badb737b)) may still say package YES —
**live peer land overrides**.

**Decision:** Mark F2 package absorbed; sole tip P1 = nav/handoff; observe
#98@`47ad537` CI + OA re-review; no race.
