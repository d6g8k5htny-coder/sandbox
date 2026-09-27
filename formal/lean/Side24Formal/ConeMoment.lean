import Mathlib.Analysis.SpecialFunctions.Integrals.Basic
import Mathlib.MeasureTheory.Integral.IntervalIntegral.FundThmCalculus
import Mathlib.Analysis.Real.Sqrt
import Mathlib.Probability.Distributions.Gaussian.Real
import Mathlib.Probability.Moments.MGFAnalytic
import Mathlib.Analysis.SpecialFunctions.Gaussian.GaussianIntegral
import Mathlib.Tactic

/-!
# SIDE24 cone moment `D₂ = 29/6 − √6` (Math- `coefficients/side24_v1/PROOF.md`, §1)

Formal object: `SIDE24-COEFFICIENT-D23-20260924-v1`, components `side24.cone.*`.

The informal §1 computes the transverse cone moment `D₂ = E[det(A)² 1{A<0}]` for the
`m = 2` reference law through (i) an elementary integral, (ii) two Gaussian moments
of the shared shift `s ~ N(0, 5/3)`, and (iii) algebra.  All three are kernel-checked
here; (ii) is stated against Mathlib's `ProbabilityTheory.gaussianReal` (whose second
argument is the *variance*).  What is **not** formalised is the probabilistic reduction
from the conditional Hessian law to these scalar integrals (PROOF.md §1 prose).

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

