# Fix for main #105 verify failure — RESOLVED (alternate path)

**Status: obsolete on head `2440881`.** Peer rewrote the LPW crosswalk to
point through `research/lpw/README.md` instead of citing
`registers/json/lpw_fold_dispositions.json`, so `consumers_check` passes with
`problems=0` without editing `CONSUMERS.json`.

Do **not** re-apply `pr105_consumers_fix.patch` on current #105 (would add a
prose consumer the docs no longer require). Keep as historical recipe for the
earlier cite-based failure mode.

Scientific effect NONE.
