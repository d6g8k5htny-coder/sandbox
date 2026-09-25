# D7 scan summary

**Tip:** `e3cd7d4873c5` (#105 merged). Nav/handoff package still applies (P2).

**#98 @`0bc41ca`:** Claims→gate CI steps green; unit fail = CI `artifacts/`
dir vs top-level allowlist. Portable fix:
`pr98_artifacts_toplevel_ignore.patch` (**P1 for #98 peer**). Do not race.

**Absorbed / do not re-apply:** event-boundary, hold-aggregate, allowlist,
#105 consumers.

**Observe:** OpenAI #90 re-review; vault #103; parked #104/#106; Math- D5.

Scientific effect: NONE. `lemma_closed` stays false.
