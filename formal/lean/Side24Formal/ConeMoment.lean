import Mathlib.Analysis.SpecialFunctions.Integrals.Basic
import Mathlib.MeasureTheory.Integral.IntervalIntegral.FundThmCalculus
import Mathlib.Analysis.Real.Sqrt
import Mathlib.Probability.Distributions.Gaussian.Real
import Mathlib.Tactic

/-!
# SIDE24 cone moment `D₂ = 29/6 − √6` (Math- `coefficients/side24_v1/PROOF.md`, §1)

Formal object: `SIDE24-COEFFICIENT-D23-20260924-v1`, components `side24.cone.*`.

The informal §1 computes the transverse cone moment `D₂ = E[det(A)² 1{A<0}]` for the
`m = 2` reference law through (i) an elementary integral, (ii) three Gaussian moments
of the shared shift `s ~ N(0, 5/3)`, and (iii) algebra.  Here (i) and (iii) are
kernel-checked and (ii) is only *specified* as a `Prop` against Mathlib's
`ProbabilityTheory.gaussianReal`.

The private sandbox experiment `experiments/cone_v1/cone_probe.py` samples the same
quantity; that Monte Carlo output is a sanity check, never evidence.  Scientific effect: NONE.
-/

namespace Side24

open MeasureTheory ProbabilityTheory

/-- Antiderivative of `z ↦ (a − z)² e^(−z/2) / 2`. -/
noncomputable def coneAntiderivative (a z : ℝ) : ℝ :=
  -Real.exp (-z / 2) * ((a - z) ^ 2 - 4 * (a - z) + 8)

theorem hasDerivAt_coneAntiderivative (a z : ℝ) :
    HasDerivAt (coneAntiderivative a) ((a - z) ^ 2 * Real.exp (-z / 2) / 2) z := by
  have hlin : HasDerivAt (fun z : ℝ => -z / 2) (-1 / 2) z := by
    simpa using ((hasDerivAt_id z).neg).div_const 2
  have hexp : HasDerivAt (fun z : ℝ => Real.exp (-z / 2)) (Real.exp (-z / 2) * (-1 / 2)) z :=
    hlin.exp
  have hs : HasDerivAt (fun z : ℝ => a - z) (-1) z := by
    simpa using (hasDerivAt_id z).const_sub a
  have hpoly : HasDerivAt (fun z : ℝ => (a - z) ^ 2 - 4 * (a - z) + 8)
      (((2 : ℕ) : ℝ) * (a - z) ^ (2 - 1) * (-1) - 4 * (-1)) z :=
    ((hs.pow 2).sub (hs.const_mul 4)).add_const 8
  have := hexp.neg.mul hpoly
  unfold coneAntiderivative
  convert this using 1
  simp only [Pi.neg_apply]
  push_cast
  ring

/-- PROOF.md §1: `∫₀ᵃ (a − z)² e^(−z/2) dz / 2 = a² − 4a + 8 − 8e^(−a/2)`.
The informal text states this for `a ≥ 0`; the identity holds for every real `a`. -/
theorem cone_integral_identity (a : ℝ) :
    ∫ z in (0 : ℝ)..a, (a - z) ^ 2 * Real.exp (-z / 2) / 2
      = a ^ 2 - 4 * a + 8 - 8 * Real.exp (-a / 2) := by
  rw [intervalIntegral.integral_eq_sub_of_hasDerivAt
      (fun z _ => hasDerivAt_coneAntiderivative a z)]
  · unfold coneAntiderivative
    simp
    ring
  · exact (by fun_prop : Continuous fun z : ℝ => (a - z) ^ 2 * Real.exp (-z / 2) / 2).intervalIntegrable _ _

/-- The `m = 2` cone moment as stated in PROOF.md §1. -/
noncomputable def D2 : ℝ := 29 / 6 - Real.sqrt 6

/-- PROOF.md §1 algebra: `(1/2)[25/3 − 20/3 + 8 − 8√(3/8)] = 29/6 − √6`. -/
theorem D2_algebra :
    (1 / 2 : ℝ) * (25 / 3 - 20 / 3 + 8 - 8 * Real.sqrt (3 / 8)) = D2 := by
  have h : Real.sqrt (3 / 8) = Real.sqrt 6 / 4 := by
    rw [show (3 / 8 : ℝ) = 6 / 4 ^ 2 by norm_num, Real.sqrt_div' _ (by norm_num),
      Real.sqrt_sq (by norm_num)]
  unfold D2
  rw [h]
  ring

/-- Outward rational enclosure of `D₂`. -/
theorem D2_bounds : (2.38384359054 : ℝ) < D2 ∧ D2 < 2.38384359056 := by
  have h1 : Real.sqrt 6 < 2.449489742784 := by
    rw [Real.sqrt_lt' (by norm_num)]; norm_num
  have h2 : (2.449489742783 : ℝ) < Real.sqrt 6 := by
    rw [Real.lt_sqrt (by norm_num)]; norm_num
  unfold D2
  constructor <;> linarith

/-- PROOF.md §1: the truncation `R < |s|` is essential — the untruncated half moment
`29/6` is strictly larger than `D₂`. -/
theorem D2_lt_untruncated : D2 < 29 / 6 := by
  unfold D2
  have : 0 < Real.sqrt 6 := Real.sqrt_pos.mpr (by norm_num)
  linarith

/-- PROOF.md §1 Gaussian inputs, statement only (status `specified`): for
`s ~ N(0, 5/3)`, `E s⁴ = 25/3` and `E e^(−s²/2) = √(3/8)`.  Not proved in this pilot. -/
def gaussian_inputs_statement : Prop :=
  (∫ s, s ^ 4 ∂(gaussianReal 0 (5 / 3 : NNReal))) = 25 / 3 ∧
  (∫ s, Real.exp (-s ^ 2 / 2) ∂(gaussianReal 0 (5 / 3 : NNReal))) = Real.sqrt (3 / 8)

end Side24
