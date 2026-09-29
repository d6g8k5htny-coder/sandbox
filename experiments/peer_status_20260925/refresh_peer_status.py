#!/usr/bin/env python3
"""Private peer-status snapshot for multi-agent D0/D7 work. Scientific effect NONE."""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

OUT = Path(__file__).resolve().parent / "STATUS.json"

# Fixed coordination surfaces + active D7 inventable / eng blockers.
SURFACES = [
    {"repo": "d6g8k5htny-coder/main", "pr": 87, "role": "chatgpt_d0_crosswalk_in_packet"},
    {"repo": "d6g8k5htny-coder/main", "pr": 92, "role": "cursor_d0_crosswalk_outside_packet"},
    {"repo": "d6g8k5htny-coder/main", "pr": 97, "role": "inventable_d0_crosswalk_duplicate_of_92"},
    {"repo": "d6g8k5htny-coder/main", "pr": 93, "role": "cursor_default_home_nav"},
    {"repo": "d6g8k5htny-coder/main", "pr": 98, "role": "cursor_scientific_state_schema_pilot"},
    {"repo": "d6g8k5htny-coder/main", "pr": 101, "role": "inventable_math_status_q2_carrier_absent"},
    {"repo": "d6g8k5htny-coder/main", "pr": 105, "role": "cursor_contribution_plan_lpw_consumers_block"},
    {"repo": "d6g8k5htny-coder/main", "pr": 104, "role": "cursor_outside_residual_guard_parked"},
    {"repo": "d6g8k5htny-coder/main", "pr": 106, "role": "cursor_retip46_cellcount_parked"},
    {"repo": "d6g8k5htny-coder/main", "pr": 107, "role": "inventable_open_problems_frozen_errata"},
    {"repo": "d6g8k5htny-coder/main", "pr": 108, "role": "inventable_tip_observe"},
    {"repo": "d6g8k5htny-coder/main", "pr": 96, "role": "vault99_census_sole_auditor_observe_only"},
    {"repo": "d6g8k5htny-coder/main", "pr": 103, "role": "vault_audit_v2_observe_only"},
    {"repo": "d6g8k5htny-coder/Math-", "pr": 8, "role": "cursor_hard_gate"},
    {"repo": "d6g8k5htny-coder/Math-", "pr": 10, "role": "chatgpt_eligibility_parallel_already_on_main"},
    {"repo": "d6g8k5htny-coder/Math-", "pr": 7, "role": "chatgpt_mesoscopic_paused"},
    {"repo": "d6g8k5htny-coder/Math-", "pr": 9, "role": "cursor_d5_mesoscopic_chart_j0"},
    {"repo": "d6g8k5htny-coder/Math-", "pr": 12, "role": "cursor_d5_chart_into_hard_gate_graph"},
    {"repo": "d6g8k5htny-coder/sandbox", "pr": 2, "role": "sandbox_handoff_this_run"},
]


def gh_json(args: list[str]):
    cp = subprocess.run(["gh", *args], capture_output=True, text=True)
    if cp.returncode != 0:
        return {"error": cp.stderr.strip()[:400]}
    return json.loads(cp.stdout)


def check_summary(checks: list[dict]) -> dict[str, str]:
    """Collapse rollup to name -> worst conclusion/status."""
    rank = {
        "FAILURE": 5,
        "CANCELLED": 4,
        "TIMED_OUT": 4,
        "ACTION_REQUIRED": 4,
        "NEUTRAL": 3,
        "SKIPPED": 2,
        "SUCCESS": 1,
        "": 0,
        None: 0,
    }
    out: dict[str, str] = {}
    for c in checks:
        name = c.get("name") or "?"
        conclusion = c.get("conclusion") or ""
        status = c.get("status") or ""
        label = conclusion if conclusion else status
        prev = out.get(name)
        if prev is None or rank.get(label, 0) >= rank.get(prev, 0):
            out[name] = label
    return out


def main() -> int:
    rows = []
    for s in SURFACES:
        data = gh_json(
            [
                "pr",
                "view",
                str(s["pr"]),
                "-R",
                s["repo"],
                "--json",
                "title,state,isDraft,url,updatedAt,headRefOid,statusCheckRollup",
            ]
        )
        if "error" in data:
            rows.append({**s, **data})
            continue
        checks = []
        for c in data.get("statusCheckRollup") or []:
            checks.append(
                {
                    "name": c.get("name"),
                    "conclusion": c.get("conclusion"),
                    "status": c.get("status"),
                }
            )
        rows.append(
            {
                **s,
                "title": data.get("title"),
                "state": data.get("state"),
                "isDraft": data.get("isDraft"),
                "url": data.get("url"),
                "updatedAt": data.get("updatedAt"),
                "head": (data.get("headRefOid") or "")[:7],
                "checks": checks,
                "check_summary": check_summary(checks),
            }
        )

    open_main = gh_json(
        [
            "pr",
            "list",
            "-R",
            "d6g8k5htny-coder/main",
            "--state",
            "open",
            "--limit",
            "40",
            "--json",
            "number,title,isDraft,headRefName,updatedAt",
        ]
    )
    open_count = len(open_main) if isinstance(open_main, list) else None

    payload = {
        "as_of_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "scientific_effect": "NONE",
        "lemma_closed": False,
        "authority": "NONE",
        "note": "Private coordination snapshot only; not research acceptance.",
        "main_open_pr_count": open_count,
        "sandbox_packages": {
            "pr105_consumers_fix": "experiments/d7_drift_scan_20260925/pr105_consumers_fix.patch",
            "pr97_followup_nav_and_handoff": "experiments/d7_drift_scan_20260925/pr97_followup_nav_and_handoff.patch",
            "pr97_followup_nav_links": "experiments/d7_drift_scan_20260925/pr97_followup_nav_links.patch",
            "pr_handoff_applied": "experiments/d7_drift_scan_20260925/pr_handoff_applied.patch",
        },
        "surfaces": rows,
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"wrote {OUT} surfaces={len(rows)} main_open={open_count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
