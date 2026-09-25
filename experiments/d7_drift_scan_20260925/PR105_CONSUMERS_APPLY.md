# Fix for main #105 verify failure

`consumers_check` fails because `docs/CONTRIBUTION_PLAN.md` now names
`lpw_fold_dispositions` but is absent from `registers/CONSUMERS.json` prose list.

```bash
git checkout <pr105-branch>
git apply pr105_consumers_fix.patch
python3 tools/consumers_check.py   # expect problems=0
```

Scientific effect NONE.
