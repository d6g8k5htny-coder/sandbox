import Mathlib.Analysis.Complex.Exponential
import Mathlib.Tactic

/-!
# SIDE24 image ledger — exact arithmetic (Math- `coefficients/side24_v1/PROOF.md`, §2–§4)

Formal object: `SIDE24-COEFFICIENT-D23-20260924-v1`, components `side24.ledger.*`.

Every statement in this file is a closed arithmetic fact that the informal proof
uses as an input.  They mirror `image_ledger()` in `coefficient.py`, which checks the
same facts with Python `Fraction` arithmetic.  Here the Lean kernel checks them.

Scientific effect: NONE.  Nothing here evaluates the parent coefficient or accepts
the parent theorem (main #63); the file proves only the finite arithmetic it states.
-/

namespace Side24

open Finset

/-- PROOF.md eq. (2): the image constant `1458·(76·24⁶ + 15)`. -/
theorem image_constant_eq : (1458 : ℕ) * (76 * 24 ^ 6 + 15) = 21175738586478 := by
  norm_num

/-- PROOF.md §2: the positive Taylor partial sum of `exp` through degree 20 at
`288/125` exceeds `10`.  Rational arithmetic only. -/
theorem exp_partial_sum_gt_ten :
    (10 : ℝ) < ∑ i ∈ range 21, ((288 : ℝ) / 125) ^ i / (Nat.factorial i : ℝ) := by
  simp only [sum_range_succ, sum_range_zero]
  norm_num [Nat.factorial]

/-- PROOF.md §2: `e^(288/125) > 10`.  Uses Mathlib's `Real.sum_le_exp_of_nonneg`
(the partial sums of the exponential series are lower bounds for `exp` at `x ≥ 0`). -/
theorem ten_lt_exp_288_div_125 : (10 : ℝ) < Real.exp (288 / 125) :=
  lt_of_lt_of_le exp_partial_sum_gt_ten (Real.sum_le_exp_of_nonneg (by norm_num) 21)

/-- PROOF.md §2: `e^288 > 10^125`. -/
theorem ten_pow_125_lt_exp_288 : (10 : ℝ) ^ 125 < Real.exp 288 := by
  have h : Real.exp 288 = Real.exp (288 / 125) ^ 125 := by
    rw [← Real.exp_nat_mul]; norm_num
  rw [h]
  exact pow_lt_pow_left₀ ten_lt_exp_288_div_125 (by norm_num) (by norm_num)

/-- PROOF.md §2: `e^(-288) < 10^(-125)`, written with a positive reciprocal. -/
theorem exp_neg_288_lt : Real.exp (-288) < 1 / (10 : ℝ) ^ 125 := by
  rw [Real.exp_neg, one_div]
  exact inv_strictAnti₀ (by positivity) ten_pow_125_lt_exp_288

/-- PROOF.md §2: successive image terms have ratio at most `512·e^(-864) < 1/2`. -/
theorem geometric_ratio_lt_half : (512 : ℝ) * Real.exp (-864) < 1 / 2 := by
  have h3 : Real.exp 864 = Real.exp 288 ^ 3 := by
    rw [← Real.exp_nat_mul]; norm_num
  have hgt : ((10 : ℝ) ^ 125) ^ 3 < Real.exp 864 := by
    rw [h3]
    exact pow_lt_pow_left₀ ten_pow_125_lt_exp_288 (by positivity) (by norm_num)
  rw [Real.exp_neg, mul_inv_lt_iff₀ (Real.exp_pos 864)]
  calc (512 : ℝ) < 1 / 2 * ((10 : ℝ) ^ 125) ^ 3 := by norm_num
    _ < 1 / 2 * Real.exp 864 := by gcongr

/-- PROOF.md eq. (2)→(3): `60·E < ε` with `E = 21175738586478·10^(-125)` and `ε = 10^(-108)`. -/
theorem covariance_relative_lt_eps :
    (60 : ℚ) * (21175738586478 / 10 ^ 125) < 1 / 10 ^ 108 := by
  norm_num

/-- PROOF.md eq. (4): `32·ε < 10^(-106)`, the reported relative periodization bound. -/
theorem density_comparison_lt_reported : (32 : ℚ) / 10 ^ 108 < 1 / 10 ^ 106 := by
  norm_num

/-- Transverse dimension `m = d − 1`. -/
def m (d : ℕ) : ℕ := d - 1

/-- Number of independent symmetric-matrix coordinates `n = m(m+1)/2`. -/
def n (d : ℕ) : ℕ := m d * (m d + 1) / 2

/-- PROOF.md §4 exponent `a = m + 2/3 + n/2`. -/
def a (d : ℕ) : ℚ := m d + 2 / 3 + n d / 2

/-- PROOF.md §4 exponent `b = d + n/2`. -/
def b (d : ℕ) : ℚ := d + n d / 2

/-- PROOF.md §4: for `d = 2`, `a + 2b < 14` and `2a + b < 13`. -/
theorem exponent_budget_d2 : a 2 + 2 * b 2 < 14 ∧ 2 * a 2 + b 2 < 13 := by
  norm_num [a, b, m, n]

/-- PROOF.md §4: for `d = 3`, `a + 2b < 14` and `2a + b < 13`. -/
theorem exponent_budget_d3 : a 3 + 2 * b 3 < 14 ∧ 2 * a 3 + b 3 < 13 := by
  norm_num [a, b, m, n]

/-- PROOF.md §4, statement only (status `specified`): for `0 < ε < 1/28` the density
ratio lies between `1 − 32ε` and `1 + 32ε`.  Not proved in this pilot. -/
def ratio_bound_statement : Prop :=
  ∀ d ∈ ({2, 3} : Finset ℕ), ∀ ε : ℝ, 0 < ε → ε < 1 / 28 →
    (1 + ε) ^ (a d : ℝ) / (1 - ε) ^ (b d : ℝ) < 1 + 32 * ε ∧
    1 - 32 * ε < (1 - ε) ^ (a d : ℝ) / (1 + ε) ^ (b d : ℝ)

end Side24
