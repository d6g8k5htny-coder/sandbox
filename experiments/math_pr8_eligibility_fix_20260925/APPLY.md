# Apply — Math- PR #8 own-node eligibility fix

**Scientific effect: NONE.**

## Preferred source (do not race)

A peer Cursor agent with **main write** already filed the same repair on
hardening tip as:

- [MATH_PR8_ELIGIBILITY_HANDOFF_20260925.md](https://github.com/d6g8k5htny-coder/main/blob/cursor/downstream-crosswalk-outside-packet-31c5/docs/MATH_PR8_ELIGIBILITY_HANDOFF_20260925.md)
- patch: `docs/patches/math_pr8_own_node_eligibility.patch` on [main PR #92](https://github.com/d6g8k5htny-coder/main/pull/92)

**Prefer that main handoff** for Math- writers. This sandbox copy is a
parallel private backup (different symbol names: `POSITIVE_CONTROLLING_ELIGIBLE`
here vs `CONTROLLING_ELIGIBLE` there). Apply **one** patch only.

## Defect (shared)

`promotion_allowed()` allowed `AUTHOR_SIDE_CANDIDATE` → `controlling` when
required deps were terminal (reproduced on tip `5887a2f`).

## Sandbox backup apply (only if main handoff unavailable)

```bash
git clone https://github.com/d6g8k5htny-coder/Math-.git
cd Math-
git checkout 5887a2f8
git apply path/to/sandbox/experiments/math_pr8_eligibility_fix_20260925/pr8_own_node_eligibility.patch
cd frontiers/downstream_gate_20260925
python3 test_hard_gate.py
python3 run_validation.py --output /tmp/math8_val
# expect: 28 tests, 8 mutations, passed=true
```

This sandbox env cannot push Math- (403).
