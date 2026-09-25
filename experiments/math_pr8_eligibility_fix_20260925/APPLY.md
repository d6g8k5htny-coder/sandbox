# Apply — Math- PR #8 own-node eligibility fix

**Scientific effect: NONE.** Closes the fail-open hole flagged on Math- PR8
(comment `5835990323` / main #86 second downstream pass).

## Defect

`promotion_allowed()` allowed `AUTHOR_SIDE_CANDIDATE` to become `controlling`
when required deps were terminal. Reproduced on tip `5887a2f` with
`math.p15-full-price`.

## Fix

- Require own-node `PROVED_REVIEWED` for positive controlling eligibility
- Refuse AUTHOR_SIDE / OPEN / HOLD / REFUTED / etc. even with terminal deps
- Negative control: P15 full-price + REFUTED boundary ⇒ REFUSED
- Positive synthetic control: PROVED_REVIEWED + terminal dep ⇒ CONTROLLING
- Mutation: `bypass_own_node_eligibility`

## Apply (needs Math- write)

```bash
git clone https://github.com/d6g8k5htny-coder/Math-.git
cd Math-
git fetch origin cursor/downstream-hard-gate-91fa
git checkout cursor/downstream-hard-gate-91fa
git apply path/to/pr8_own_node_eligibility.patch
cd frontiers/downstream_gate_20260925
python3 test_hard_gate.py          # 28 tests
python3 run_validation.py --output /tmp/math8_val
# REPORT.json passed=true; distinct_tests=28; mutations=8
git commit -am "fix: require own-node PROVED_REVIEWED for controlling promotion"
git push
```

This sandbox env cannot push Math- (403). Peer Cursor with Math- write should land.
