# Reciprocal translation review — Math- PR18 / trial PR121

**Lease / claim response:** OA-RECIPROCAL-REVIEW-20260925-D7  
**Scientific effect: NONE.** `lemma_closed` stays false. No theorem acceptance.  
**Read-only:** did not edit Math- PR18, trial PR121, or main #98 author branches.

## Reviewer provenance (no org-independence claim)

| Field | Value |
| --- | --- |
| Agent | [Collaborative work progress](bc-01a0d95c-b9ca-70ce-864d-99d51b2a8fb0) |
| URL | https://cursor.com/agents/bc-01a0d95c-b9ca-70ce-864d-99d51b2a8fb0 |
| Repo / branch | `d6g8k5htny-coder/sandbox` / `cursor/d0-crosswalk-allowlist-8fb0` |
| Model label | Cursor Cloud Agent (`originalModelName: default`) — branding ≠ organizational independence |
| Lease | Bounded translation MATCH/AMEND only for the targets below; no unbounded agent fan-out; no status writes |
| Publish path | Sandbox package (this agent cannot write forge comments on main/Math-/trial). Peers with main write may paste onto main #98. |

## Exact targets

| Surface | Head | Path |
| --- | --- | --- |
| Math- PR18 | `0ae7e8fdf5d359f80cf6a3dcd614120f7aa9a19c` | `frontiers/formal_p15_20260925/` |
| SPEC.json SHA-256 | `45d208d07428ed1b88c0021ca51f246a86e8283a0b90996d009cc21efd124afd` | matches trial README claim |
| Parent PROOF.md | `baca69c394ab42130c61771bee74e808703f1ce7` | blob `582180e41dca0ad815ad0f18574df42040912149`; sha256 `87521901ca8e5405b4d1e47f1deb1cd0326affbd6f5967b53c4178590da993f9`; 11352 B / 153 lines |
| trial PR121 | `391f6a8e421e61d888e7687f6847e62339eef191` | `experiments/p15_assumption_probe_20260925/` (seven-obligation crosswalk table) |

Runtime green / solver counts are **not** re-audited here (already documented by authors). This review is **formula / hypothesis / domain** correspondence only.

## Per-obligation MATCH / AMEND

### 1. `F5_DENOM_POSITIVE` — **MATCH**

- **SPEC:** `a,b>=0`, `a+b>0`, `x>0`, `d=a+b*x` ⇒ `d>0`.
- **Parent (45–53 / F4–F5):** `A0,B0>=0`, sum positive, factor `exp(-t_i)>0` in the good-event probability.
- **Domain:** algebraic `x>0` is a sufficient abstraction of `exp(-t)`; constructing the continuum good-event probability remains imported (disclosed).
- **Note:** unused SPEC variable `c` is harmless noise, not a domain error.

### 2. `F5_CURVATURE_NONPOSITIVE` — **MATCH** (imports disclosed)

- **SPEC:** prior denom hyps + cleared `d^2 * c = -a*b*x` ⇒ `c<=0`.
- **Parent (49–53):** `partial_i^2 F_A = -A0 B0 exp(-t_i)/(A0+B0 exp(-t_i))^2 <= 0`.
- **Correspondence:** cleared polynomial is sign-equivalent to the displayed second derivative **once** `d>0` is established.
- **Nonformalized (must stay imported):** differentiation; identification `c = partial_i^2 F_A`; `x = exp(-t)`.

### 3. `F10_RECURRENCE_IDENTITY` — **MATCH**

- **SPEC:** premise `(1-p)*n = p*m` ⇒ `(1-p)^2*n - p^2*m = p*(1-2*p)*m`.
- **Parent (81–87 / F10):** second equality after adjoining trials; ratio `P(S=a+1)/P(S=a)=p/(1-p)` proves it.
- **Correspondence:** `m↔P(S=a)`, `n↔P(S=a+1)`, mass relation matches the ratio premise.
- **Nonformalized:** construction/normalization of binomial masses; first displayed equality in F10.

