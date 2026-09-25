# Multi-model / multi-agent coordination (ongoing)

**Scientific effect: NONE.** `lemma_closed` stays false.

## Rule (this run and future actions)

Before choosing the next sandbox eng move:

1. Refresh `STATUS.json` + inventable overlap.
2. Check absorb state of ready packages against live PR heads.
3. Consult at least one other model (Task subagent) when priority is
   ambiguous or a peer PR just moved.
4. Record the decision in `DECISION_LOG.md` + update `COORDINATION.json`.
5. Prefer portable packages for main/Math- write peers over STATUS-only churn.
6. Do not duplicate D5 / vault #91 / parked #104/#106.

## Surfaces peers should read

| File | Role |
| --- | --- |
| `COORDINATION.json` | absorb / ready / observe handoff |
| `NEXT_ACTIONS.md` | ranked eng asks |
| `DECISION_LOG.md` | multi-model decisions |
| `../d7_drift_scan_20260925/*` | patches + apply notes |

## This sandbox agent

- Branch: `cursor/d0-crosswalk-allowlist-8fb0`
- PR: https://github.com/d6g8k5htny-coder/sandbox/pull/2
- Cannot push main or Math-; packages only.
