# Formal glossary — project terms → standard mathematics → Lean

**Object:** FORMAL-GLOSSARY-20260927-v1. **Scientific effect: NONE.** This table
changes no claim status. It exists so that every non-standard term used in the
research repositories has a standard mathematical meaning *before* it is formalized,
and so that external readers (journals, Lean community, AI provers) can read the work
without project vocabulary.

Rules (from the Layer 1 roadmap):

1. A term that cannot be mapped to a standard object is either **ill-defined** or
   **novel**. Both are recorded as `UNMAPPED`; novelty must be justified against the
   literature before the term is used in a Lean statement.
2. A Lean name in the last column means the standard object is *defined* in
   `formal/lean`. It does not mean anything about it is proved; see
   `FORMALIZATION_STATUS.json` for the status of each statement.
3. Extend this table in the same change that introduces a new term to a Lean file.

| Project term | Where it is used | Standard mathematical object | Lean (`Side24` namespace) | Mapping status |
|---|---|---|---|---|
| Universal Law mathematics | repo names (`query-`, ULW) | Umbrella label for the programme: **Gaussian random fields** and **persistent homology of excursion/level sets** (H₀ bars of a smooth Gaussian field on a torus). Not a mathematical object. | — | PROJECT-LABEL |
| SIDE24 / `K_24` | Math- `coefficients/side24_v1` | Stationary centred Gaussian field on the flat torus `(ℝ/24ℤ)^d`, `d ∈ {2,3}`, with covariance the **periodisation** of the Gaussian kernel `exp(-|z|²/2)`, normalised to variance one | not yet (covariance not formalised) | MAPPED (definition only in prose) |
| image sum / omitted periodic images | PROOF.md §2 | The lattice sum `Σ_{n≠0} φ(z+24n)` and its derivatives; the **Poisson-periodisation remainder** | arithmetic inputs only: `image_constant_eq`, `exp_neg_288_lt`, `geometric_ratio_lt_half` | MAPPED |
| contact covariance / reference law | PROOF.md §1 | Joint Gaussian law of `(∇f, ∇²f, ∂₁³f)` at a point for the non-periodic kernel `exp(-|z|²/2)`; conditional covariance via **Schur complement** | — | MAPPED (not formalised) |
| shared scalar shift `Z I_m` / `s` | PROOF.md §1 | Trace-direction component of the conditional Hessian; a centred Gaussian scalar with variance `5/3` for `m=2` | `gaussian_fourth_moment`, `gaussian_exp_moment` | MAPPED |
| cone moment `D_m` | PROOF.md §1, ENCLOSURE.json | `E[det(A)² · 1{A ≺ 0}]` for the conditional Gaussian symmetric `m×m` matrix `A`; the **negative-definite cone** is `{A ≺ 0}` | `D2`, `coneMoment`, `cone_integral_identity`, `D2_algebra` | MAPPED |
| untruncated half moment | PROOF.md §1 | `½·E[det(A)²]` without the indicator; the incorrect value `29/6` | `D2_lt_untruncated` | MAPPED |
| lifetime coefficient `c_{d,24}` | PROOF.md, main #63 eq. 15.2 | Leading coefficient in the **Kac–Rice** expression for the density of H₀ bar lifetimes (birth–death gaps) of the field; defined by the parent source | *parametrised* as an arbitrary `c : ℕ → ℝ` in `enclosure_statement`, `periodization_statement` | MAPPED-BY-REFERENCE (parent unformalised) |
| reference coefficient `c_{d,ref}` | PROOF.md eq. (1) | `Γ(7/6)·(3/2)^{1/3}·D_{d-1} / (2√3·π^{d-1}·√π)` | `referenceCoefficient` | MAPPED |
| lifetime density / per-unit-volume lifetime density | Math- `LIFETIME_REMAINDER.md`, LANDING_CLAIMS | Intensity measure (w.r.t. `dℓ`) of the point process of finite H₀ bar lengths of a Gaussian field on a torus, normalised by volume | — | MAPPED (not formalised) |
| elder rule / elder selection | main #63, `LIFETIME_REMAINDER.md` | Standard **elder rule** of persistent homology: when two components merge at a saddle, the younger (higher-birth) component dies | — | MAPPED (standard term) |
| elder density | main #63 | Conditional density of critical points (saddle/maximum pairs) given the elder-rule pairing event — i.e. a conditional Kac–Rice density | — | MAPPED (prose only) |
| candidate density | project reviews | Density of a *specified* Gaussian field model proposed as a candidate; the word "candidate" is a review status, not mathematics | — | PROJECT-LABEL |
| pin / pin Jacobian / height-gradient pin | PROOF.md, RN packages | Conditioning on `∇f = 0` (and a height value) in Kac–Rice; the Jacobian factor `|det ∇²f|` | — | MAPPED |
| RN / 24-jet / JETMOD | GRAPH.json, governance | Project labels for a family of remainder/jet-modulus obligations on the D3–D5 layers; each must be mapped individually when formalised | — | UNMAPPED (label family; map per object) |
| P15 | Math- `frontiers/*price*` | A **combinatorial optimisation** family (price budgets, palettes, demands) unrelated to Gaussian fields; own glossary needed | — | OUT-OF-SCOPE for this glossary |
| outward rational arithmetic | coefficient.py | **Interval arithmetic** over ℚ with outward rounding to a fixed grid `10^{-80}` | rational endpoints `ref2Lo`, …; transfer lemma `perturbed_bounds` | MAPPED |
| periodization allowance | PROOF.md §5 | Relative error bound `|c/c_ref − 1| < 10^{-106}` applied multiplicatively to the reference enclosure | `periodizationBound`, `enclosure_of_reference` | MAPPED |
| hard gate | Math- `frontiers/downstream_gate_20260925` | Engineering: fail-closed promotion control over a dependency graph. Not mathematics. | — | ENGINEERING |
| verification museum | main `docs/site` | Engineering: public display of pinned source bytes and review status. Not mathematics. | — | ENGINEERING |
| kernel-checked | this layer | A Lean 4 declaration accepted by the Lean kernel with `#print axioms ⊆ {propext, Classical.choice, Quot.sound}` at pinned source bytes | `BUILD_EVIDENCE.json` | ENGINEERING (defined in `FORMALIZATION_STATUS.json`) |

## Standard references used for the mappings

* Kac–Rice formula and Gaussian critical points: Adler & Taylor, *Random Fields and Geometry* (2007), Ch. 11–12.
* Elder rule / persistence barcodes: Edelsbrunner & Harer, *Computational Topology* (2010), Ch. VII.
* Gaussian conditioning / Schur complement: any multivariate-normal reference (e.g. Anderson, *Introduction to Multivariate Statistical Analysis*, §2.5).
* Gamma function remainder (Stirling): NIST DLMF §5.11 (cited in PROOF.md).

## Unmapped terms — action

`RN`, `24-jet`, `JETMOD` are label families. Before any Lean statement mentions them,
the responsible author adds a row per concrete object (statement, domain, normalisation)
to this table. Until then they stay `UNMAPPED` and cannot appear in
`FORMALIZATION_STATUS.json`.
