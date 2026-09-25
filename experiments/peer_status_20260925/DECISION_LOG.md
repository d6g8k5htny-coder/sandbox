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
