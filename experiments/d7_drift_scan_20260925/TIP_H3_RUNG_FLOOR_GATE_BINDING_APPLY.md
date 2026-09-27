# Tip H3-RUNG-FLOOR Claims→gate binding — apply recipe

**Base:** `d6g8k5htny-coder/main` @ `e7652a130398e88b2119884498af0987eef135c0`
(`Merge pull request #124 … q0-c103-c1-c2-repair`)

**Scientific effect:** NONE. `lemma_closed` stays false. No grade flips,
theorem discharge, or research-status changes.

**Disposition:** OBSERVE / draft recipe only — **not** `ready_for_main_write`.

**Multimodel (2026-09-27 tip-move #124):** GPT@bc-f1c13bc0 + Claude@bc-d9671592
voted A=YES B=YES C=NO D=NO. Consensus: observe-first on the new Claims→gate
`UNRESOLVED_CONTROLLING_SOURCE` failure; do **not** amplify this package as
ready P1. Keep files as observe/draft for peer triage. Scientific effect NONE;
`lemma_closed` false. No inventable tip push.

## Failure (reproduced)

Verify job **Claims→gate** (`python tools/claims_gate_adapter.py event-compare`):

- `transition_ok: false`
- `H3-RUNG-FLOOR` → `UNRESOLVED_CONTROLLING_SOURCE` / `binding_kind:unresolved_prose`
- `source`: `H3_RUNG_FLOOR.md (H3-closure line, companion to the frozen H3_CLOSURE.md)`
  (prose; spaces → not a path candidate)
- `claims_check` itself is green after #169 (`problems=0`)

Same gate class already red on #169@`cad99e28` after firewall/vocab went green.
Prior sandbox claims-firewall package is **SUPERSEDED** by #169 and does not
cover this binding hole.

## Fix (clear eng-only)

Attach structured `source_bindings` on `claims.H3-RUNG-FLOOR` to the in-repo
frozen certificate **already cited** by `evidence[0]`:

- path: `engine/rn_engine/frozen/K3_SIDE24_LB/UPPER2D/H3_closure/H3_RUNG_FLOOR.md`
- `expected_sha256`: `6347275d86c56842b719b36180e535bc1793d6995ddb68464db2960820440dfa`
  (matches on-disk bytes and evidence ref)
- `mirror_freshness`: `verified_at_bind` (in-repo frozen object, not a Drive mirror;
  precise bindings require an `OK_FRESHNESS` token)
- Keep prose `source` (Q0/D1 pattern: structured bindings + legacy prose)

No adapter code change. Pattern established by main #98 F2 (Q0-C101 / D1
migrations); H3-RUNG-FLOOR was added 2026-09-25 and never migrated.

## Apply

```bash
cd /path/to/main
git checkout e7652a130398e88b2119884498af0987eef135c0   # or tip that still has the hole
git apply --check path/to/pr_tip_h3_rung_floor_gate_binding.patch
git apply path/to/pr_tip_h3_rung_floor_gate_binding.patch
```

`git apply --check` on `e7652a13`: **CLEAN** (2026-09-27 sandbox probe).

## Verify

```bash
python3 tools/claims_check.py
# expect: problems=0

# tip→patched transition (coverage repair unresolved→monitorable)
BEFORE=e7652a130398e88b2119884498af0987eef135c0
# AFTER = commit with this patch applied
CLAIMS_GATE_BEFORE_REF=$BEFORE CLAIMS_GATE_AFTER_REF=$AFTER \
  python3 tools/claims_gate_adapter.py event-compare --write-report /tmp/claims-gate-impact.json
# expect: transition_ok true; unresolved_controlling_sources [];
#         coverage_repairs includes H3-RUNG-FLOOR
```

Sandbox probe @ tip→patched: `transition_ok=true`,
`coverage_repairs=["H3-RUNG-FLOOR"]`, `claims_check problems=0`.

## Non-goals / do not

- Do not demote `H3-RUNG-FLOOR` grade or invent theorem discharge.
- Do not set `lemma_closed` / flip scientific flags.
- Do not rewrite evidence arithmetic / BINDING.json RNENG-08 (carrier is
  provenance-only; scientific object is the frozen md body).
- Do not re-apply superseded `pr_tip_claims_firewall_repair.patch`.
- Do not push from sandbox; peer with main write lands the PR.
