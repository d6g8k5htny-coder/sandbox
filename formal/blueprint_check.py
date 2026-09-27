"""Blueprint ↔ status alignment check (fail-closed; scientific effect NONE).

* every ``\\lean{Name}`` in blueprint/src/content.tex is a component ``lean_decl``;
* ``\\leanok`` appears only in environments whose component is ``kernel-checked``;
* every kernel-checked component carries ``\\leanok`` and every formalized component
  appears at least once;
* blueprint/lean_decls lists exactly the bound names (for ``lake exe checkdecls``).

Standard library only.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import formal_gate as fg  # noqa: E402

ROOT = Path(__file__).resolve().parent
_ENV = re.compile(r'\\begin\{(theorem|lemma|proposition|definition|corollary)\}(.*?)\\end\{\1\}', re.DOTALL)
_LEAN = re.compile(r'\\lean\{([^}]*)\}')


def check(root: Path, *, content: str | None = None, decls_text: str | None = None) -> dict:
    formal = root / 'formal'
    status = fg.load_json_strict((formal / 'FORMALIZATION_STATUS.json').read_text(encoding='utf-8'))
    content = content if content is not None else (formal / 'blueprint' / 'src' / 'content.tex').read_text(encoding='utf-8')
    decls_text = decls_text if decls_text is not None else (formal / 'blueprint' / 'lean_decls').read_text(encoding='utf-8')
    by_decl = {c['lean_decl']: c for o in status['objects'] for c in o['components'] if c['formalization_status'] != 'none'}

    problems: list[str] = []
    seen: dict[str, bool] = {}
    for kind, body in _ENV.findall(content):
        names = _LEAN.findall(body)
        if len(names) != 1:
            problems.append('%s environment must bind exactly one \\lean{} name' % kind)
            continue
        name = names[0].strip()
        leanok = '\\leanok' in body
        comp = by_decl.get(name)
        if comp is None:
            problems.append('\\lean{%s} is not a formalized component' % name)
            continue
        if leanok and comp['formalization_status'] != 'kernel-checked':
            problems.append('\\leanok on %s but status is %s' % (name, comp['formalization_status']))
        if not leanok and comp['formalization_status'] == 'kernel-checked':
            problems.append('kernel-checked %s lacks \\leanok' % name)
        if kind != 'definition' and comp['formalization_status'] != 'kernel-checked' and 'specified' not in body.lower():
            problems.append('%s is not kernel-checked; the blueprint text must say so' % name)
        seen[name] = seen.get(name, False) or leanok
    for name in by_decl:
        if name not in seen:
            problems.append('component %s missing from blueprint' % name)
    listed = [line.strip() for line in decls_text.splitlines() if line.strip()]
    if sorted(listed) != sorted(seen):
        problems.append('blueprint/lean_decls differs from bound \\lean{} names')
    return {'passed': not problems, 'problems': problems, 'bound': sorted(seen), 'scientific_effect': 'NONE'}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--root', type=Path, default=ROOT.parent)
    args = parser.parse_args(argv)
    result = check(args.root.resolve())
    for problem in result['problems']:
        print('FAIL ' + problem)
    print('BLUEPRINT_CHECK %s (%d bound declarations; scientific effect NONE)' % (
        'PASSED' if result['passed'] else 'FAILED', len(result['bound'])))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    sys.exit(main())
