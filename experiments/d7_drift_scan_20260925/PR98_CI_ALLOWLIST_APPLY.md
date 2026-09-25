# Fix for main #98 verify failure — CI allowlist

**Scientific effect: NONE.**

`closure_pipeline.py check-plan` fails because `.github/workflows/ci.yml` adds:

- `python tools/scientific_state_check.py`
- `python tools/claims_gate_adapter.py`

but `tools/run_checks.py` `REQUIRED_COMMANDS` was not updated. The restricted
workflow parser rejects unfamiliar commands.

```bash
git checkout <pr98-branch>   # e.g. cursor/scientific-state-schema-crosswalk-31c5
git apply pr98_ci_allowlist_fix.patch
python tools/closure_pipeline.py check-plan   # expect PASS
```

Verified locally on #98 head: `PASS closure plan … 51 explicit checks`.
Does not flip scientific flags; schema checker remains pointers-only.
