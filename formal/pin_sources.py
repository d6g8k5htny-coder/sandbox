"""Regenerate SOURCE_FILES.json: byte/sha256 pins for the Layer 1 Lean project.

Deliberate regeneration only.  A pin mismatch in formal_gate.py means the Lean
sources changed without this file being refreshed; refreshing a pin does not move
any formalization status and never touches lemma_closed.  Standard library only.

    python -B -S formal/pin_sources.py            # rewrite formal/SOURCE_FILES.json
    python -B -S formal/pin_sources.py --check    # exit 1 if pins are stale
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = 'formal/lean'
PINNED_TOP_LEVEL = ('lean-toolchain', 'lakefile.toml', 'lake-manifest.json', 'Side24Formal.lean')
MODULE_DIR = 'Side24Formal'


def build_pins(repo_root: Path) -> dict:
    project = repo_root / PROJECT_ROOT
    files = {}
    names = list(PINNED_TOP_LEVEL) + sorted(
        str(p.relative_to(project)) for p in (project / MODULE_DIR).glob('*.lean'))
    for rel in names:
        path = project / rel
        if path.is_symlink() or not path.is_file():
            raise ValueError('pinned source must be a regular file: ' + rel)
        data = path.read_bytes()
        files[rel] = {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}
    return {
        'schema_version': 1,
        'object': 'FORMAL-LAYER-SOURCE-FILES-v1',
        'project_root': PROJECT_ROOT,
        'files': files,
        'meaning': 'byte identities of the Lean project; a match proves identity, not correctness or acceptance',
        'scientific_effect': 'NONE',
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--root', type=Path, default=ROOT.parent)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args(argv)
    text = json.dumps(build_pins(args.root.resolve()), indent=2, sort_keys=True) + '\n'
    target = args.root.resolve() / 'formal' / 'SOURCE_FILES.json'
    if args.check:
        if not target.is_file() or target.read_text(encoding='utf-8') != text:
            print('SOURCE_FILES.json is stale; regenerate deliberately', file=sys.stderr)
            return 1
        print('SOURCE_FILES.json matches the Lean sources')
        return 0
    target.write_text(text, encoding='utf-8')
    print('wrote ' + str(target))
    return 0


if __name__ == '__main__':
    sys.exit(main())
