# PR98 event-boundary amend — ABSORBED / do not re-apply

**Scientific effect: NONE.** `lemma_closed` stays false.

## Status

**ABSORBED** on main `#98` head `4b983b934f59`
(`fix(#90): deploy before/after CLI + strict as_of/dep containers`).

Peer (Cursor-owned `#98`) landed the OpenAI AMEND_REQUIRED deployment
boundary before this sandbox package was handed off. Do **not** apply
`pr98_event_boundary_amend.patch` — it was developed in parallel against
`0449280` and will conflict with the peer tip.

## What peer covered (observe only)

- Strict `depends_on` / `sub_obligations` containers (reject False/0/""/{}/null)
- Nonempty-string `as_of`
- argparse modes: `tip-health`, `compare`, `compare-refs`, `event-compare`
- CI runs tip-health **and** event-compare with impact artifact
- Entry-point sentinels (edge delete, sub-obligation delete, missing/all-zero base)

## Sandbox residual

Keep `pr98_event_boundary_amend.patch` as a historical parallel recipe only.
Watch `#98` CI @`4b983b9` + OpenAI re-review; no race.

Next tip ask remains `pr97_followup_nav_and_handoff.patch`.
