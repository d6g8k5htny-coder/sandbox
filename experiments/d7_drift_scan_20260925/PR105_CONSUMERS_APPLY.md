# Fix for main #105 verify failure

**Status: NEEDED AGAIN on head `36fe375`.** Branch was rewritten to a single
CONTRIBUTION_PLAN commit; `registers/CONSUMERS.json` no longer lists
`docs/CONTRIBUTION_PLAN.md` under `lpw_fold_dispositions.prose`, so
`consumers_check` fails again.

```bash
git checkout cursor/contribution-plan-crosswalk-lpw-identity
git apply pr105_consumers_fix.patch
python3 tools/consumers_check.py   # expect problems=0
```

Scientific effect NONE.
