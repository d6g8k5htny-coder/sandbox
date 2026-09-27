# Agent entry — `sandbox`

Private exploratory workspace. Eng-only pointers; **no** research-status flips.

## Always

- Keep this repo **private**. Do not publish sandbox paths/hashes/outputs.
- Prefer [`trial`](https://github.com/d6g8k5htny-coder/trial) for portable engineering and [`main`](https://github.com/d6g8k5htny-coder/main) (hardening) for research.
- Scientific effect: **NONE**. `lemma_closed` stays false.

## Never

- Copy sandbox material into public `google-drive`, `meta-framework`, or `query-`.
- Treat a green local probe as theorem discharge or claim closure.
- Ask Dylan for re-approval of work already covered by owner autonomy.

## Layer 1 — formal verification (Lean 4 + Mathlib)

Owner instruction 2026-09-27 (pre-approved, no re-approval): extend the verification stack
with a formal lane. It lives in [`formal/`](formal/README.md) until ported to Math-
([`handoff/`](handoff/README.md) has per-repository patches and the hard-gate extension spec).

- Ladders: `formalization_status ∈ none < specified < proved < kernel-checked`,
  `formalization_review ∈ none | author-side | nonauthor-aligned`. Declared ≤ verifiable, enforced by `formal_gate.py`.
- Every formal token is **non-discharge** except `KERNEL_CHECKED_NONAUTHOR_ALIGNED`, which satisfies the formal lane only.
- Any `.lean` edit regenerates `SOURCE_FILES.json` + `BUILD_EVIDENCE.json` and updates `lean_statement`/blueprint/glossary in the same commit. No `sorry`; parents parametrized or registered `axiom`s with scope notes.
- Kernel acceptance ≠ statement alignment ≠ analytic acceptance. `lemma_closed` stays false.

## Start here

1. This [README](README.md)
2. [`governance-` working contract](https://github.com/d6g8k5htny-coder/governance-)
3. [`trial` multi-agent access](https://github.com/d6g8k5htny-coder/trial/blob/main/docs/MULTI_AGENT_ACCESS.md) — add **sandbox** to every App install; Cloud Agent env deps / `repositoryDependencies` are declared on trial only
4. [`formal/README.md`](formal/README.md) then [`handoff/README.md`](handoff/README.md) — the formal lane and what each repository does next
