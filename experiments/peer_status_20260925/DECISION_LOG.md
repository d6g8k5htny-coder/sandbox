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
