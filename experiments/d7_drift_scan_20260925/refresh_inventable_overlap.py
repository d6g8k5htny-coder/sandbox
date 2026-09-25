#!/usr/bin/env python3
"""Refresh D7 inventable-overlap snapshot. Scientific effect NONE."""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

OUT = Path(__file__).resolve().parent / "INVENTABLE_OVERLAP.json"

WATCH = [98, 101, 102, 104, 105, 106, 107, 108]


def gh_json(args: list[str]):
    cp = subprocess.run(["gh", *args], capture_output=True, text=True)
    if cp.returncode != 0:
        return {"error": cp.stderr.strip()[:400]}
    return json.loads(cp.stdout)


def worst_check(rollup):
    rank = {
        "FAILURE": 5,
        "CANCELLED": 4,
        "TIMED_OUT": 4,
        "ACTION_REQUIRED": 4,
        "NEUTRAL": 3,
        "SUCCESS": 1,
        "": 0,
        None: 0,
    }
    out = {}
    for c in rollup or []:
        name = c.get("name") or "?"
        label = c.get("conclusion") or c.get("status") or ""
        prev = out.get(name)
        if prev is None or rank.get(label, 0) >= rank.get(prev, 0):
            out[name] = label
    return out


def main() -> int:
    rows = []
    for n in WATCH:
        data = gh_json(
            [
                "pr",
                "view",
                str(n),
                "-R",
                "d6g8k5htny-coder/main",
                "--json",
                "number,title,state,isDraft,baseRefName,headRefOid,files,statusCheckRollup,updatedAt,url",
            ]
        )
        if "error" in data:
            rows.append({"number": n, **data})
            continue
        rows.append(
            {
                "number": data["number"],
                "title": data.get("title"),
                "state": data.get("state"),
                "draft": data.get("isDraft"),
                "base": data.get("baseRefName"),
                "head": (data.get("headRefOid") or "")[:7],
                "url": data.get("url"),
                "updatedAt": data.get("updatedAt"),
                "files": [f.get("path") for f in (data.get("files") or [])],
                "checks": worst_check(data.get("statusCheckRollup")),
            }
        )
    tip_cp = subprocess.run(
        [
            "gh",
            "api",
            "repos/d6g8k5htny-coder/main/commits/chatgpt/drive-github-hardening-20260919",
            "--jq",
            ".sha",
        ],
        capture_output=True,
        text=True,
    )
    tip_sha = tip_cp.stdout.strip() if tip_cp.returncode == 0 else ""

    payload = {
        "as_of_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "scientific_effect": "NONE",
        "lemma_closed": False,
        "hardening_tip": (tip_sha or "")[:12],
        "note": "Overlap watch for inventable/cursor eng PRs; not acceptance.",
        "sandbox_packages": [
            "pr97_followup_nav_and_handoff.patch",
            "pr97_followup_nav_links.patch",
            "pr_handoff_applied.patch",
            "pr105_consumers_fix.patch (ABSORBED on main#105@54a8c59 — do not reapply)",
        ],
        "absorbed": ["pr105_consumers_fix on main#105@54a8c59"],
        "ready": ["pr97_followup_nav_and_handoff.patch"],
        "prs": rows,
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"wrote {OUT} prs={len(rows)} tip={(tip_sha or '')[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
