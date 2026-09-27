import Mathlib.Analysis.SpecialFunctions.Gamma.Basic
import Mathlib.Analysis.SpecialFunctions.Pow.Real
import Mathlib.Tactic
import Side24Formal.ConeMoment

/-!
# SIDE24 reference coefficient and the enclosure statement
(Math- `coefficients/side24_v1/PROOF.md`, eq. (1), (4) and the displayed theorem)

Formal object: `SIDE24-COEFFICIENT-D23-20260924-v1`, components `side24.reference.*`.

## What is and is not defined here

* `referenceCoefficient d` is eq. (1) in standard objects (`Real.Gamma`, `Real.pi`,
  `Real.sqrt`, real powers).  It is the *nonperiodic reference* expression.
* The periodic coefficient `c_{d,24}` is **not** defined: it is fixed by the parent
  source (main #63, eq. 15.2), which is not formalized.  Every statement about it is
  therefore parametrized by an arbitrary `c : ℕ → ℝ`.  The hypotheses of
  `enclosure_of_reference` are exactly the scope of what is proved.
* `reference_enclosure_statement` records the author's 80-digit outward rational
  enclosure of `referenceCoefficient` (from `coefficient.py`).  It is *specified*, not
  proved: bounding `Γ(7/6)`, `π` and the roots in Lean is future work.
* `periodization_statement c` is eq. (4).  It depends on the parent analysis and is
  *specified*, not proved.

`enclosure_of_reference` is the kernel-checked logical step of PROOF.md §5:
"the periodization allowance in (4) is applied to exact rational endpoints BEFORE the
final outward rounding".  Scientific effect: NONE.
-/

namespace Side24

/-- Cone moments `D_m` for `m = d − 1 ∈ {1, 2}` (PROOF.md §1); `0` outside that range. -/
noncomputable def coneMoment : ℕ → ℝ
  | 1 => 4 / 3
  | 2 => D2
  | _ => 0

/-- PROOF.md eq. (1): `c_{d,ref} = Γ(7/6)·(3/2)^(1/3)·D_{d−1} / (2√3·π^(d−1)·√π)`. -/
noncomputable def referenceCoefficient (d : ℕ) : ℝ :=
  Real.Gamma (7 / 6) * (3 / 2 : ℝ) ^ ((1 : ℝ) / 3) * coneMoment (d - 1)
    / (2 * Real.sqrt 3 * Real.pi ^ (d - 1) * Real.sqrt Real.pi)

/-- Author-side 80-digit outward lower endpoint for `referenceCoefficient 2`. -/
def ref2Lo : ℚ :=
  7340691930603427103013596295776273618445946768885664197004403216711382893223557 / 10 ^ 80

/-- Author-side 80-digit outward upper endpoint for `referenceCoefficient 2`. -/
def ref2Hi : ℚ :=
  7340691930603427103013596295777417013380655703769646772200313740800240533333043 / 10 ^ 80

/-- Author-side 80-digit outward lower endpoint for `referenceCoefficient 3`. -/
def ref3Lo : ℚ :=
  4177593184059834334293666542856911775587214492195145252592066752648167407187767 / 10 ^ 80

/-- Author-side 80-digit outward upper endpoint for `referenceCoefficient 3`. -/
def ref3Hi : ℚ :=
  4177593184059834334293666542857562482486657407720240268849039889886922519700256 / 10 ^ 80

/-- The relative periodization allowance of PROOF.md eq. (4). -/
def periodizationBound : ℚ := 1 / 10 ^ 106

/-- Statement only (status `specified`): the reference coefficient lies in the author's
rational enclosure.  Its informal evidence is `coefficient.py`; not kernel-checked. -/
def reference_enclosure_statement : Prop :=
  (ref2Lo : ℝ) < referenceCoefficient 2 ∧ referenceCoefficient 2 < ref2Hi ∧
  (ref3Lo : ℝ) < referenceCoefficient 3 ∧ referenceCoefficient 3 < ref3Hi

/-- Statement only (status `specified`): PROOF.md eq. (4), `|c_{d,24}/c_{d,ref} − 1| < 10^(−106)`
for `d ∈ {2, 3}`, for the periodic coefficient `c` fixed by the (unformalized) parent. -/
def periodization_statement (c : ℕ → ℝ) : Prop :=
  ∀ d ∈ ({2, 3} : Finset ℕ), |c d / referenceCoefficient d - 1| < (periodizationBound : ℝ)

/-- The displayed theorem of PROOF.md as a statement about an arbitrary `c : ℕ → ℝ`. -/
def enclosure_statement (c : ℕ → ℝ) : Prop :=
  (0.07340691930603427103 : ℝ) < c 2 ∧ c 2 < 0.07340691930603427104 ∧
  (0.04177593184059834334 : ℝ) < c 3 ∧ c 3 < 0.04177593184059834335

/-- Relative-perturbation transfer: if `r ∈ (lo, hi)` with `lo > 0` and `|c/r − 1| < δ`,
then `(1 − δ)·lo < c < (1 + δ)·hi`. -/
theorem perturbed_bounds {c r lo hi δ : ℝ} (hlo : 0 < lo) (h₁ : lo < r) (h₂ : r < hi)
    (hδ : 0 < δ) (hδ1 : δ < 1) (h : |c / r - 1| < δ) :
    (1 - δ) * lo < c ∧ c < (1 + δ) * hi := by
  have hr : 0 < r := hlo.trans h₁
  rw [abs_sub_lt_iff] at h
  obtain ⟨hA, hB⟩ := h
  have hu : c < (1 + δ) * r := by
    have := (div_lt_iff₀ hr).mp (show c / r < 1 + δ by linarith)
    linarith
  have hl : (1 - δ) * r < c := by
    have := (lt_div_iff₀ hr).mp (show 1 - δ < c / r by linarith)
    linarith
  constructor
  · calc (1 - δ) * lo < (1 - δ) * r := by gcongr
      _ < c := hl
  · calc c < (1 + δ) * r := hu
      _ < (1 + δ) * hi := by gcongr

/-- PROOF.md §5, kernel-checked: the author's rational reference enclosure together with
the relative periodization bound (4) implies the displayed 20-digit enclosure.
Both hypotheses are `specified` Props; this theorem discharges neither. -/
theorem enclosure_of_reference (c : ℕ → ℝ)
    (href : reference_enclosure_statement) (hper : periodization_statement c) :
    enclosure_statement c := by
  obtain ⟨lo2, hi2, lo3, hi3⟩ := href
  have h2 := hper 2 (by simp)
  have h3 := hper 3 (by simp)
  have hδ : (0 : ℝ) < (periodizationBound : ℝ) := by norm_num [periodizationBound]
  have hδ1 : (periodizationBound : ℝ) < 1 := by norm_num [periodizationBound]
  obtain ⟨l2, u2⟩ := perturbed_bounds (by norm_num [ref2Lo]) lo2 hi2 hδ hδ1 h2
  obtain ⟨l3, u3⟩ := perturbed_bounds (by norm_num [ref3Lo]) lo3 hi3 hδ hδ1 h3
  have e2l : (0.07340691930603427103 : ℝ) ≤ (1 - (periodizationBound : ℝ)) * (ref2Lo : ℝ) := by
    norm_num [periodizationBound, ref2Lo]
  have e2u : (1 + (periodizationBound : ℝ)) * (ref2Hi : ℝ) ≤ 0.07340691930603427104 := by
    norm_num [periodizationBound, ref2Hi]
  have e3l : (0.04177593184059834334 : ℝ) ≤ (1 - (periodizationBound : ℝ)) * (ref3Lo : ℝ) := by
    norm_num [periodizationBound, ref3Lo]
  have e3u : (1 + (periodizationBound : ℝ)) * (ref3Hi : ℝ) ≤ 0.04177593184059834335 := by
    norm_num [periodizationBound, ref3Hi]
  exact ⟨e2l.trans_lt l2, u2.trans_le e2u, e3l.trans_lt l3, u3.trans_le e3u⟩

end Side24
