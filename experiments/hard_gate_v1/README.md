# hard_gate_v1 — private #90 prototype

Sandbox prototype of the owner hard-gate in
[main #90](https://github.com/d6g8k5htny-coder/main/issues/90):

- fail-closed on controlling promotion over non-terminal deps
- `BLOCKED_ABSENT` forces dependent HOLD
- reverse-impact report + required `REVALIDATION_REQUIRED` marking
- negative controls in `tests/test_hard_gate.py`

**Scientific effect: NONE.** Green tests here are not theorem discharge.
`lemma_closed` stays false. Not a live register; do not copy into public catalogs.

```bash
python3 hard_gate.py check fixtures/d0_d7_seed.json
python3 hard_gate.py reverse-impact fixtures/d0_d7_seed.json D1_parent_gaussian_KR
python3 tests/test_hard_gate.py
```
