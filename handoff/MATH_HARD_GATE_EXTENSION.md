# Extending the Math- hard gate with the formal lane

**Target:** Math- `frontiers/downstream_gate_20260925/hard_gate.py` (+ `GRAPH.json`,
`test_hard_gate.py`, `SOURCE_FILES.json`, `RESULTS.json`, `run_validation.py`).
**Scientific effect: NONE.** This adds a stricter *necessary* criterion; it removes no
existing rule and promotes nothing.

The hard gate today decides `promotion_allowed(graph, node)` from classifications
(`PROVED_REVIEWED` etc.) and refuses promotion justified only by non-discharge tokens
(`GREEN_CI`, `HASH_MATCH`, …). The extension makes the gate aware of Layer 1 without
letting Layer 1 decide anything on its own.

## 1. Node field

```json
"math.side24-coefficient": {
  "...": "...",
  "formalization": {
    "status": "specified",                      // none | specified | proved | kernel-checked  (object-level = min over required components)
    "review": "author-side",                    // none | author-side | nonauthor-aligned
    "required": false,                          // when true, CONTROLLING needs the formal lane satisfied
    "evidence": {
      "repository": "d6g8k5htny-coder/Math-",   // where formal/ lives after the port
      "status_file": "formal/FORMALIZATION_STATUS.json",
      "commit": "<full OID>",
      "sha256": "<sha256 of the status file>"
    }
  }
}
```

Missing `formalization` ⇒ treated as `{"status": "none", "review": "none", "required": false}`.
`formalization.required` defaults to `false` so that existing nodes behave exactly as
today; turning it on for a node is an explicit, reviewable graph edit.

**Validation (fail-closed, in `_validate_graph_shape`):** status/review must be exact
strings from the ladders; `required` must be an exact boolean; `evidence.commit` a full
40-hex OID when status ≠ `none`; `review ≠ none` requires `status ≠ none`.

## 2. Tokens

Extend `NON_DISCHARGE_DEFAULT` (and `GRAPH.json.non_discharge_tokens`) with

```
FORMAL_SPECIFIED, FORMAL_PROVED_AUTHOR_SIDE, KERNEL_CHECKED_AUTHOR_SIDE, KERNEL_CHECKED_CONDITIONAL
```

and add `KERNEL_CHECKED_NONAUTHOR_ALIGNED` to the *known* (not non-discharge) list in
`refuse_non_discharge_promotion`. A promotion justified **only** by
`KERNEL_CHECKED_NONAUTHOR_ALIGNED` must still be refused: it satisfies one lane, and the
analytic lanes (`LINE_BY_LINE_ANALYTIC_REVIEW`, `PROVED_REVIEWED`) are still required.
Implement as: `only_non_discharge or tokens == {KERNEL_CHECKED_NONAUTHOR_ALIGNED}` ⇒ refused
with reason `formal lane alone is not theorem acceptance`.

## 3. Rule in `promotion_allowed`

```python
formal = node.get('formalization', {'status': 'none', 'review': 'none', 'required': False})
if formal.get('required'):
    if formal['status'] != 'kernel-checked' or formal['review'] != 'nonauthor-aligned':
        reasons.append('formal lane required: needs kernel-checked + nonauthor-aligned')
```

Return the formal record in the decision (`'formalization': formal`) so the museum can
display it. Nothing else in the decision changes.

## 4. Reverse impact

A change of `formalization.evidence.sha256` or of `status`/`review` on a node is a node
record change; `reverse_impact_between` already marks dependents `REVALIDATION_REQUIRED`
because it compares complete canonical node records. No new code; add a test asserting it.

## 5. Sync from Layer 1 (no manual editing of the field)

Add `tools/sync_formalization.py` (stdlib): reads `formal/FORMALIZATION_STATUS.json`, runs
`formal_gate.run_gate()`, and for each `objects[].hard_gate_node` writes
`status = min(verified_status over components)`, `review = min(verified_review …)`,
`evidence.sha256 = sha256(status file)`, `evidence.commit = HEAD`. Refuse (exit 2) if the
gate did not pass. Run it in the same commit as any Lean change; CI runs it with `--check`
and `git diff --exit-code`. The gate output is the only writer of `formalization`.

## 6. Tests and mutants to add (`test_hard_gate.py`)

1. `formalization.required=true` + status `specified` ⇒ not allowed, reason present.
2. `required=true` + `kernel-checked` + `author-side` ⇒ not allowed.
3. `required=true` + `kernel-checked` + `nonauthor-aligned` + node `PROVED_REVIEWED` + deps satisfied ⇒ allowed (and identical to today's outcome when `required=false`).
4. Tokens `['KERNEL_CHECKED_AUTHOR_SIDE']` ⇒ refused as non-discharge.
5. Tokens `['KERNEL_CHECKED_NONAUTHOR_ALIGNED']` alone ⇒ refused (`formal lane alone`).
6. `formalization.status = 'accepted'` ⇒ `ValueError('unknown formalization status')`.
7. `required = 'true'` (string) ⇒ `ValueError`.
8. `review = 'nonauthor-aligned'` with `status = 'none'` ⇒ `ValueError`.
9. Evidence sha256 change on a node ⇒ dependents `REVALIDATION_REQUIRED`.
10. `hist.lemma_closed` with a formalization record ⇒ still `FALSE`, never promoted.

Update the documented counts (`67 distinct tests / 24 mutants` → new numbers) in
`README.md`, `run_validation.py` and the workflow assertion together, and regenerate
`SOURCE_FILES.json` / `RESULTS.json` on the final tree (measured amendment: pins fail
first otherwise).

## 7. Museum (main)

`tools/museum_data.py` gains a `formalization` field per displayed source, read from the
Math- `GRAPH.json` node at the pinned Math commit. Display the ladder value and the
token name verbatim; never render `kernel-checked` as "verified".
