# Follow-up after #97 merge — restore #92-only nav links

**Scientific effect: NONE.**

#97 landed the crosswalk pages but not the #92 `RESEARCH_INDEX.md` /
`math_status/README.md` pointers (and left eligibility handoff sounding open).

Apply on hardening tip post-#97:

```bash
git checkout chatgpt/drive-github-hardening-20260919
git apply experiments/d7_drift_scan_20260925/pr97_followup_nav_links.patch
# or from this sandbox package path
python3 -m unittest tests.test_navigation -q
python3 tools/math_status_check.py   # expect problems=0
```

Also marks Math- eligibility handoff as APPLIED.
