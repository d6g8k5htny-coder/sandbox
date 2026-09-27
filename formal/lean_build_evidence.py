"""Produce (or check) BUILD_EVIDENCE.json for the Layer 1 Lean project.

Runs ``lake build`` in the pinned project, then asks Lean for ``#print axioms`` of
every declaration listed in FORMALIZATION_STATUS.json, and records the result
together with the byte identities of the pinned sources.  The record is
deterministic (no timestamps) so CI can regenerate it and ``cmp`` against the
committed copy.

The output is evidence about *these bytes* only.  formal_gate.py refuses to use it
when any pinned source has changed since the build.  Standard library only.

    python -B -S formal/lean_build_evidence.py            # build + write
    python -B -S formal/lean_build_evidence.py --check    # build + compare with committed
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
_AXIOM_LINE = re.compile(r"^'([^']+)' depends on axioms: \[([^\]]*)\]\s*$")
_NO_AXIOM_LINE = re.compile(r"^'([^']+)' does not depend on any axioms\s*$")


def _strict(path: Path):
    def pairs(items):
        out = {}
        for k, v in items:
            if k in out:
                raise ValueError('duplicate JSON key: ' + k)
            out[k] = v
        return out
    return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=pairs)


def _module_name(rel: str) -> str | None:
    if not rel.endswith('.lean'):
        return None
    return rel[:-5].replace('/', '.')


def _run(cmd: list[str], cwd: Path, timeout: int) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    elan_bin = Path.home() / '.elan' / 'bin'
    if elan_bin.is_dir():
        env['PATH'] = str(elan_bin) + os.pathsep + env.get('PATH', '')
    return subprocess.run(cmd, cwd=str(cwd), env=env, capture_output=True, text=True, timeout=timeout)


def collect(root: Path, *, skip_build: bool = False, build_timeout: int = 3600) -> dict:
    formal = root / 'formal'
    status = _strict(formal / 'FORMALIZATION_STATUS.json')
    pins = _strict(formal / 'SOURCE_FILES.json')
    project = root / pins['project_root']
    toolchain = (project / 'lean-toolchain').read_text().strip()
    if toolchain != status['lean']['toolchain']:
        raise ValueError('lean-toolchain differs from FORMALIZATION_STATUS.lean.toolchain')

    sources = {}
    for rel in pins['files']:
        data = (project / rel).read_bytes()
        sources[rel] = {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}

    decls = sorted({c['lean_decl'] for o in status['objects'] for c in o['components']
                    if c['formalization_status'] != 'none'})
    modules = sorted({m for m in (_module_name(r) for r in pins['files']) if m})

    if skip_build:
        build = {'command': 'lake build', 'exit_code': 0, 'note': 'reused existing build artifacts'}
        build_stdout = ''
    else:
        proc = _run(['lake', 'build'], project, build_timeout)
        build = {'command': 'lake build', 'exit_code': proc.returncode}
        build_stdout = proc.stdout + proc.stderr
        if proc.returncode != 0:
            build['tail'] = build_stdout[-4000:]
    sorry_warning = 'declaration uses \'sorry\'' in build_stdout

    declarations: dict[str, dict] = {}
    if build['exit_code'] == 0:
        with tempfile.NamedTemporaryFile('w', suffix='.lean', dir=str(project), delete=False, encoding='utf-8') as handle:
            for module in modules:
                handle.write('import %s\n' % module)
            for decl in decls:
                handle.write('#print axioms %s\n' % decl)
            probe = Path(handle.name)
        try:
            proc = _run(['lake', 'env', 'lean', probe.name], project, 600)
        finally:
            probe.unlink(missing_ok=True)
        if proc.returncode != 0:
            raise RuntimeError('axiom probe failed:\n' + proc.stdout + proc.stderr)
        for line in proc.stdout.splitlines():
            match = _AXIOM_LINE.match(line.strip())
            if match:
                axioms = [a.strip() for a in match.group(2).split(',') if a.strip()]
                declarations[match.group(1)] = {'axioms': sorted(axioms)}
                continue
            match = _NO_AXIOM_LINE.match(line.strip())
            if match:
                declarations[match.group(1)] = {'axioms': []}
        missing = [d for d in decls if d not in declarations]
        if missing:
            raise RuntimeError('no axiom report for: ' + ', '.join(missing))

    version = _run(['lean', '--version'], project, 60).stdout.strip()
    manifest = _strict(project / 'lake-manifest.json')
    mathlib = next((p for p in manifest['packages'] if p['name'] == 'mathlib'), None)
    sorry_free = (not sorry_warning) and all('sorryAx' not in d['axioms'] for d in declarations.values())
    return {
        'schema_version': 1,
        'object': 'FORMAL-LAYER-BUILD-EVIDENCE-v1',
        'toolchain': toolchain,
        'lean_version': version,
        'mathlib_rev': mathlib['rev'] if mathlib else None,
        'build': build,
        'sources': sources,
        'declarations': declarations,
        'sorry_free': sorry_free,
        'meaning': 'kernel acceptance of the encoded statements at these exact bytes; not translation fidelity, not theorem acceptance',
        'scientific_effect': 'NONE',
        'lemma_closed': False,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--root', type=Path, default=ROOT.parent)
    parser.add_argument('--output', type=Path, default=None)
    parser.add_argument('--check', action='store_true', help='compare with the committed evidence instead of writing')
    parser.add_argument('--skip-build', action='store_true')
    args = parser.parse_args(argv)
    root = args.root.resolve()
    evidence = collect(root, skip_build=args.skip_build)
    text = json.dumps(evidence, indent=2, sort_keys=True) + '\n'
    target = args.output or (root / 'formal' / 'BUILD_EVIDENCE.json')
    if args.check:
        committed = target.read_text(encoding='utf-8')
        if committed != text:
            sys.stdout.write(text)
            print('BUILD_EVIDENCE differs from committed record', file=sys.stderr)
            return 1
        print('BUILD_EVIDENCE matches committed record (scientific effect NONE)')
        return 0
    target.write_text(text, encoding='utf-8')
    print('wrote ' + str(target))
    return 0 if evidence['build']['exit_code'] == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
