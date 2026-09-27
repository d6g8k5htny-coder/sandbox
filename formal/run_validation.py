"""Replay the Layer 1 gate controls in both Python modes and write REPORT.json.

Mirrors the Math- package convention (normal + optimized unittest runs, distinct
test and semantic-mutant counts, explicit non-acceptance flags).  Optionally
regenerates and compares BUILD_EVIDENCE.json when a Lean toolchain is present.

    python -B -S formal/run_validation.py --output /tmp/formal-gate-run [--with-lean]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EXPECTED_TESTS = 27
EXPECTED_MUTANTS = 33


def _count_mutants() -> int:
    text = (ROOT / 'test_formal_gate.py').read_text(encoding='utf-8')
    block = text[text.index('MUTANTS = ['):text.index(']', text.index('MUTANTS = ['))]
    return len(re.findall(r'_m_\w+', block))


def _run_tests(flags: list[str], log: Path) -> int:
    proc = subprocess.run([sys.executable, *flags, '-B', '-S', '-m', 'unittest', 'discover',
                           '-s', str(ROOT), '-p', 'test_*.py', '-v'],
                          capture_output=True, text=True, timeout=900)
    log.write_text(proc.stdout + proc.stderr, encoding='utf-8')
    match = re.search(r'^Ran (\d+) tests', proc.stderr, re.MULTILINE)
    if proc.returncode != 0 or not match:
        raise RuntimeError('unittest failed in mode ' + ' '.join(flags or ['normal']))
    return int(match.group(1))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--with-lean', action='store_true', help='also rebuild and compare BUILD_EVIDENCE.json')
    args = parser.parse_args(argv)
    out = args.output.resolve()
    if out.exists() and any(out.iterdir()):
        raise SystemExit('choose a new, empty output directory outside the source tree')
    if ROOT in out.parents or out == ROOT:
        raise SystemExit('output directory must be outside formal/')
    out.mkdir(parents=True, exist_ok=True)

    counts = {'normal': _run_tests([], out / 'unittest_normal.log'),
              'optimized': _run_tests(['-O'], out / 'unittest_optimized.log')}
    mutants = _count_mutants()

    gate = subprocess.run([sys.executable, '-B', '-S', str(ROOT / 'formal_gate.py'), '--json'],
                          capture_output=True, text=True, timeout=300)
    (out / 'gate_stdout.txt').write_text(gate.stdout + gate.stderr, encoding='utf-8')
    gate_report = json.loads(gate.stdout[:gate.stdout.rindex('}') + 1]) if gate.returncode == 0 else None
    blueprint = subprocess.run([sys.executable, '-B', '-S', str(ROOT / 'blueprint_check.py')],
                               capture_output=True, text=True, timeout=300)
    (out / 'blueprint_stdout.txt').write_text(blueprint.stdout + blueprint.stderr, encoding='utf-8')

    lean = None
    if args.with_lean:
        proc = subprocess.run([sys.executable, '-B', '-S', str(ROOT / 'lean_build_evidence.py'), '--check'],
                              capture_output=True, text=True, timeout=7200)
        (out / 'lean_evidence_check.log').write_text(proc.stdout + proc.stderr, encoding='utf-8')
        lean = {'evidence_matches_committed': proc.returncode == 0}

    files = {p.name: {'bytes': p.stat().st_size, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
             for p in sorted(ROOT.iterdir()) if p.is_file()}
    passed = (counts['normal'] == counts['optimized'] == EXPECTED_TESTS and mutants == EXPECTED_MUTANTS
              and gate.returncode == 0 and gate_report is not None and gate_report['passed']
              and blueprint.returncode == 0
              and (lean is None or lean['evidence_matches_committed']))
    report = {
        'object': 'FORMAL-LAYER-VALIDATION-v1',
        'passed': passed,
        'distinct_tests': counts['normal'],
        'distinct_semantic_mutants': mutants,
        'modes': ['normal', 'optimized'],
        'gate_exit_code': gate.returncode,
        'blueprint_exit_code': blueprint.returncode,
        'lean': lean,
        'python': sys.version,
        'files': files,
        'mathematical_acceptance': False,
        'lemma_closed': False,
        'scientific_effect': 'NONE',
        'meaning': 'software-behavior replay of the formalization gate; not theorem acceptance or nonauthor review',
    }
    (out / 'REPORT.json').write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(json.dumps({k: report[k] for k in ('passed', 'distinct_tests', 'distinct_semantic_mutants', 'scientific_effect')}))
    return 0 if passed else 1


if __name__ == '__main__':
    sys.exit(main())
