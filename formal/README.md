# Layer 1 — formal verification (Lean 4 + Mathlib)

**Object:** FORMAL-LAYER-20260927-v1. **Engineering author:** Cursor cloud agent
(Anthropic / Claude), author-side. **Scientific effect: NONE.** `lemma_closed` stays
`false`; nothing here promotes, closes or discharges a claim.

## What this is

The research stack already has **Layer 0**: provenance (SHA-256, commits, blobs),
explicit scope and "does not claim" statements, review-status tracking, the fail-closed
Math- hard gate and the public verification museum. Layer 0 verifies *identity* and
*process*. It cannot verify *logic*.

Layer 1 adds machine-checked logic without replacing anything:

| Layer | Verifies | Where |
|---|---|---|
| 0 provenance / scope / hard gate | these bytes are the reviewed bytes; scope is explicit; promotion is fail-closed | Math- `frontiers/downstream_gate_20260925`, `claims/LANDING_CLAIMS.json`, main museum |
| **1 formal (this directory)** | the encoded statement is a theorem of Lean 4 + Mathlib (kernel-checked); the statement text is byte-bound to the informal object | `formal/lean`, `FORMALIZATION_STATUS.json`, `BUILD_EVIDENCE.json` |
| 1r alignment review | the Lean statement means what the prose means | `FORMALIZATION_REVIEW_LANE.md`, `formal/reviews/` |
| 2 analytic nonauthor review, peer review | significance and correctness of the informal mathematics | main issues (#63, #65 …), journals |

The hard gate is meant to enforce that no lane is skipped. Layer 1 emits tokens for it
(below); it never decides promotion.

## Status ladder (`formalization_status`) and review ladder

```
none < specified < proved < kernel-checked          formalization_review: none | author-side | nonauthor-aligned
```

* `specified` — the statement (or object) is a Lean definition that compiles. Nothing proved.
* `proved` — a sorry-free Lean theorem exists in the pinned module (text-level, author-side).
* `kernel-checked` — `BUILD_EVIDENCE.json` records `lake build` success and
  `#print axioms ⊆ {propext, Classical.choice, Quot.sound} ∪ registered assumed axioms`,
  bound to exactly the pinned source bytes.

`formal_gate.py` recomputes the *verifiable* level for every component and fails if the
*declared* level is higher. Declared ≤ verifiable is the only direction allowed.

Tokens handed to the Math- hard gate (see `handoff/MATH_HARD_GATE_EXTENSION.md`):

| Token | When | Discharge? |
|---|---|---|
| `FORMAL_SPECIFIED` | statement exists | non-discharge |
| `FORMAL_PROVED_AUTHOR_SIDE` | sorry-free theorem, no kernel evidence | non-discharge |
| `KERNEL_CHECKED_AUTHOR_SIDE` | kernel evidence, alignment unreviewed | non-discharge |
| `KERNEL_CHECKED_CONDITIONAL` | kernel evidence but depends on a registered assumed axiom (e.g. an unformalized parent theorem) | non-discharge |
| `KERNEL_CHECKED_NONAUTHOR_ALIGNED` | kernel evidence **and** a distinct reviewer's alignment record bound to these bytes, no assumed axioms | satisfies the *formal lane only*; analytic lanes and #90 rules still apply |

## Pilot: SIDE24 coefficient (Math- `coefficients/side24_v1/PROOF.md`)

Bound to commit `760340e921ac4ceda296b8118da936f1133e956e`, sha256
`c06daccc…7769` (the same identity the museum and `GRAPH.json` pin). 22 components:

* **kernel-checked (16):** the §2–§4 arithmetic ledger (image constant, `e^{288/125} > 10`
  via Mathlib's exponential partial sums, `e^{-288} < 10^{-125}`, `512e^{-864} < 1/2`,
  `60E < ε`, `32ε < 10^{-106}`, exponent budgets for `d = 2, 3`); the §1 cone integral
  `∫₀ᵃ (a−z)²e^{−z/2}dz/2 = a²−4a+8−8e^{−a/2}`; the §1 Gaussian inputs `E s⁴ = 25/3` (via
  the MGF `mgf_id_gaussianReal`) and `E e^{−s²/2} = √(3/8)` (via `integral_gaussian`) for
  `s ~ N(0, 5/3)`; the algebra `D₂ = 29/6 − √6`, its outward enclosure and `D₂ < 29/6`
  (truncation essential); the §5 transfer lemma and the implication
  *(reference enclosure ∧ eq. (4)) ⇒ displayed 20-digit bounds*.
* **specified (6):** the §4 ratio bound `1 ± 32ε`; the reference coefficient eq. (1) as a
  definition; the author's 80-digit reference enclosure; eq. (4); and the displayed
  theorem itself.

The periodic coefficient `c_{d,24}` is **not** defined in Lean because its definition is
the unformalized parent (main #63, eq. 15.2). Every statement about it is parametrized by
an arbitrary `c : ℕ → ℝ`, so the hypotheses of `Side24.enclosure_of_reference` *are* the
scope. No parent theorem is introduced as an axiom; the `assumed_axioms` registry is
empty. The headline theorem therefore stays `specified`, honestly.

The private sandbox Monte Carlo (`experiments/cone_v1`) samples `D₂` — it is now a
sanity check against a kernel-checked constant, and still not evidence of anything.

## Run

```sh
python -B -S formal/pin_sources.py --check                  # Lean bytes match SOURCE_FILES.json
python -B -S formal/formal_gate.py                          # status ≤ evidence, alignment bytes, axioms
python -B -S formal/blueprint_check.py                      # blueprint ↔ status
python -B -S -m unittest discover -s formal -p 'test_*.py' -v
python -B -O -S -m unittest discover -s formal -p 'test_*.py' -v
python -B -S formal/run_validation.py --output /tmp/formal-gate-new-run
```

27 distinct tests and 33 assertion-detected semantic mutants are required in both Python
modes. With a Lean toolchain (`elan`, toolchain in `formal/lean/lean-toolchain`):

```sh
cd formal/lean && lake exe cache get && lake build && cd ../..
python -B -S formal/lean_build_evidence.py --check          # regenerate evidence, cmp with committed
```

CI (`.github/workflows/formal-gate.yml`) runs both: the Python controls, and a Lean job
that rebuilds with the Mathlib cache, regenerates `BUILD_EVIDENCE.json` and refuses any
byte difference.

## Changing anything

* Edit a `.lean` file → regenerate `SOURCE_FILES.json` (`pin_sources.py`) and
  `BUILD_EVIDENCE.json` (`lean_build_evidence.py`) in the same commit, and update the
  `lean_statement` of any component whose header changed. Any `nonauthor-aligned` review
  of that module is now stale (hash mismatch) and must be redone — by design.
* Add a theorem → add a component (`informal_ref`, `lean_statement`, `does_not_claim`),
  a blueprint environment, and a glossary row for any new project term.
* Need a parent theorem you cannot prove → do **not** add `sorry`. Either parametrize
  (preferred, as here) or add a Lean `axiom` *and* a registry entry with a scope note; the
  dependent theorems become `KERNEL_CHECKED_CONDITIONAL`.
* Never widen `standard_axioms`, never set `lemma_closed`/`mathematical_acceptance`, never
  extend the ladders. Each of these is a refused mutant.

## Files

| File | Role |
|---|---|
| `lean/` | Lake project (`Side24Formal`), toolchain `leanprover/lean4:v4.34.1`, Mathlib `v4.34.1` |
| `FORMALIZATION_STATUS.json` | per-component declared status, verbatim statements, informal source binding |
| `SOURCE_FILES.json` | byte/sha256 pins of the Lean project |
| `BUILD_EVIDENCE.json` | deterministic `lake build` + `#print axioms` record (no timestamps) |
| `formal_gate.py`, `test_formal_gate.py` | the gate and its mutants |
| `blueprint/`, `blueprint_check.py` | Lean Blueprint document and alignment check |
| `GLOSSARY.md` | project terms → standard mathematics → Lean names |
| `FORMALIZATION_REVIEW_LANE.md` | alignment reviewer protocol and record format |
| `run_validation.py` | both-mode replay with `REPORT.json` |

## Roadmap (from the Layer 1 plan)

1. ✔ Pilot on SIDE24 (this directory). 2. ✔ Glossary. 3. ✔ Review lane defined (no
review yet — every component is `author-side`). 4. ✔ CI `lake build` + evidence replay
here; **Math- hard gate extension pending** (see `handoff/`). 5. Expand: prove the
remaining `specified` Props (the `1 ± 32ε` ratio bound; `Γ(7/6)`/`π` enclosures — the
Gaussian moments were `specified` in the first revision and are now kernel-checked, which is
the intended ladder progression), then the next Math- object (BF six-pin certificates are exact
finite arithmetic — good candidates). 6. External validation once a nonauthor alignment
review exists. 7. AI-prover cross-check lane: run an independent Lean prover on the
`specified` Props; any kernel-accepted proof is recorded as evidence with its own
provenance, still author-side until aligned.
