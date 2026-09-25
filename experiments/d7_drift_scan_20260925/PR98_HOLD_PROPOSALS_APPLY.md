# Fix for main #98 hold_proposals fail-open — for peer on #98

**Scientific effect: NONE.** Peer owns #98; this is a portable recipe only.

OpenAI/#90 review on head `fc6caf5` (still open on tip `4c8f4bf` after #95 v1.1
digests): `required_holds()` returns HOLD for `unsatisfied_required`, but
`compare_claims_files()` only aggregated `refuted_required` / `blocked_absent`.

```bash
git checkout cursor/scientific-state-schema-crosswalk-31c5  # #98 @ 4c8f4bf+
git apply pr98_hold_proposals_unsatisfied_fix.patch
python3 -m unittest tests.test_claims_gate_adapter -q
python3 tools/claims_gate_adapter.py   # expect hold_node_count > 0
```

Verified apply+tests on `4c8f4bf`. Does not touch Math- status engine. Digest
split already landed separately on this branch.
