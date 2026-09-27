# Handoff — Layer 1 formal verification, for every agent on every repository

**Object:** FORMAL-LAYER-HANDOFF-20260927-v1. **Scientific effect: NONE.**

## Owner instruction (verbatim intent)

Dylan Roy, 2026-09-27: incorporate a formal verification layer (Lean 4 + Mathlib) on top
of the existing provenance / scope / hard-gate / museum system, so that
"provenance-bound natural-language proofs" become "provenance-bound formal proofs" that
are also machine-checked; coordinate with all current and future agents on all
repositories. **"I, Dylan Roy, pre-approve any decision, request, or action needed to
achieve this goal."** No agent needs to ask for re-approval of work inside this scope.

## What was built (in `sandbox`, this repository)

[`formal/`](../formal/README.md) — Lean 4 project, status ladder, fail-closed gate,
kernel evidence, blueprint, glossary, alignment-review lane, CI. Pilot object: the SIDE24
coefficient note from Math- (14 kernel-checked components, 7 specified, 0 axioms, 0 sorry).

## Why here and not in Math-

Measured 2026-09-27 from this sandbox-launched Cloud Agent: `git push` to `trial`,
`main`, `Math-` and `governance-` returns `403 Permission denied to cursor[bot]`. This is
the known write-scope behaviour recorded in the governance contract ("Cloud Agent write
scope follows the launch environment"). The work therefore landed where it could and
ships with ready-to-apply artifacts for the other repositories.

## What each repository does next (OFFERED — not activity until an agent claims it)

| Repo | Task | Artifact here |
|---|---|---|
| **Math-** | Port `formal/` + workflow; then extend `hard_gate.py` with the `formalization` node field, the four non-discharge formal tokens and the `required` rule | [`PORT.md`](PORT.md), [`MATH_HARD_GATE_EXTENSION.md`](MATH_HARD_GATE_EXTENSION.md), [`agents/Math-.AGENTS.md.patch`](agents/Math-.AGENTS.md.patch) |
| **main** | Add `formalization` lane to museum/STATUS; open one alignment-review issue per formal object (pilot: SIDE24, linking #63/#65); adopt glossary terminology in new prose | [`agents/main.AGENTS.md.patch`](agents/main.AGENTS.md.patch), `formal/GLOSSARY.md`, `formal/FORMALIZATION_REVIEW_LANE.md` |
| **trial** | Cross-repo eng test: Math- `formal/FORMALIZATION_STATUS.json` `informal_source` pins match live Math- bytes; `BUILD_EVIDENCE.sources == SOURCE_FILES.files` | [`agents/trial.AGENTS.md.patch`](agents/trial.AGENTS.md.patch) |
| **governance-** | Record the process amendment (ladders, tokens, non-discharge rule, same-provider no-credit, measured 403) | [`agents/governance-.AGENTS.md.patch`](agents/governance-.AGENTS.md.patch) |
| **any nonauthor agent (OpenAI, Grok, …)** | First alignment review of the pilot: follow the checklist, write `formal/reviews/<component>.<provider>.json` per component, set `formalization_review` accordingly — in Math- after the port, or as a PR here before it | `formal/FORMALIZATION_REVIEW_LANE.md` |
| **AI-prover cross-check lane** | Attempt the 7 `specified` Props (`ratio_bound_statement`, `gaussian_inputs_statement`, `reference_enclosure_statement`, …) with an independent Lean prover; any kernel-accepted proof is recorded with its own provenance and stays author-side until aligned | `formal/lean/Side24Formal/*.lean` |

Patches were generated against these sibling tips and apply with `git apply`:
trial `abae0b4f931e988f582d629f932bb35623dc3af9`, main `f8591b0e1101d97753677044f04e9d87f2fc719a`,
Math- `3b2ac59f8f02b9573d01087aefff85bbc279a55a`, governance- `ae1b92ef1bb794050e584bec1c6f58f9495a018e`.
If a tip moved, re-append the section by hand — it is self-contained.

## Rules that every agent inherits from this layer

1. **Declared ≤ verifiable.** `formalization_status` may never exceed what
   `formal_gate.py` can verify from pinned bytes and kernel evidence.
2. **Kernel ≠ meaning.** `kernel-checked` says the encoded statement is a theorem. Whether
   the encoding matches the prose is the alignment lane; whether the prose is
   mathematically accepted is the analytic lane. Three lanes, none skippable.
3. **Non-discharge by default.** Every formal token is non-discharge except
   `KERNEL_CHECKED_NONAUTHOR_ALIGNED`, which satisfies the formal lane only.
4. **No hidden assumptions.** Parents are parametrized or registered as `axiom` with a
   scope note; `sorry` is refused; conditional theorems carry `KERNEL_CHECKED_CONDITIONAL`.
5. **Same commit.** Lean edit ⇒ pins + evidence + `lean_statement` + blueprint + glossary
   in the same commit. A stale alignment review fails by hash, never by memory.
6. **Standard terminology.** Map every project term in `formal/GLOSSARY.md` before it
   appears in Lean. `UNMAPPED` terms cannot enter `FORMALIZATION_STATUS.json`.
7. **Same-provider review earns no independence credit** (REVIEW_TOPOLOGY v1.1). The gate
   reports `organizational_independence` as `false` or `ATTESTED_NOT_VALIDATED`, never `true`.
8. **Unchanged:** `lemma_closed=false`, prizes, premises, the #90 rules, sandbox privacy.

## For future agents reading this cold

Start with [`formal/README.md`](../formal/README.md), run the six commands under "Run",
read the pilot's `FORMALIZATION_STATUS.json` to see how a component is declared, then pick
the row above for your repository. Coordination is through existing PRs and the
governance work-lease ledger; this file offers tasks, it does not assign or claim them.
