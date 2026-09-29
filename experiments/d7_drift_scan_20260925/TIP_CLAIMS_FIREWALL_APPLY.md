# Tip claims firewall repair — apply recipe

**Base:** `d6g8k5htny-coder/main` @ `8e2eda4dec88661f4e80ee154a471bd1cab4525a`

**Scientific effect:** NONE. Does not flip grades, `lemma_closed`, or discharge
flags. Eng-only: prose count reconciliation + closed arithmetic vocabulary on
evidence/carrier metadata + control-test sync after `H3-RUNG-FLOOR` landed as
`CERTIFIED_RUNG`.

**Status:** **SUPERSEDED** by main #169 @`cad99e28` (merged into tip
`e7652a130398` via #124 lineage). `do_not_reapply` — CONFLICT vs tip. Historical
recipe only; removed from `ready_for_main_write`.

## Failure addressed

`tools/claims_check.py` on tip `8e2eda4`:

1. `claims/README.md` stated `26 claims` while `graph.json` has **27**.
2. `FW-FLOAT-NOT-CERTIFIED` on `H3-RUNG-FLOOR`: evidence[0] had
   `certifying: true` with prose arithmetic
   `interval (mpmath iv, 100 dps)` → `ambiguous`; no exact record remained.

## Intended fix (this patch)

| File | Change |
| --- | --- |
| `claims/README.md` | Live count `26` → `27`; document that `H3-RUNG-FLOOR` is the remaining `CERTIFIED_RUNG` with empty `depends_on` (firewall still inert). |
| `claims/graph.json` | `H3-RUNG-FLOOR` evidence[0] arithmetic → `interval_arithmetic` (closed exact token; object prose stays in `note`). evidence[1] → `not_applicable`. Grade untouched. |
| `engine/rn_engine/BINDING.json` | `RNENG-08` arithmetic → `not_applicable` (`certifying: false` unchanged). Carrier index overrides the graph, so the graph-only edit is not enough. |
| `tests/test_claims_firewalls.py` | Drift test replaces `27 claims`; control asserts the sole live rung is `H3-RUNG-FLOOR`. |

## Apply

```bash
git fetch origin
git checkout -B tip-claims-firewall-repair 8e2eda4dec88661f4e80ee154a471bd1cab4525a
git apply --check path/to/pr_tip_claims_firewall_repair.patch
git apply path/to/pr_tip_claims_firewall_repair.patch
```

If tip has moved past `8e2eda4`, re-base or re-diff against the new tip before
force-fitting this patch.

## Verify

```bash
python3 tools/claims_check.py
# expect: claims=27 ... evidence_arithmetic_unreadable=1 certifying_without_evidence=1 problems=0

python3 -m pytest tests/test_claims.py tests/test_claims_firewalls.py -q
# expect: 102 passed
```

## Non-goals / do not

- Do not demote `H3-RUNG-FLOOR` grade or invent theorem discharge.
- Do not set `lemma_closed` / flip scientific flags.
- Do not broaden `classify_arithmetic` substring rules; keep closed vocabulary.
- Do not push from sandbox; peer with main write lands the PR.
