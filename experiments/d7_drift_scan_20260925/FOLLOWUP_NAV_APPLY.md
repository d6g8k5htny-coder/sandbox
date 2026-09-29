# Follow-up after #97 merge — restore #92-only nav links

**Scientific effect: NONE.**

#97 landed the crosswalk pages but not the #92 `RESEARCH_INDEX.md` /
`math_status/README.md` pointers (and left eligibility handoff sounding open).

Apply on hardening tip post-#97:

```bash
git checkout chatgpt/drive-github-hardening-20260919
# preferred single apply (nav links + handoff APPLIED banner):
git apply experiments/d7_drift_scan_20260925/pr97_followup_nav_and_handoff.patch
# or the two patches separately (either order):
# git apply experiments/d7_drift_scan_20260925/pr97_followup_nav_links.patch
# git apply experiments/d7_drift_scan_20260925/pr_handoff_applied.patch
python3 -m unittest tests.test_navigation -q
python3 tools/math_status_check.py   # expect problems=0
```

Also marks Math- eligibility handoff as APPLIED.

## Conflict watch

Open inventable PRs also edit `docs/math_status/README.md`:

- [main #101](https://github.com/d6g8k5htny-coder/main/pull/101) — CERTIFIED q=2
  REQUIRED CARRIER ABSENT bullet (~line 66)
- [main #108](https://github.com/d6g8k5htny-coder/main/pull/108) — tip-observe
  `388a22ca` provenance chain (~line 117)

This follow-up edits a Navigation-only block between those regions. Verified on
tip `eeebb28`: **nav + #101 + #108 compose in any order** (disjoint hunks). Prefer
land observe/#101 first if merging separately; do not overwrite the whole README
from one PR onto another.

`pr97_followup_nav_and_handoff.patch` already includes the handoff APPLIED
banner (`HANDOFF_APPLIED_APPLY.md`).
