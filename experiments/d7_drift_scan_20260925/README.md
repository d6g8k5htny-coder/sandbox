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
| `pr105_consumers_fix.patch` | main #105 verify |
| `pr97_followup_nav_links.patch` | tip after #97 (+ composes with #101) |
| `pr_handoff_applied.patch` | tip handoff prose (Math- already fixed) |

Scientific effect NONE. Does not merge or close PRs (sandbox cannot push main).
