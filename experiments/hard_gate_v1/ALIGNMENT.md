# Alignment — Math- PR #8 is the eng hard-gate surface

Canonical executable gate for [main #90](https://github.com/d6g8k5htny-coder/main/issues/90) /
[#86](https://github.com/d6g8k5htny-coder/main/issues/86) D0/D7:

- [Math- PR #8](https://github.com/d6g8k5htny-coder/Math-/pull/8)
  (`frontiers/downstream_gate_20260925/`, schema_version 1, 24 tests)
- Human crosswalk + node-ID map: [main PR #92](https://github.com/d6g8k5htny-coder/main/pull/92)
- Default-home pointer: [main PR #93](https://github.com/d6g8k5htny-coder/main/pull/93)

This `hard_gate_v1/` tree is a **private pedagogical / negative-control sandbox**
with a simpler list-of-nodes schema (`sandbox.hard-gate/v1`). It is **not** a
second live register and must not race Math- PR #8 file paths.

Scientific effect: **NONE**. `lemma_closed` stays false.

```bash
./peer_probe_math_pr8.sh   # shallow-clone Math- tip and re-run their tests
python3 tests/test_hard_gate.py
```
