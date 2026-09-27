# sandbox — public exploratory workspace

Public exploratory and adversarial experiments for Dylan Roy’s research
workspace. This repository is a public artifact catalog and **not** a
scientific-status register.

## Boundaries (eng)

| Repository | Responsibility |
|---|---|
| `main` | Research campaign, claims/reviews, integration |
| `Math-` | Mathematical candidates and reproducible calculations |
| `trial` | Engineering / portable Path C; no research-register duplication |
| `governance-` | Cross-repository working contract |
| `sandbox` | experiments only — automatic public export |

Do not copy sandbox files, outputs, paths, or hashes into public catalogs,
public workflow artifacts, or Drive replicas.

## Layer 1 — formal verification (Lean 4 + Mathlib)

[`formal/`](formal/README.md) holds the formal-verification lane: a Lean 4 + Mathlib
project kernel-checking components of the Math- SIDE24 coefficient note, a fail-closed
`formalization_status` gate (`none < specified < proved < kernel-checked`), byte-bound
kernel evidence, a Lean Blueprint, a terminology glossary and an alignment-review lane.
[`handoff/`](handoff/README.md) carries the per-repository patches and the Math- hard-gate
extension spec so every agent on `main`, `Math-`, `trial` and `governance-` can take it up.
Kernel acceptance is not statement alignment and not analytic acceptance.

Scientific effect from this README: **NONE**. Never flip `lemma_closed`, prizes,
or premises. Agent entry: [AGENTS.md](AGENTS.md).
