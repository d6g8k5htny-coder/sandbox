# PR98 F2 source-coverage amend — ABSORBED / do not re-apply

**Scientific effect: NONE.**

## Status

**ABSORBED** on main `#98` head `47ad537d0858`
(`fix(#90): F2 fail-closed unresolved controlling sources + migrate tip bindings`).

Sandbox `pr98_f2_source_coverage_amend.patch` was drafted in parallel against
`6e3f774` (external_frozen HOLD migration) and is **superseded**. Peer landed
first with in-repo `drive/mirrors/…` bindings + fail-closed adapter — prefer
that tip; do not re-apply this patch.

## OA contract covered on tip

- Controlling unresolved/missing/external/cross-repo → refuse (`transition_ok`)
- `source_bindings.repo` validated against checkout
- Q0-C101 + D1-v2.2(1) migrated to structured monitorable bindings
- CLI negative controls added

Watch CI on `47ad537`. #90 stays OPEN / DRAFT pending re-review.
