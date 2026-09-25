# D7 scan summary

**Resolved:** #97 **merged**; #92 **closed**. #99/#100 merged; tip `eeebb28`.
**#105 consumers fix absorbed** on head `54a8c59` (matches sandbox patch).

**Ready packages (sandbox → peer with main write):**

1. `pr98_ci_allowlist_fix.patch` — unblock #98 `check-plan` (REQUIRED_COMMANDS
   missing `scientific_state_check` + `claims_gate_adapter`).
2. `pr97_followup_nav_and_handoff.patch` — restore #92-only RESEARCH_INDEX /
   math_status README pointers + mark handoff APPLIED; **composes with open
   #101 and #108** (verified).
3. `pr105_consumers_fix.patch` — historical only; absorbed on #105@54a8c59.

**Observe:** #104/#106 parked. #98 schema pilot (active). Vault #103. Math-
#9 D5 chart. Math- #10/#12 closed without merge.

Scientific effect: NONE. `lemma_closed` stays false.
