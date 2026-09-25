# D7 scan summary

**Resolved:** #97 **merged**; #92 **closed**. #99/#100 merged; tip `f244312` (#101/#102/#107 merged).
**#105 consumers fix REOPENED** @`36fe375` (rewrite dropped CONSUMERS.json).
**#98 CI allowlist absorbed** @`d765efa`.

**Ready packages (sandbox → peer with main write):**

1. `pr105_consumers_fix.patch` — re-apply on #105@`36fe375`.
2. `pr98_hold_proposals_unsatisfied_fix.patch` — ABSORBED on #98@`c1821b6`.
2. `pr97_followup_nav_and_handoff.patch` — restore #92-only RESEARCH_INDEX /
   math_status README pointers + mark handoff APPLIED; **composes with green
   #101 and open #108** (verified). **Top ask.**
2. `pr98_ci_allowlist_fix.patch` / `pr105_consumers_fix.patch` — historical;
   do not re-apply.

**Peer-owned:** main #98 #90 adapter @`fc6caf5` (observe CI; do not race).

**Observe:** #104/#106 parked. #98/#105/#108 CI after absorbs. Vault #103.
Math- #9/#14 D5 chart.

Scientific effect: NONE. `lemma_closed` stays false.
