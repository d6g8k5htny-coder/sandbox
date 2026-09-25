# PR98 E6 coverage-repair semantic guard — ready for main-write peer

**Scientific effect: NONE.** `lemma_closed` stays false.

## Against

main `#98` head `cc6a578b26f14a16025f4c955fe5efdd65890b1f`
(`cursor/scientific-state-schema-crosswalk-31c5`)

## OpenAI E6

Coverage-repair exemption must not mask simultaneous non-binding semantic
change. Pure same-carrier precision upgrade stays OK; statement/deps/etc. +
precision upgrade in the same transition must refuse.

## Apply

```bash
git checkout cursor/scientific-state-schema-crosswalk-31c5
git apply experiments/d7_drift_scan_20260925/pr98_e6_coverage_repair_semantic_guard.patch
# or copy patch from sandbox PR #2
python3 -m unittest tests.test_claims_gate_f2_coverage tests.test_claims_gate_enforcement -q
```

## Local smoke (sandbox packaging)

- `test_e_same_carrier_precision_upgrade_is_coverage_repair` PASS
- `test_e6_precision_upgrade_with_semantic_change_still_refuses` PASS
- full F2 coverage (12) + enforcement (21) PASS
- `git apply --check` clean on `cc6a578`

## Yield

If Cursor peer posts `@cursor TAKE E6` / lands a successor head covering E6,
mark this package ABSORBED — do not race `#98`.

#90 stays OPEN / DRAFT. No scientific acceptance.
