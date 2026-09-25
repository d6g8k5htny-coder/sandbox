#!/usr/bin/env python3
"""Private peer-status snapshot for multi-agent D0/D7 work. Scientific effect NONE."""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

OUT = Path(__file__).resolve().parent / "STATUS.json"

SURFACES = [
    {"repo": "d6g8k5htny-coder/main", "pr": 87, "role": "chatgpt_d0_crosswalk_in_packet"},
    {"repo": "d6g8k5htny-coder/main", "pr": 92, "role": "cursor_d0_crosswalk_outside_packet"},
    {"repo": "d6g8k5htny-coder/main", "pr": 93, "role": "cursor_default_home_nav"},
    {"repo": "d6g8k5htny-coder/Math-", "pr": 8, "role": "cursor_hard_gate"},
    {"repo": "d6g8k5htny-coder/Math-", "pr": 7, "role": "chatgpt_mesoscopic_paused"},
    {"repo": "d6g8k5htny-coder/sandbox", "pr": 2, "role": "sandbox_handoff_this_run"},
    {"repo": "d6g8k5htny-coder/main", "pr": 96, "role": "vault99_census_sole_auditor_observe_only"},
]


def gh_json(args: list[str]):
    cp = subprocess.run(
        ["gh", *args], capture_output=True, text=True
    )
    if cp.returncode != 0:
        return {"error": cp.stderr.strip()[:400]}
    return json.loads(cp.stdout)


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
            }
        )
    payload = {
        "as_of_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "scientific_effect": "NONE",
        "lemma_closed": False,
        "authority": "NONE",
        "note": "Private coordination snapshot only; not research acceptance.",
        "surfaces": rows,
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps({"wrote": str(OUT), "surfaces": len(rows), "lemma_closed": False}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