### 4. `F10_STRICT_INTERIOR` — **MATCH**

- **SPEC:** `1/2 < p < 1`, `m>0`, `n>=0`, mass relation ⇒ `delta < 0`.
- **Parent:** printed strict `<0` under interior `p>1/2` application (`p_star` interior).
- **Domain:** positive mass + open upper bound are required for strictness; disclosed and consistent with source application.

### 5. `F10_CLOSED_NONPOSITIVE` — **AMEND** (additive clarification; disclosed)

- **SPEC:** closed `p ∈ [1/2,1]`, `m,n>=0`, mass relation ⇒ `delta <= 0`.
- **Parent:** printed form is **strict** `<0`, not the closed non-strict statement.
- **Judgment:** **AMEND** — additive endpoint-safe restatement, not a literal copy of the printed inequality. Acceptable **only** as an explicitly labeled clarification (PR18 README + trial crosswalk already say this). Must not be read as a silent edit to frozen PROOF.md.
- **Supporting negative control:** `M_STRICT_AT_P_ONE` correctly witnesses false strictness at `p=1` with vanishing masses.

### 6. `F11_QUADRATIC_GAP` — **MATCH** (imports disclosed)

- **SPEC:** real `e>2` ⇒ `0 < 3e-2 < e^2`.
- **Parent (89–97):** `e^2 - (3e-2) = (e-1)(e-2) > 0` under `e>2`.
- **Correspondence:** polynomial step matches.
- **Nonformalized:** `e` is Euler’s number; `e>2`; exp/log monotonicity used to finish F11.

### 7. `F3_RATIONAL_MARGINS` — **MATCH**

- **SPEC:**  
  - `87/32 - 31967/11760 = 11/23520 > 0`  
  - `∑_{j=0}^5 (11/6)^j/j! - 197/32 = 26081/933120 > 0`
- **Parent (130–139):** same displayed margins.
- **Independent Fraction check (this review):** both identities hold exactly.
- **Nonformalized:** exponential-series / geometric-tail bounds and the final `rho_star` deduction.

## Mutants / anti-vacuity (spot check, not full replay)

PR18’s six mutants and premise-witness SAT design are **directionally correct** relative to the disclosed scopes (drop `a>=0` / `b>=0`, false strict curvature, reversed F10 sign, strictness at `p=1`, omit mass relation). Full solver replay is out of lease (authors already documented green runtime).

## trial PR121 crosswalk consistency

The seven-row table in trial `experiments/p15_assumption_probe_20260925/README.md` at `391f6a8` is **consistent** with the judgments above: same parent line ranges, same MATCH cores, and the same explicit **AMEND**/additive note on `F10_CLOSED_NONPOSITIVE`. F5/F10 assumption-minimization findings (algebraic redundancy ≠ permission to drop probability-model domain constraints) are compatible with keeping import boundaries intact.

## Overall

| Obligation | Verdict |
| --- | --- |
| F5_DENOM_POSITIVE | MATCH |
| F5_CURVATURE_NONPOSITIVE | MATCH |
| F10_RECURRENCE_IDENTITY | MATCH |
| F10_STRICT_INTERIOR | MATCH |
| F10_CLOSED_NONPOSITIVE | **AMEND** (additive disclosed clarification) |
| F11_QUADRATIC_GAP | MATCH |
| F3_RATIONAL_MARGINS | MATCH |

**Translation review status proposed for peers:** six MATCH + one additive AMEND; **not** parent-theorem acceptance; **not** independent proof-kernel check; PR18 `independent_translation_review` / `parent_acceptance` should remain false until a nonauthor with forge write records disposition on the author surfaces.

## Out of scope (explicit)

- No edit to Math-/trial/main author branches.
- No claim/register/status promotion.
- No re-run of 26/224 solver queries.
- No Lean/Coq/Isabelle checking.
- No organizational independence claimed from Cursor branding alone.
