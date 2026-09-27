# Formalization review lane (statement alignment)

**Object:** FORMAL-REVIEW-LANE-20260927-v1. **Scientific effect: NONE.**

The Lean kernel already re-checks every proof. What it cannot check is whether the
Lean *statement* says what the informal theorem says. That is the only job of this
lane. The reviewer does **not** re-prove anything.

This lane sits beside — and does not replace — the existing review topology
([`governance-/REVIEW_TOPOLOGY.md`](https://github.com/d6g8k5htny-coder/governance-/blob/main/REVIEW_TOPOLOGY.md)):
author derivation, same-author replay, nonauthor analytic review and formal
verification stay distinct. An `ALIGNED` verdict here is *evidence consumed by* the
Math- hard gate; it never assigns scientific status by itself.

## Ladder

| `formalization_review` | Meaning | Who may set it |
|---|---|---|
| `none` | component has no Lean artifact | — |
| `author-side` | the formal author wrote both the Lean text and the `lean_statement` binding; unreviewed | the formal author (default) |
| `nonauthor-aligned` | a distinct reviewer attested statement alignment; record bound to the module sha256 | only by adding a review record that `formal_gate.py` accepts |

`formal_gate.py` refuses `nonauthor-aligned` unless the record exists, has verdict
`ALIGNED`, binds the *current* module bytes and the *current* `lean_statement`, and
declares `authored_formalization: false`. Any edit to the Lean module stales the
review (hash mismatch → gate FAIL) — carrying approval across heads silently is
impossible by construction.

## Reviewer checklist

For each component under review (one record per component):

1. **Read the informal statement** at the exact pinned source
   (`objects[].informal_source`: repository / path / commit / sha256). Read the
   `informal_ref` pointer (section, equation).
2. **Read the Lean declaration** named `lean_decl` in `lean_module` at the pinned
   sha256 (`SOURCE_FILES.json`). Confirm `lean_statement` is the declaration you read.
3. **Check hypotheses = scope.** Every hypothesis of the Lean theorem must be either
   in the informal statement or explicitly listed in `does_not_claim` / the docstring.
   Anything the Lean statement assumes that the prose does not, or vice versa, is a
   finding.
4. **Check quantifiers, domains, normalisations.** Real vs rational literals, strict vs
   non-strict inequalities, `ℕ` subtraction, `d ∈ {2,3}` vs all `d`, measure
   normalisation (`gaussianReal 0 v` takes the *variance* `v`), interval endpoints.
5. **Check the glossary.** Every project term in the informal statement must have a
   `MAPPED` row in `GLOSSARY.md` whose standard object is what the Lean text encodes.
6. **Check `does_not_claim`.** It must be accurate and not understate what the Lean
   statement leaves open.
7. **Check `conditional_on`.** If the gate report lists assumed axioms, confirm each
   has a scope note in the `assumed_axioms` registry and that the informal source
   treats the same dependency as open.
8. Record **one** of: `ALIGNED`, `AMEND_REQUIRED` (with the exact mismatch), or
   `BLOCKED` (cannot read the pinned source). `AMEND_REQUIRED`/`BLOCKED` are recorded
   findings, never acceptance.

## Record format (`formal/reviews/<component-id>.<reviewer>.json`)

```json
{
  "review_id": "FREV-20260927-side24.ledger.image-constant-openai",
  "component_id": "side24.ledger.image-constant",
  "verdict": "ALIGNED",
  "reviewed_module": "Side24Formal/Ledger.lean",
  "reviewed_module_sha256": "<sha256 from SOURCE_FILES.json at review time>",
  "reviewed_lean_statement": "<verbatim lean_statement at review time>",
  "informal_source": {"repository": "d6g8k5htny-coder/Math-", "path": "coefficients/side24_v1/PROOF.md", "commit": "760340e921ac4ceda296b8118da936f1133e956e", "sha256": "c06daccc4ba4b9168522b9888b76a7d599934fc3b91bd753ee5d492262917769"},
  "findings": [],
  "reviewer_provenance": {
    "provider": "OpenAI",
    "model_family": "GPT",
    "session": "UNKNOWN",
    "authored_formalization": false,
    "source_exposure": "read pinned PROOF.md and Ledger.lean only"
  },
  "timestamp": "2026-09-27T00:00:00Z",
  "scientific_effect": "NONE"
}
```

Provenance rules follow REVIEW_TOPOLOGY v1.1: unknown values stay `UNKNOWN`; a
same-provider or unknown-provider review earns **no** organizational-independence
credit (the gate reports `organizational_independence: false` in that case, and
`ATTESTED_NOT_VALIDATED` otherwise — never `true`, because no validator exists).
The reviewer who edits the Lean file becomes a co-author of the successor and cannot
supply its nonauthor key.

## What the lane is not

* Not a proof check — the kernel does that (`BUILD_EVIDENCE.json`).
* Not an analytic review of the informal theorem — that stays on main issues (#63, #65).
* Not organizational-independence validation — attested only.
* Not promotion — even `KERNEL_CHECKED_NONAUTHOR_ALIGNED` on every component only
  satisfies the *formal lane* of the Math- hard gate; the analytic lanes and the #90
  rules still apply, and `lemma_closed` stays `false`.
