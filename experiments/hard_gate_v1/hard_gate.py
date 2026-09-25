#!/usr/bin/env python3
"""Private exploratory hard-gate for main #90 semantics.

Scientific effect: NONE. Implementing or greening this checker does not
promote, discharge, FREEZE, or close any research obligation. lemma_closed
stays false. Not a live register; sandbox prototype only.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

TERMINAL = frozenset({
    "PROVED_REVIEWED",
    "SUPERSEDED_NONBLOCKING",
    "REFUTED",
    "BLOCKED_ABSENT",
})
NONTERMINAL = frozenset({
    "OPEN",
    "HOLD",
    "REVALIDATION_REQUIRED",
    "AUTHOR_SIDE_ONLY",
})
CONTROLLING_ROLES = frozenset({"controlling", "campaign_controlling"})
# A controlling node may sit HOLD/OPEN/REVALIDATION_REQUIRED over unfinished
# deps. Fail closed only when it claims a promoted terminal success.
PROMOTED_CONTROLLING = frozenset({"PROVED_REVIEWED", "SUPERSEDED_NONBLOCKING"})


def load_graph(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema") != "sandbox.hard-gate/v1":
        raise ValueError("schema must be sandbox.hard-gate/v1")
    if data.get("scientific_effect") != "NONE":
        raise ValueError("scientific_effect must be NONE")
    if data.get("lemma_closed") is not False:
        raise ValueError("lemma_closed must be false")
    return data


def index_nodes(graph: dict[str, Any]) -> dict[str, dict[str, Any]]:
    nodes = {}
    for node in graph.get("nodes", []):
        nid = node.get("id")
        if not isinstance(nid, str) or not nid:
            raise ValueError("node id required")
        if nid in nodes:
            raise ValueError(f"duplicate node id {nid}")
        nodes[nid] = node
    return nodes


def dependents(edges: list[dict[str, Any]], changed: str) -> set[str]:
    """Transitive dependents: nodes that depend_on changed (directly or deeper)."""
    children: dict[str, set[str]] = {}
    for edge in edges:
        if edge.get("type") != "depends_on":
            continue
        frm, to = edge.get("from"), edge.get("to")
        if not isinstance(frm, str) or not isinstance(to, str):
            raise ValueError("depends_on edges need from/to strings")
        children.setdefault(to, set()).add(frm)
    out: set[str] = set()
    stack = list(children.get(changed, ()))
    while stack:
        n = stack.pop()
        if n in out:
            continue
        out.add(n)
        stack.extend(children.get(n, ()))
    return out


def check_graph(graph: dict[str, Any]) -> list[str]:
    problems: list[str] = []
    nodes = index_nodes(graph)
    edges = graph.get("edges", [])
    for edge in edges:
        if edge.get("type") != "depends_on":
            problems.append(f"unsupported edge type {edge.get('type')!r}")
            continue
        frm, to = edge.get("from"), edge.get("to")
        if frm not in nodes:
            problems.append(f"edge from unknown node {frm!r}")
        if to not in nodes:
            problems.append(f"edge to unknown node {to!r}")

    # Illegal promotion / BLOCKED_ABSENT force-HOLD.
    for node in nodes.values():
        status = node.get("classification")
        role = node.get("role", "supporting")
        if status not in TERMINAL | NONTERMINAL:
            problems.append(f"{node['id']}: unknown classification {status!r}")
        deps = [
            e["to"]
            for e in edges
            if e.get("type") == "depends_on" and e.get("from") == node["id"]
        ]
        if role not in CONTROLLING_ROLES:
            continue
        for dep in deps:
            dstatus = nodes[dep]["classification"] if dep in nodes else None
            if dstatus == "BLOCKED_ABSENT":
                # Rule 2: BLOCKED_ABSENT dep forces dependent HOLD (or stronger stop).
                if status not in {"HOLD", "BLOCKED_ABSENT", "REFUTED"}:
                    problems.append(
                        f"{node['id']}: required BLOCKED_ABSENT dependency "
                        f"{dep} forces HOLD (found {status})"
                    )
            elif status in PROMOTED_CONTROLLING and dstatus not in TERMINAL:
                problems.append(
                    f"{node['id']}: controlling promotion {status} blocked by "
                    f"nonterminal dependency {dep} ({dstatus})"
                )

    # Reverse-impact bookkeeping: if a node declares source_revision_changed,
    # every transitive dependent must be REVALIDATION_REQUIRED (or terminal refute).
    for node in nodes.values():
        if not node.get("source_revision_changed"):
            continue
        for dep_id in dependents(edges, node["id"]):
            d = nodes[dep_id]
            if d.get("classification") not in {
                "REVALIDATION_REQUIRED",
                "REFUTED",
                "HOLD",
            }:
                problems.append(
                    f"{dep_id}: reverse-impact required after change to "
                    f"{node['id']} (found {d.get('classification')})"
                )
    return problems


def reverse_impact_report(graph: dict[str, Any], changed: str) -> dict[str, Any]:
    nodes = index_nodes(graph)
    if changed not in nodes:
        raise ValueError(f"unknown node {changed}")
    hit = sorted(dependents(graph.get("edges", []), changed))
    return {
        "changed": changed,
        "transitive_dependents": hit,
        "scientific_effect": "NONE",
        "lemma_closed": False,
        "authority": "NONE",
        "note": "Report only; does not rewrite classifications.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_check = sub.add_parser("check", help="fail-closed graph invariant check")
    p_check.add_argument("graph", type=Path)
    p_impact = sub.add_parser("reverse-impact", help="list transitive dependents")
    p_impact.add_argument("graph", type=Path)
    p_impact.add_argument("changed")
    args = parser.parse_args(argv)
    graph = load_graph(args.graph)
    if args.cmd == "check":
        problems = check_graph(graph)
        for problem in problems:
            print(f"PROBLEM {problem}")
        print(
            f"hard_gate: problems={len(problems)} "
            "scientific_effect=NONE lemma_closed=false authority=NONE"
        )
        print(
            "hard_gate: a green checker is not obligation discharge; "
            "not a live research register."
        )
        return 1 if problems else 0
    report = reverse_impact_report(graph, args.changed)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
