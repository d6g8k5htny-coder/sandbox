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

Open [main #101](https://github.com/d6g8k5htny-coder/main/pull/101) also edits
`docs/math_status/README.md` (CERTIFIED q=2 REQUIRED CARRIER ABSENT bullet near
line 66). This follow-up edits a later Navigation-only block (~line 114). The
hunks are disjoint: either order applies cleanly on tip `eeebb28` (#99/#100
merged). Prefer land #101 then this follow-up, or combine both before push.
Do not overwrite the whole README from one PR onto the other.

Also apply `pr_handoff_applied.patch` (see `HANDOFF_APPLIED_APPLY.md`) so the
eligibility handoff page no longer claims the Math- tip hole is still open.
