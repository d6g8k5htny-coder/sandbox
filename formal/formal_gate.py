"""Layer 1 formal-verification gate (fail-closed; scientific effect NONE).

Reads FORMALIZATION_STATUS.json, the pinned Lean sources, BUILD_EVIDENCE.json
and optional alignment-review records, and checks that every *declared*
formalization status is backed by evidence of at least that level:

    none < specified < proved < kernel-checked

A declared level above the verifiable level fails closed.  The gate never
grants nonauthor review, never edits status files, and never touches
``lemma_closed``.  A green run means: the encoded Lean statements are what the
status file says they are, and the recorded kernel evidence is bound to exactly
these bytes.  It does not mean the informal theorem is accepted; translation
fidelity is a separate review lane (``FORMALIZATION_REVIEW_LANE.md``).

Standard library only.  Run from anywhere:

    python -B -S formal/formal_gate.py [--root REPO_ROOT] [--json]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
STATUS_PATH = ROOT / 'FORMALIZATION_STATUS.json'
SOURCE_FILES_PATH = ROOT / 'SOURCE_FILES.json'
EVIDENCE_PATH = ROOT / 'BUILD_EVIDENCE.json'

STATUS_LADDER = ('none', 'specified', 'proved', 'kernel-checked')
REVIEW_LADDER = ('none', 'author-side', 'nonauthor-aligned')
STANDARD_AXIOMS = frozenset({'propext', 'Classical.choice', 'Quot.sound'})

# Tokens handed to the downstream (Math-) hard gate.  Every token except the
# last is NON-DISCHARGE: it can never by itself justify promotion.
TOKEN_SPECIFIED = 'FORMAL_SPECIFIED'
TOKEN_PROVED_AUTHOR = 'FORMAL_PROVED_AUTHOR_SIDE'
TOKEN_KERNEL_AUTHOR = 'KERNEL_CHECKED_AUTHOR_SIDE'
TOKEN_KERNEL_CONDITIONAL = 'KERNEL_CHECKED_CONDITIONAL'
TOKEN_KERNEL_ALIGNED = 'KERNEL_CHECKED_NONAUTHOR_ALIGNED'
FORMAL_NON_DISCHARGE = (TOKEN_SPECIFIED, TOKEN_PROVED_AUTHOR,
                        TOKEN_KERNEL_AUTHOR, TOKEN_KERNEL_CONDITIONAL)

_DECL_KINDS = ('theorem', 'lemma', 'def', 'abbrev', 'noncomputable def')
_SORRY_RE = re.compile(r'(?<![A-Za-z0-9_.])sorry(?![A-Za-z0-9_])')
_AXIOM_RE = re.compile(r'^\s*axiom\s+([A-Za-z_][\w.\']*)', re.MULTILINE)
_NAMESPACE_RE = re.compile(r'^\s*namespace\s+([A-Za-z_][\w.]*)', re.MULTILINE)


class GateError(ValueError):
    """Any fail-closed refusal."""


# ---------------------------------------------------------------- utilities

def load_json_strict(text: str) -> Any:
    def pairs(items):
        out = {}
        for key, value in items:
            if key in out:
                raise GateError('duplicate JSON key: ' + key)
            out[key] = value
        return out

    def constant(value):
        raise GateError('non-finite JSON constant: ' + value)

    try:
        return json.loads(text, object_pairs_hook=pairs, parse_constant=constant)
    except json.JSONDecodeError as exc:
        raise GateError('malformed JSON: ' + str(exc)) from exc


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _norm_ws(text: str) -> str:
    return ' '.join(text.split())


def _require(cond: bool, message: str) -> None:
    if not cond:
        raise GateError(message)


def _exact_bool(value: Any) -> bool:
    return type(value) is bool


def _level(status: str) -> int:
    _require(status in STATUS_LADDER, 'unknown formalization_status: ' + repr(status))
    return STATUS_LADDER.index(status)


# ------------------------------------------------------------- Lean sources

def scan_lean_module(text: str) -> dict[str, Any]:
    """Text-level facts about one Lean module.  Not a parser; fail-closed hints."""
    stripped = _strip_comments(text)
    decls: dict[str, dict[str, Any]] = {}
    namespace = _NAMESPACE_RE.findall(stripped)
    prefix = (namespace[0] + '.') if namespace else ''
    if len(set(namespace)) > 1:
        raise GateError('gate supports a single namespace per module')
    decl_re = re.compile(
        r'^\s*(?:@\[[^\]]*\]\s*)?(?:private\s+|protected\s+)?'
        r'(noncomputable\s+def|theorem|lemma|def|abbrev)\s+([A-Za-z_][\w\']*)',
        re.MULTILINE)
    for kind, name in decl_re.findall(stripped):
        full = prefix + name
        if full in decls:
            raise GateError('duplicate declaration in module: ' + full)
        decls[full] = {'kind': kind, 'short': name}
    return {
        'declarations': decls,
        'sorry': bool(_SORRY_RE.search(stripped)),
        'axioms': [prefix + a if '.' not in a else a for a in _AXIOM_RE.findall(stripped)],
        'namespace': namespace[0] if namespace else '',
    }


def _strip_comments(text: str) -> str:
    text = re.sub(r'/-.*?-/', ' ', text, flags=re.DOTALL)
    return re.sub(r'--[^\n]*', ' ', text)


def statement_present(module_text: str, statement: str) -> bool:
    """Blueprint-lite alignment: the reviewed statement bytes must appear verbatim
    (modulo whitespace runs) in the module.  Any drift stales the review."""
    _require(isinstance(statement, str) and statement.strip(), 'empty lean_statement')
    return _norm_ws(statement) in _norm_ws(_strip_comments(module_text))


# ---------------------------------------------------------------- pin checks

def verify_source_pins(root: Path, pins: dict[str, Any]) -> dict[str, dict[str, Any]]:
    _require(isinstance(pins, dict) and pins.get('schema_version') == 1, 'unsupported SOURCE_FILES schema')
    files = pins.get('files')
    _require(isinstance(files, dict) and files, 'SOURCE_FILES.files must be a nonempty object')
    project = root / pins['project_root']
    out = {}
    for rel, identity in files.items():
        path = project / rel
        _require(not path.is_symlink() and path.is_file(), 'pinned source missing or not regular: ' + rel)
        _require('..' not in Path(rel).parts, 'pinned source escapes project root: ' + rel)
        data = path.read_bytes()
        _require(type(identity.get('bytes')) is int and identity['bytes'] == len(data),
                 'source byte-length mismatch: ' + rel)
        _require(identity.get('sha256') == sha256_bytes(data), 'source sha256 mismatch: ' + rel)
        out[rel] = {'bytes': len(data), 'sha256': identity['sha256'], 'text': data.decode('utf-8')}
    return out


def verify_build_evidence(evidence: Any, sources: dict[str, dict[str, Any]], lean_cfg: dict[str, Any]) -> dict[str, Any]:
    """Evidence is only usable when bound to exactly the pinned bytes."""
    _require(isinstance(evidence, dict) and evidence.get('schema_version') == 1, 'unsupported BUILD_EVIDENCE schema')
    _require(evidence.get('scientific_effect') == 'NONE', 'build evidence must declare scientific_effect NONE')
    build = evidence.get('build')
    _require(isinstance(build, dict) and build.get('exit_code') == 0 and build.get('command') == 'lake build',
             'build evidence does not record a successful `lake build`')
    _require(evidence.get('toolchain') == lean_cfg['toolchain'], 'build evidence toolchain differs from status file')
    ev_sources = evidence.get('sources')
    _require(isinstance(ev_sources, dict), 'build evidence lacks sources')
    for rel, identity in sources.items():
        _require(rel in ev_sources, 'build evidence does not cover pinned source: ' + rel)
        _require(ev_sources[rel].get('sha256') == identity['sha256'] and ev_sources[rel].get('bytes') == identity['bytes'],
                 'build evidence is stale for source: ' + rel)
    for rel in ev_sources:
        _require(rel in sources, 'build evidence covers an unpinned source: ' + rel)
    decls = evidence.get('declarations')
    _require(isinstance(decls, dict), 'build evidence lacks declarations')
    for name, record in decls.items():
        _require(isinstance(record, dict) and isinstance(record.get('axioms'), list)
                 and all(isinstance(a, str) for a in record['axioms']),
                 'malformed axiom record for ' + name)
    _require(_exact_bool(evidence.get('sorry_free')) and evidence['sorry_free'] is True,
             'build evidence must record sorry_free == true')
    return decls


# ------------------------------------------------------------ review records

def verify_review_record(root: Path, component: dict[str, Any], module_identity: dict[str, Any],
                         formal_author_provider: str) -> dict[str, Any]:
    record_ref = component.get('review_record')
    _require(isinstance(record_ref, dict) and isinstance(record_ref.get('path'), str),
             'nonauthor-aligned requires a review_record.path')
    path = root / record_ref['path']
    _require(path.is_file(), 'review record missing: ' + record_ref['path'])
    record = load_json_strict(path.read_text(encoding='utf-8'))
    _require(record.get('verdict') == 'ALIGNED', 'review record verdict is not ALIGNED')
    _require(record.get('component_id') == component['component_id'], 'review record binds a different component')
    _require(record.get('reviewed_module_sha256') == module_identity['sha256'],
             'review record is bound to different module bytes (stale review)')
    _require(_norm_ws(record.get('reviewed_lean_statement', '')) == _norm_ws(component['lean_statement']),
             'review record statement differs from current lean_statement')
    prov = record.get('reviewer_provenance')
    _require(isinstance(prov, dict) and isinstance(prov.get('provider'), str) and prov['provider'].strip(),
             'review record lacks reviewer provenance')
    _require(prov.get('authored_formalization') is False, 'reviewer participated in authorship; not a nonauthor key')
    same_provider = prov['provider'].strip().lower() == formal_author_provider.strip().lower()
    return {
        'path': record_ref['path'],
        'reviewer_provider': prov['provider'],
        # Same-provider review earns no organizational-independence credit
        # (governance REVIEW_TOPOLOGY v1.1).  Reported, never inferred as true.
        'organizational_independence': False if same_provider or prov.get('provider', '').upper() == 'UNKNOWN' else 'ATTESTED_NOT_VALIDATED',
    }


# ------------------------------------------------------------------- gate

def evaluate_component(root: Path, component: dict[str, Any], sources: dict[str, dict[str, Any]],
                       evidence_decls: dict[str, Any] | None, standard_axioms: frozenset[str],
                       formal_author_provider: str) -> dict[str, Any]:
    cid = component.get('component_id')
    _require(isinstance(cid, str) and cid.strip(), 'component without component_id')
    declared = component.get('formalization_status')
    declared_level = _level(declared)
    review = component.get('formalization_review')
    _require(review in REVIEW_LADDER, 'unknown formalization_review: ' + repr(review))
    assumed = component.get('assumed_axioms')
    _require(isinstance(assumed, list), 'assumed_axioms must be a list')
    for entry in assumed:
        _require(isinstance(entry, dict) and isinstance(entry.get('name'), str)
                 and isinstance(entry.get('scope_note'), str) and entry['scope_note'].strip(),
                 'each assumed axiom needs name and nonempty scope_note: ' + cid)
    assumed_names = {a['name'] for a in assumed}
    _require(isinstance(component.get('does_not_claim'), str) and component['does_not_claim'].strip(),
             'component must state what it does not claim: ' + cid)

    result: dict[str, Any] = {
        'component_id': cid,
        'declared_status': declared,
        'declared_review': review,
        'verified_status': 'none',
        'verified_review': 'none',
        'conditional_on': sorted(assumed_names),
        'reasons': [],
    }
    if declared == 'none':
        _require(review == 'none', 'unformalized component cannot carry a review level')
        result['verified_review'] = 'none'
        result['promotion_token'] = None
        result['ok'] = True
        return result

    module_rel = component.get('lean_module')
    _require(module_rel in sources, 'lean_module is not a pinned source: ' + repr(module_rel))
    module = sources[module_rel]
    scan = scan_lean_module(module['text'])
    decl = component.get('lean_decl')
    _require(isinstance(decl, str) and decl in scan['declarations'],
             'lean_decl not found in module: ' + repr(decl))
    _require(statement_present(module['text'], component.get('lean_statement', '')),
             'lean_statement text is not present verbatim in module (alignment drift): ' + cid)
    kind = scan['declarations'][decl]['kind']
    verified = 1  # specified

    undeclared_axioms = [a for a in scan['axioms'] if a not in assumed_names]
    _require(not undeclared_axioms, 'module declares axioms not listed in assumed_axioms: ' + ','.join(undeclared_axioms))

    if kind in ('theorem', 'lemma') and not scan['sorry']:
        verified = 2  # proved (author-side text level)
        if evidence_decls is not None and decl in evidence_decls:
            axioms = set(evidence_decls[decl]['axioms'])
            foreign = sorted(axioms - standard_axioms - assumed_names)
            _require(not foreign, 'kernel evidence shows undeclared axioms for %s: %s' % (decl, ','.join(foreign)))
            _require('sorryAx' not in axioms, 'kernel evidence shows sorryAx for ' + decl)
            verified = 3  # kernel-checked
            result['kernel_axioms'] = sorted(axioms)
    elif kind in ('theorem', 'lemma') and scan['sorry']:
        result['reasons'].append('module contains sorry; theorem cannot exceed specified')
    else:
        _require(declared_level <= 1, 'a def/abbrev cannot be declared proved or kernel-checked: ' + decl)

    result['verified_status'] = STATUS_LADDER[verified]
    if declared_level > verified:
        result['reasons'].append('declared %s exceeds verifiable %s' % (declared, STATUS_LADDER[verified]))

    # Review lane.  The gate can confirm a nonauthor record is bound to these
    # bytes; it cannot manufacture organizational independence.
    result['verified_review'] = 'author-side'
    if review == 'nonauthor-aligned':
        result['review'] = verify_review_record(root, component, module, formal_author_provider)
        result['verified_review'] = 'nonauthor-aligned'
    elif review == 'none':
        result['reasons'].append('formalized component must at least be author-side')

    effective = STATUS_LADDER[min(declared_level, verified)]
    if effective == 'specified':
        token = TOKEN_SPECIFIED
    elif effective == 'proved':
        token = TOKEN_PROVED_AUTHOR
    elif assumed_names:
        token = TOKEN_KERNEL_CONDITIONAL
    elif result['verified_review'] == 'nonauthor-aligned':
        token = TOKEN_KERNEL_ALIGNED
    else:
        token = TOKEN_KERNEL_AUTHOR
    result['promotion_token'] = token
    result['non_discharge'] = token in FORMAL_NON_DISCHARGE
    result['ok'] = not result['reasons']
    return result


def run_gate(root: Path | None = None, *, status: dict[str, Any] | None = None,
             pins: dict[str, Any] | None = None, evidence: dict[str, Any] | None = None,
             require_evidence: bool = True) -> dict[str, Any]:
    root = (root or ROOT.parent).resolve()
    formal_dir = root / 'formal'
    status = status if status is not None else load_json_strict((formal_dir / 'FORMALIZATION_STATUS.json').read_text(encoding='utf-8'))
    pins = pins if pins is not None else load_json_strict((formal_dir / 'SOURCE_FILES.json').read_text(encoding='utf-8'))

    _require(isinstance(status, dict) and status.get('schema_version') == 1, 'unsupported FORMALIZATION_STATUS schema')
    _require(status.get('scientific_effect') == 'NONE', 'status file must declare scientific_effect NONE')
    _require(_exact_bool(status.get('lemma_closed')) and status['lemma_closed'] is False, 'lemma_closed must be exact false')
    _require(_exact_bool(status.get('mathematical_acceptance')) and status['mathematical_acceptance'] is False,
             'mathematical_acceptance must be exact false')
    _require(tuple(status.get('status_ladder', ())) == STATUS_LADDER, 'status_ladder differs from gate ladder')
    _require(tuple(status.get('review_ladder', ())) == REVIEW_LADDER, 'review_ladder differs from gate ladder')
    standard = frozenset(status.get('standard_axioms', ()))
    _require(standard == STANDARD_AXIOMS, 'standard_axioms differ from the Lean kernel standard set')
    lean_cfg = status.get('lean')
    _require(isinstance(lean_cfg, dict) and isinstance(lean_cfg.get('toolchain'), str)
             and lean_cfg.get('project_root') == pins.get('project_root'),
             'lean project configuration missing or inconsistent with SOURCE_FILES')
    toolchain_file = root / lean_cfg['project_root'] / 'lean-toolchain'
    _require(toolchain_file.is_file() and toolchain_file.read_text().strip() == lean_cfg['toolchain'],
             'lean-toolchain file differs from declared toolchain')

    sources = verify_source_pins(root, pins)

    evidence_decls: dict[str, Any] | None = None
    evidence_path = formal_dir / 'BUILD_EVIDENCE.json'
    if evidence is None and evidence_path.is_file():
        evidence = load_json_strict(evidence_path.read_text(encoding='utf-8'))
    if evidence is not None:
        evidence_decls = verify_build_evidence(evidence, sources, lean_cfg)
    elif require_evidence:
        raise GateError('BUILD_EVIDENCE.json is required (run lean_build_evidence.py)')

    objects = status.get('objects')
    _require(isinstance(objects, list) and objects, 'status file has no objects')
    seen_components: set[str] = set()
    report_objects = []
    for obj in objects:
        _require(isinstance(obj, dict) and isinstance(obj.get('object_id'), str), 'malformed object record')
        src = obj.get('informal_source')
        _require(isinstance(src, dict) and all(isinstance(src.get(k), str) and src[k] for k in ('repository', 'path', 'commit', 'sha256')),
                 'object must bind an informal source by repository/path/commit/sha256: ' + obj['object_id'])
        _require(re.fullmatch(r'[0-9a-f]{40}', src['commit']) is not None, 'informal_source.commit must be a full OID')
        author = obj.get('authorship')
        _require(isinstance(author, dict) and isinstance(author.get('formal_provider'), str), 'object lacks authorship.formal_provider')
        comps = obj.get('components')
        _require(isinstance(comps, list) and comps, 'object has no components: ' + obj['object_id'])
        results = []
        for comp in comps:
            res = evaluate_component(root, comp, sources, evidence_decls, standard, author['formal_provider'])
            _require(res['component_id'] not in seen_components, 'duplicate component_id: ' + res['component_id'])
            seen_components.add(res['component_id'])
            results.append(res)
        report_objects.append({
            'object_id': obj['object_id'],
            'hard_gate_node': obj.get('hard_gate_node'),
            'informal_source': src,
            'components': results,
            'formal_lane_satisfied': all(r.get('promotion_token') == TOKEN_KERNEL_ALIGNED for r in results if r['declared_status'] != 'none') and any(r['declared_status'] != 'none' for r in results),
        })

    failures = [r['component_id'] + ': ' + '; '.join(r['reasons'])
                for o in report_objects for r in o['components'] if not r['ok']]
    return {
        'object': status.get('object'),
        'passed': not failures,
        'failures': failures,
        'evidence_present': evidence is not None,
        'objects': report_objects,
        'lemma_closed': False,
        'mathematical_acceptance': False,
        'scientific_effect': 'NONE',
        'meaning': 'formalization-status integrity only; kernel evidence verifies encoded statements, not translation fidelity or theorem acceptance',
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--root', type=Path, default=ROOT.parent)
    parser.add_argument('--json', action='store_true', help='print the full report')
    parser.add_argument('--allow-missing-evidence', action='store_true',
                        help='text-level checks only; kernel-checked declarations will fail')
    args = parser.parse_args(argv)
    try:
        report = run_gate(args.root, require_evidence=not args.allow_missing_evidence)
    except GateError as exc:
        print('FORMAL_GATE REFUSED: ' + str(exc))
        return 2
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        for obj in report['objects']:
            for comp in obj['components']:
                print('%-40s declared=%-14s verified=%-14s review=%-18s token=%s' % (
                    comp['component_id'], comp['declared_status'], comp['verified_status'],
                    comp['verified_review'], comp.get('promotion_token')))
        for failure in report['failures']:
            print('FAIL ' + failure)
    print('FORMAL_GATE ' + ('PASSED' if report['passed'] else 'FAILED') + ' (scientific effect NONE; lemma_closed false)')
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    sys.exit(main())