/-- Derivative of `p(t)·exp(v t²/2)` for a differentiable `p` (MGF bookkeeping). -/
theorem hasDerivAt_poly_mul_gauss {v : ℝ} {p : ℝ → ℝ} {p' t : ℝ} (hp : HasDerivAt p p' t) :
    HasDerivAt (fun t => p t * Real.exp (v * t ^ 2 / 2))
      ((p' + p t * (v * t)) * Real.exp (v * t ^ 2 / 2)) t := by
  have hq : HasDerivAt (fun t : ℝ => v * t ^ 2 / 2) (v * t) t := by
    have := (((hasDerivAt_id' t).pow 2).const_mul v).div_const 2
    convert this using 1
    simp; ring
  have := hp.mul hq.exp
  convert this using 1
  ring

/-- Fourth derivative at `0` of the centred Gaussian MGF `t ↦ exp(v t²/2)` is `3v²`. -/
theorem iteratedDeriv_gauss_four (v : ℝ) :
    iteratedDeriv 4 (fun t : ℝ => Real.exp (v * t ^ 2 / 2)) 0 = 3 * v ^ 2 := by
  have d1 : deriv (fun t : ℝ => Real.exp (v * t ^ 2 / 2))
      = fun t => (v * t) * Real.exp (v * t ^ 2 / 2) := by
    funext t
    have := hasDerivAt_poly_mul_gauss (v := v) (hasDerivAt_const t (1 : ℝ))
    simpa using this.deriv
  have d2 : deriv (fun t : ℝ => (v * t) * Real.exp (v * t ^ 2 / 2))
      = fun t => (v + v ^ 2 * t ^ 2) * Real.exp (v * t ^ 2 / 2) := by
    funext t
    have hp : HasDerivAt (fun t : ℝ => v * t) v t := by simpa using (hasDerivAt_id' t).const_mul v
    have := (hasDerivAt_poly_mul_gauss (v := v) hp).deriv
    rw [this]; ring
  have d3 : deriv (fun t : ℝ => (v + v ^ 2 * t ^ 2) * Real.exp (v * t ^ 2 / 2))
      = fun t => (3 * v ^ 2 * t + v ^ 3 * t ^ 3) * Real.exp (v * t ^ 2 / 2) := by
    funext t
    have hp : HasDerivAt (fun t : ℝ => v + v ^ 2 * t ^ 2) (v ^ 2 * (2 * t)) t := by
      have := (((hasDerivAt_id' t).pow 2).const_mul (v ^ 2)).const_add v
      convert this using 1; simp
    have := (hasDerivAt_poly_mul_gauss (v := v) hp).deriv
    rw [this]; ring
  have d4 : deriv (fun t : ℝ => (3 * v ^ 2 * t + v ^ 3 * t ^ 3) * Real.exp (v * t ^ 2 / 2))
      = fun t => (3 * v ^ 2 + 6 * v ^ 3 * t ^ 2 + v ^ 4 * t ^ 4) * Real.exp (v * t ^ 2 / 2) := by
    funext t
    have hp : HasDerivAt (fun t : ℝ => 3 * v ^ 2 * t + v ^ 3 * t ^ 3)
        (3 * v ^ 2 + v ^ 3 * (3 * t ^ 2)) t := by
      have h1 : HasDerivAt (fun t : ℝ => 3 * v ^ 2 * t) (3 * v ^ 2) t := by
        simpa using (hasDerivAt_id' t).const_mul (3 * v ^ 2)
      have h2 : HasDerivAt (fun t : ℝ => v ^ 3 * t ^ 3) (v ^ 3 * (3 * t ^ 2)) t := by
        have := ((hasDerivAt_id' t).pow 3).const_mul (v ^ 3)
        convert this using 1; simp
      exact h1.add h2
    have := (hasDerivAt_poly_mul_gauss (v := v) hp).deriv
    rw [this]; ring
  rw [show (4 : ℕ) = 0 + 1 + 1 + 1 + 1 from rfl, iteratedDeriv_succ, iteratedDeriv_succ,
    iteratedDeriv_succ, iteratedDeriv_succ, iteratedDeriv_zero, d1, d2, d3, d4]
  simp

/-- PROOF.md §1: `E s⁴ = 25/3` for `s ~ N(0, 5/3)` (fourth moment `3·Var(s)²`),
via the moment-generating function `mgf_id_gaussianReal`. -/
theorem gaussian_fourth_moment :
    (∫ s, s ^ 4 ∂(gaussianReal 0 (5 / 3 : NNReal))) = 25 / 3 := by
  have h := iteratedDeriv_mgf_zero (X := id) (μ := gaussianReal 0 (5 / 3 : NNReal)) (by simp) 4
  rw [mgf_id_gaussianReal] at h
  simp only [zero_mul, zero_add] at h
  rw [iteratedDeriv_gauss_four ((5 / 3 : NNReal) : ℝ)] at h
  have : (∫ s, s ^ 4 ∂(gaussianReal 0 (5 / 3 : NNReal))) = (gaussianReal 0 (5 / 3 : NNReal))[id ^ 4] := by
    congr 1
  rw [this, ← h]
  norm_num

/-- PROOF.md §1: `E exp(−s²/2) = √(3/8)` for `s ~ N(0, 5/3)`, via the Gaussian integral
`∫ exp(−b x²) = √(π/b)`. -/
theorem gaussian_exp_moment :
    (∫ s, Real.exp (-s ^ 2 / 2) ∂(gaussianReal 0 (5 / 3 : NNReal))) = Real.sqrt (3 / 8) := by
  rw [integral_gaussianReal_eq_integral_smul (by norm_num)]
  simp only [gaussianPDFReal, smul_eq_mul, sub_zero]
  have hcoe : ((5 / 3 : NNReal) : ℝ) = 5 / 3 := by norm_num
  rw [hcoe]
  have hpt : ∀ x : ℝ, (√(2 * Real.pi * (5 / 3)))⁻¹ * Real.exp (-x ^ 2 / (2 * (5 / 3)))
      * Real.exp (-x ^ 2 / 2) = (√(2 * Real.pi * (5 / 3)))⁻¹ * Real.exp (-(4 / 5) * x ^ 2) := by
    intro x
    rw [mul_assoc, ← Real.exp_add]
    congr 2
    ring
  simp_rw [hpt]
  rw [integral_const_mul, integral_gaussian]
  rw [← Real.sqrt_inv, ← Real.sqrt_mul (by positivity)]
  congr 1
  field_simp
  ring

end Side24
