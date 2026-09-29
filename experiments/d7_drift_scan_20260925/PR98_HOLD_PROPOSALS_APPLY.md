# Fix for main #98 hold_proposals fail-open — APPLIED

**Status: absorbed on #98 head `c1821b6`.** Peer commit
`fix(#90): surface unsatisfied_required in aggregate HOLD reports`
adds `aggregate_hold_proposals()` (includes `unsatisfied_required`) and
`audit_tip` hold counts.

Do **not** re-apply `pr98_hold_proposals_unsatisfied_fix.patch` on current #98
(patch no longer applies). Keep as historical recipe only. Watch CI on `c1821b6`.

Scientific effect NONE.
