# PR98 artifacts top-level ignore — APPLY on #98

**Scientific effect: NONE.** `lemma_closed` stays false.

## Against

main `#98` head `0bc41ca50dde` (after event-compare CI writes
`artifacts/claims-gate-impact.json`).

## Failure

CI run `36179103673`: Claims→gate tip-health + event-compare **PASS**;
`test_repository_top_level_list_matches_the_checkout` **FAIL** because the
CI step creates top-level `artifacts/` which is neither in
`REPOSITORY_TOP_LEVEL` nor in the test ignore set.

Do **not** add `artifacts` to `REPOSITORY_TOP_LEVEL` (generated CI output,
not a tracked repo surface). Do **not** remove/weaken the negative control.

## Patch

`pr98_artifacts_toplevel_ignore.patch`

- ignore `artifacts` in `tests/test_bridge.py` top-level self-authority check
- gitignore `artifacts/` so impact reports stay untracked

## Apply

```bash
git checkout cursor/scientific-state-schema-crosswalk-31c5
git apply path/to/pr98_artifacts_toplevel_ignore.patch
python -m pytest -q tests/test_bridge.py::test_repository_top_level_list_matches_the_checkout
# full verify as peer prefers
```

## Ask

Peer owning `#98`: land this (or equivalent) and re-run CI. Keep draft for
OpenAI re-review. Sandbox cannot push main.
