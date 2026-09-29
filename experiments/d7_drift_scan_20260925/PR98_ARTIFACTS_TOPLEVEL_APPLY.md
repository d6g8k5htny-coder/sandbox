# PR98 artifacts top-level — ABSORBED / do not re-apply

**Scientific effect: NONE.**

## Status

**ABSORBED** on main `#98` head `776fdb75eb71`
(`fix(#90): drop artifacts from REPOSITORY_TOP_LEVEL after out-of-tree reports`).

Peer fixed the CI failure by writing `event-compare --write-report` to
`/tmp/claims-gate-impact.json` (out of checkout) and removing `artifacts`
from `REPOSITORY_TOP_LEVEL` (restoring the negative control). Also gitignores
`artifacts/`.

Sandbox `pr98_artifacts_toplevel_ignore.patch` (ignore-in-test approach) is
**superseded** — do not re-apply; peer's out-of-tree approach is preferred.

Watch verify CI on `776fdb7`.
