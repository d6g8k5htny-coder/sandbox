# D7 drift scan — 2026-09-25

Private eng scan for main #86 Cursor D7 assignment after D0 gate merge:

- stale schema / live-tip assumptions
- duplicate review surfaces
- misleading Actions labels
- navigation / catalog drift

See `REPORT.json` / `SUMMARY.md`. Refresh inventable watch:

```bash
python3 refresh_inventable_overlap.py
```

Ready apply packages for peers with main write:

| Package | Target |
| --- | --- |
| `pr98_ci_allowlist_fix.patch` | main #98 check-plan allowlist |
| `pr105_consumers_fix.patch` | main #105 verify (ABSORBED @54a8c59) |
| `pr97_followup_nav_links.patch` | tip after #97 (+ composes with #101) |
| `pr_handoff_applied.patch` | tip handoff prose (Math- already fixed) |

Scientific effect NONE. Does not merge or close PRs (sandbox cannot push main).

- `pr98_event_boundary_amend.patch` — ABSORBED on #98@`4b983b9` (do not re-apply).

- `pr98_artifacts_toplevel_ignore.patch` — P1 for #98@`0bc41ca` (CI artifacts/ ignore).

- `pr98_enforcement_boundary_amend.patch` — P1 for #98@`776fdb7` (OpenAI five-family AMEND).
