# Alignment — Math- tip is the eng hard-gate surface

Canonical executable gate for [main #90](https://github.com/d6g8k5htny-coder/main/issues/90) /
[#86](https://github.com/d6g8k5htny-coder/main/issues/86) D0/D7:

- Math- `main` `frontiers/downstream_gate_20260925/` (PR #8 merged; later
  clarifications include required-REFUTED HOLD + `reverse_impact_between`)
- Observed Math- tip carrying `CONTROLLING_ELIGIBLE={PROVED_REVIEWED}`:
  `baca69c394ab`
- Human crosswalk landed via inventable [#97](https://github.com/d6g8k5htny-coder/main/pull/97)
  (superseded Cursor [#92](https://github.com/d6g8k5htny-coder/main/pull/92))

This `hard_gate_v1/` tree is a **private pedagogical / negative-control sandbox**
with a simpler list-of-nodes schema (`sandbox.hard-gate/v1`). It mirrors the
eligibility + REFUTED-premise rules above but is **not** a second live register
and must not race Math- file paths.

Scientific effect: **NONE**. `lemma_closed` stays false.

```bash
./peer_probe_math_pr8.sh   # shallow-clone Math- tip and re-run their tests
python3 tests/test_hard_gate.py
```
