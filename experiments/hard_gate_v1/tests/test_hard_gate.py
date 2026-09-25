#!/usr/bin/env python3
"""Negative controls for sandbox hard_gate prototype. Scientific effect NONE."""
from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable
GATE = ROOT / "hard_gate.py"
FIX = ROOT / "fixtures"


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [PY, str(GATE), *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )


class HardGateTests(unittest.TestCase):
    def test_seed_holds_upstream(self):
        cp = run("check", str(FIX / "d0_d7_seed.json"))
        self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
        self.assertIn("problems=0", cp.stdout)
        self.assertIn("lemma_closed=false", cp.stdout)

    def test_illegal_promotion_fails(self):
        cp = run("check", str(FIX / "illegal_promotion.json"))
        self.assertEqual(cp.returncode, 1)
        self.assertIn("controlling promotion", cp.stdout)

    def test_blocked_absent_forces_hold(self):
        cp = run("check", str(FIX / "blocked_absent_promoted.json"))
        self.assertEqual(cp.returncode, 1)
        self.assertIn("BLOCKED_ABSENT", cp.stdout)
        self.assertIn("forces HOLD", cp.stdout)

    def test_missing_revalidation_fails(self):
        cp = run("check", str(FIX / "missing_revalidation.json"))
        self.assertEqual(cp.returncode, 1)
        self.assertIn("REVALIDATION_REQUIRED", cp.stdout)

    def test_revalidation_ok(self):
        cp = run("check", str(FIX / "revalidation_ok.json"))
        self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)

    def test_reverse_impact_lists_dependents(self):
        cp = run("reverse-impact", str(FIX / "d0_d7_seed.json"), "D1_parent_gaussian_KR")
        self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
        data = json.loads(cp.stdout)
        self.assertIn("D2_lifetime_successor", data["transitive_dependents"])
        self.assertIn("UPSTREAM_NEW_THEOREM", data["transitive_dependents"])
        self.assertIs(data["lemma_closed"], False)



    def test_mutate_lower_fails_closed(self):
        cp = run("mutate-lower", str(FIX / "revalidation_ok.json"), "lower")
        # revalidation_ok already marks upper; use seed instead
        cp = run("mutate-lower", str(FIX / "d0_d7_seed.json"), "D1_parent_gaussian_KR")
        self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
        data = json.loads(cp.stdout)
        self.assertTrue(data["fails_closed"])
        self.assertIn("D2_lifetime_successor", data["transitive_dependents"])

    def test_closure_report_shape(self):
        cp = run("closure-report", str(FIX / "d0_d7_seed.json"))
        self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
        data = json.loads(cp.stdout)
        self.assertEqual(data["schema"], "sandbox.hard-gate-closure/v1")
        self.assertIs(data["lemma_closed"], False)
        self.assertGreaterEqual(data["node_count"], 1)
        self.assertEqual(data["problems"], [])

if __name__ == "__main__":
    raise SystemExit(unittest.main())
