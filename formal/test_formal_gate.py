"""Tests and assertion-detected semantic mutants for formal_gate.py.

Every mutant is an in-memory edit of the real status/pins/evidence trees that a
careless or adversarial author could make; each must be refused.  Passing tests
prove software behavior only (scientific effect NONE).

    python -B -S -m unittest discover -s formal -p 'test_*.py' -v
    python -B -O -S -m unittest discover -s formal -p 'test_*.py' -v
"""
from __future__ import annotations

import contextlib
import copy
import io
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import formal_gate as fg  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
FORMAL = REPO / 'formal'


def _load(name: str):
    return fg.load_json_strict((FORMAL / name).read_text(encoding='utf-8'))


def _component(status, cid):
    for obj in status['objects']:
        for comp in obj['components']:
            if comp['component_id'] == cid:
                return comp
    raise KeyError(cid)


class _Tree:
    """Copy of the formal tree in a temp dir so mutants can rewrite Lean bytes."""

    def __init__(self):
        self.dir = Path(tempfile.mkdtemp(prefix='formal-gate-'))
        shutil.copytree(FORMAL, self.dir / 'formal', ignore=shutil.ignore_patterns('.lake', '__pycache__'))
        self.status = _load('FORMALIZATION_STATUS.json')
        self.pins = _load('SOURCE_FILES.json')
        self.evidence = _load('BUILD_EVIDENCE.json')

    def module(self, rel: str) -> Path:
        return self.dir / self.pins['project_root'] / rel

    def rewrite_module(self, rel: str, text: str, *, repin: bool = True, re_evidence: bool = True):
        path = self.module(rel)
        path.write_text(text, encoding='utf-8')
        data = path.read_bytes()
        identity = {'bytes': len(data), 'sha256': fg.sha256_bytes(data)}
        if repin:
            self.pins['files'][rel] = dict(identity)
        if re_evidence:
            self.evidence['sources'][rel] = dict(identity)

    def run(self, **kw):
        return fg.run_gate(self.dir, status=self.status, pins=self.pins, evidence=self.evidence, **kw)

    def cleanup(self):
        shutil.rmtree(self.dir, ignore_errors=True)


KERNEL = 'side24.ledger.image-constant'
SPECIFIED = 'side24.theorem.enclosure'
THEOREM_MODULE = 'Side24Formal/Ledger.lean'


class RealTreeTests(unittest.TestCase):
    def test_committed_tree_passes(self):
        report = fg.run_gate(REPO)
        self.assertTrue(report['passed'], report['failures'])
        self.assertEqual(report['scientific_effect'], 'NONE')
        self.assertIs(report['lemma_closed'], False)
        self.assertIs(report['mathematical_acceptance'], False)

    def test_no_component_reaches_nonauthor_lane_by_default(self):
        report = fg.run_gate(REPO)
        tokens = {c['promotion_token'] for o in report['objects'] for c in o['components']}
        self.assertNotIn(fg.TOKEN_KERNEL_ALIGNED, tokens)
        self.assertFalse(any(o['formal_lane_satisfied'] for o in report['objects']))

    def test_every_formal_token_except_aligned_is_non_discharge(self):
        report = fg.run_gate(REPO)
        for obj in report['objects']:
            for comp in obj['components']:
                self.assertTrue(comp['non_discharge'], comp['component_id'])
                self.assertIn(comp['promotion_token'], fg.FORMAL_NON_DISCHARGE)

    def test_kernel_checked_components_use_standard_axioms_only(self):
        report = fg.run_gate(REPO)
        for obj in report['objects']:
            for comp in obj['components']:
                if comp['verified_status'] == 'kernel-checked':
                    self.assertTrue(set(comp['kernel_axioms']) <= fg.STANDARD_AXIOMS)
                    self.assertEqual(comp['conditional_on'], [])

    def test_declared_status_never_exceeds_verified(self):
        report = fg.run_gate(REPO)
        for obj in report['objects']:
            for comp in obj['components']:
                self.assertLessEqual(fg.STATUS_LADDER.index(comp['declared_status']),
                                     fg.STATUS_LADDER.index(comp['verified_status']))

    def test_headline_theorem_is_only_specified(self):
        report = fg.run_gate(REPO)
        comp = next(c for o in report['objects'] for c in o['components'] if c['component_id'] == SPECIFIED)
        self.assertEqual(comp['verified_status'], 'specified')
        self.assertEqual(comp['promotion_token'], fg.TOKEN_SPECIFIED)

    def test_pins_match_lean_sources(self):
        pins = _load('SOURCE_FILES.json')
        for rel, identity in pins['files'].items():
            data = (REPO / pins['project_root'] / rel).read_bytes()
            self.assertEqual(identity['sha256'], fg.sha256_bytes(data), rel)
            self.assertEqual(identity['bytes'], len(data), rel)

    def test_evidence_sorry_free_and_successful_build(self):
        evidence = _load('BUILD_EVIDENCE.json')
        self.assertIs(evidence['sorry_free'], True)
        self.assertEqual(evidence['build']['exit_code'], 0)
        self.assertEqual(evidence['scientific_effect'], 'NONE')

    def test_cli_passes_and_prints_scientific_effect(self):
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            code = fg.main(['--root', str(REPO)])
        self.assertEqual(code, 0)
        self.assertIn('FORMAL_GATE PASSED (scientific effect NONE; lemma_closed false)', buffer.getvalue())

    def test_missing_evidence_is_refused_unless_allowed(self):
        tree = _Tree()
        try:
            (tree.dir / 'formal' / 'BUILD_EVIDENCE.json').unlink()
            with self.assertRaises(fg.GateError):
                fg.run_gate(tree.dir, status=tree.status, pins=tree.pins, evidence=None)
            # allow-missing: kernel-checked declarations now exceed verifiable 'proved'
            report = fg.run_gate(tree.dir, status=tree.status, pins=tree.pins, evidence=None, require_evidence=False)
            self.assertFalse(report['passed'])
            self.assertFalse(report['evidence_present'])
            kernel = next(c for o in report['objects'] for c in o['components'] if c['component_id'] == KERNEL)
            self.assertEqual(kernel['verified_status'], 'proved')
        finally:
            tree.cleanup()


class ScanTests(unittest.TestCase):
    def test_scan_finds_declarations_with_namespace(self):
        scan = fg.scan_lean_module('namespace X\ntheorem foo : True := trivial\nnoncomputable def bar : Nat := 0\nend X\n')
        self.assertEqual(scan['declarations']['X.foo']['kind'], 'theorem')
        self.assertEqual(scan['declarations']['X.bar']['kind'], 'noncomputable def')
        self.assertFalse(scan['sorry'])
        self.assertEqual(scan['axioms'], [])

    def test_scan_detects_sorry_and_axiom_but_not_in_comments(self):
        scan = fg.scan_lean_module('namespace X\n-- sorry here is a comment\n/- axiom nope -/\naxiom hidden : False\ntheorem foo : True := by sorry\nend X\n')
        self.assertTrue(scan['sorry'])
        self.assertEqual(scan['axioms'], ['X.hidden'])

    def test_scan_ignores_identifiers_containing_sorry(self):
        scan = fg.scan_lean_module('theorem notsorry_lemma : True := trivial\n')
        self.assertFalse(scan['sorry'])

    def test_statement_presence_is_whitespace_insensitive_only(self):
        text = 'theorem foo :\n    1 + 1 = 2 := by norm_num\n'
        self.assertTrue(fg.statement_present(text, 'theorem foo : 1 + 1 = 2'))
        self.assertFalse(fg.statement_present(text, 'theorem foo : 1 + 1 = 3'))

    def test_strict_json_rejects_duplicates_and_nan(self):
        with self.assertRaises(fg.GateError):
            fg.load_json_strict('{"a": 1, "a": 2}')
        with self.assertRaises(fg.GateError):
            fg.load_json_strict('{"a": NaN}')


# ------------------------------------------------------------------ mutants

def _m_declare_specified_as_kernel(t: _Tree):
    _component(t.status, SPECIFIED)['formalization_status'] = 'kernel-checked'


def _m_declare_specified_as_proved(t: _Tree):
    _component(t.status, SPECIFIED)['formalization_status'] = 'proved'


def _m_insert_sorry(t: _Tree):
    text = t.module(THEOREM_MODULE).read_text(encoding='utf-8')
    text = text.replace('theorem image_constant_eq : (1458 : ℕ) * (76 * 24 ^ 6 + 15) = 21175738586478 := by\n  norm_num',
                        'theorem image_constant_eq : (1458 : ℕ) * (76 * 24 ^ 6 + 15) = 21175738586478 := by\n  sorry')
    assert 'sorry' in text
    t.rewrite_module(THEOREM_MODULE, text)


def _m_undeclared_axiom(t: _Tree):
    text = t.module(THEOREM_MODULE).read_text(encoding='utf-8')
    t.rewrite_module(THEOREM_MODULE, text.replace('namespace Side24\n', 'namespace Side24\naxiom parent_theorem : False\n', 1))


def _m_source_edit_without_repin(t: _Tree):
    text = t.module(THEOREM_MODULE).read_text(encoding='utf-8')
    t.rewrite_module(THEOREM_MODULE, text + '\n', repin=False, re_evidence=True)


def _m_source_edit_with_stale_evidence(t: _Tree):
    text = t.module(THEOREM_MODULE).read_text(encoding='utf-8')
    t.rewrite_module(THEOREM_MODULE, text + '\n', repin=True, re_evidence=False)


def _m_statement_drift(t: _Tree):
    _component(t.status, KERNEL)['lean_statement'] = 'theorem image_constant_eq : (1458 : ℕ) * (76 * 24 ^ 6 + 15) = 21175738586479'


def _m_decl_missing(t: _Tree):
    _component(t.status, KERNEL)['lean_decl'] = 'Side24.not_a_declaration'


def _m_evidence_sorry_axiom(t: _Tree):
    t.evidence['declarations']['Side24.image_constant_eq']['axioms'].append('sorryAx')


def _m_evidence_foreign_axiom(t: _Tree):
    t.evidence['declarations']['Side24.image_constant_eq']['axioms'].append('Side24.parent_theorem')


def _m_evidence_failed_build(t: _Tree):
    t.evidence['build']['exit_code'] = 1


def _m_evidence_not_sorry_free(t: _Tree):
    t.evidence['sorry_free'] = False


def _m_evidence_sorry_free_string(t: _Tree):
    t.evidence['sorry_free'] = 'true'


def _m_evidence_wrong_toolchain(t: _Tree):
    t.evidence['toolchain'] = 'leanprover/lean4:v4.0.0'


def _m_lemma_closed_true(t: _Tree):
    t.status['lemma_closed'] = True


def _m_lemma_closed_string_false(t: _Tree):
    t.status['lemma_closed'] = 'false'


def _m_mathematical_acceptance_true(t: _Tree):
    t.status['mathematical_acceptance'] = True


def _m_scientific_effect(t: _Tree):
    t.status['scientific_effect'] = 'PROMOTION'


def _m_ladder_extended(t: _Tree):
    t.status['status_ladder'] = list(t.status['status_ladder']) + ['accepted']


def _m_standard_axioms_widened(t: _Tree):
    t.status['standard_axioms'] = list(t.status['standard_axioms']) + ['Side24.parent_theorem']


def _m_nonauthor_without_record(t: _Tree):
    _component(t.status, KERNEL)['formalization_review'] = 'nonauthor-aligned'


def _m_nonauthor_stale_record(t: _Tree):
    comp = _component(t.status, KERNEL)
    comp['formalization_review'] = 'nonauthor-aligned'
    comp['review_record'] = {'path': 'formal/reviews/stale.json'}
    (t.dir / 'formal' / 'reviews').mkdir(exist_ok=True)
    (t.dir / 'formal' / 'reviews' / 'stale.json').write_text(json.dumps({
        'verdict': 'ALIGNED', 'component_id': KERNEL,
        'reviewed_module_sha256': '0' * 64,
        'reviewed_lean_statement': comp['lean_statement'],
        'reviewer_provenance': {'provider': 'OpenAI', 'authored_formalization': False},
    }), encoding='utf-8')


def _m_nonauthor_record_by_author(t: _Tree):
    comp = _component(t.status, KERNEL)
    comp['formalization_review'] = 'nonauthor-aligned'
    comp['review_record'] = {'path': 'formal/reviews/self.json'}
    (t.dir / 'formal' / 'reviews').mkdir(exist_ok=True)
    (t.dir / 'formal' / 'reviews' / 'self.json').write_text(json.dumps({
        'verdict': 'ALIGNED', 'component_id': KERNEL,
        'reviewed_module_sha256': t.pins['files'][THEOREM_MODULE]['sha256'],
        'reviewed_lean_statement': comp['lean_statement'],
        'reviewer_provenance': {'provider': 'Anthropic / Claude', 'authored_formalization': True},
    }), encoding='utf-8')


def _m_nonauthor_record_amend_required(t: _Tree):
    comp = _component(t.status, KERNEL)
    comp['formalization_review'] = 'nonauthor-aligned'
    comp['review_record'] = {'path': 'formal/reviews/amend.json'}
    (t.dir / 'formal' / 'reviews').mkdir(exist_ok=True)
    (t.dir / 'formal' / 'reviews' / 'amend.json').write_text(json.dumps({
        'verdict': 'AMEND_REQUIRED', 'component_id': KERNEL,
        'reviewed_module_sha256': t.pins['files'][THEOREM_MODULE]['sha256'],
        'reviewed_lean_statement': comp['lean_statement'],
        'reviewer_provenance': {'provider': 'OpenAI', 'authored_formalization': False},
    }), encoding='utf-8')


def _m_assumed_axiom_without_scope_note(t: _Tree):
    t.status['assumed_axioms'] = [{'name': 'Side24.parent_theorem', 'scope_note': ''}]


def _m_registry_lists_standard_axiom(t: _Tree):
    t.status['assumed_axioms'] = [{'name': 'propext', 'scope_note': 'smuggle'}]


def _m_registered_axiom_still_blocks_aligned_lane(t: _Tree):
    """A registered parent axiom used by a nonauthor-aligned theorem must stay CONDITIONAL."""
    text = t.module(THEOREM_MODULE).read_text(encoding='utf-8')
    t.rewrite_module(THEOREM_MODULE, text.replace('namespace Side24\n', 'namespace Side24\naxiom parent_theorem : True\n', 1))
    t.status['assumed_axioms'] = [{'name': 'Side24.parent_theorem', 'scope_note': 'assumed parent'}]
    t.evidence['declarations']['Side24.image_constant_eq']['axioms'].append('Side24.parent_theorem')
    comp = _component(t.status, KERNEL)
    comp['formalization_review'] = 'nonauthor-aligned'
    comp['review_record'] = {'path': 'formal/reviews/ok.json'}
    (t.dir / 'formal' / 'reviews').mkdir(exist_ok=True)
    (t.dir / 'formal' / 'reviews' / 'ok.json').write_text(json.dumps({
        'verdict': 'ALIGNED', 'component_id': KERNEL,
        'reviewed_module_sha256': t.pins['files'][THEOREM_MODULE]['sha256'],
        'reviewed_lean_statement': comp['lean_statement'],
        'reviewer_provenance': {'provider': 'OpenAI', 'authored_formalization': False},
    }), encoding='utf-8')
    t.expect_token = fg.TOKEN_KERNEL_CONDITIONAL


def _m_missing_does_not_claim(t: _Tree):
    _component(t.status, KERNEL)['does_not_claim'] = ''


def _m_informal_source_short_commit(t: _Tree):
    t.status['objects'][0]['informal_source']['commit'] = '760340e'


def _m_duplicate_component(t: _Tree):
    comps = t.status['objects'][0]['components']
    comps.append(copy.deepcopy(comps[0]))


def _m_toolchain_file_drift(t: _Tree):
    (t.dir / t.pins['project_root'] / 'lean-toolchain').write_text('leanprover/lean4:v4.0.0\n')


def _m_unpinned_module_referenced(t: _Tree):
    del t.pins['files'][THEOREM_MODULE]
    del t.evidence['sources'][THEOREM_MODULE]


def _m_evidence_missing_module(t: _Tree):
    del t.evidence['sources'][THEOREM_MODULE]


MUTANTS = [
    _m_declare_specified_as_kernel, _m_declare_specified_as_proved, _m_insert_sorry,
    _m_undeclared_axiom, _m_source_edit_without_repin, _m_source_edit_with_stale_evidence,
    _m_statement_drift, _m_decl_missing, _m_evidence_sorry_axiom, _m_evidence_foreign_axiom,
    _m_evidence_failed_build, _m_evidence_not_sorry_free, _m_evidence_sorry_free_string,
    _m_evidence_wrong_toolchain, _m_lemma_closed_true, _m_lemma_closed_string_false,
    _m_mathematical_acceptance_true, _m_scientific_effect, _m_ladder_extended,
    _m_standard_axioms_widened, _m_nonauthor_without_record, _m_nonauthor_stale_record,
    _m_nonauthor_record_by_author, _m_nonauthor_record_amend_required,
    _m_assumed_axiom_without_scope_note, _m_registry_lists_standard_axiom, _m_missing_does_not_claim,
    _m_informal_source_short_commit, _m_duplicate_component, _m_toolchain_file_drift,
    _m_unpinned_module_referenced, _m_evidence_missing_module, _m_registered_axiom_still_blocks_aligned_lane,
]


class MutantTests(unittest.TestCase):
    def _refused(self, mutant):
        """True when the mutant is refused, or (for token mutants) demoted to the expected token."""
        tree = _Tree()
        try:
            mutant(tree)
            try:
                report = tree.run()
            except fg.GateError:
                return True
            expected = getattr(tree, 'expect_token', None)
            if expected is not None:
                res = next(c for o in report['objects'] for c in o['components'] if c['component_id'] == KERNEL)
                return res['promotion_token'] == expected and res['non_discharge'] and not report['objects'][0]['formal_lane_satisfied']
            return not report['passed']
        finally:
            tree.cleanup()

    def test_unmutated_copy_passes(self):
        tree = _Tree()
        try:
            self.assertTrue(tree.run()['passed'])
        finally:
            tree.cleanup()

    def test_every_semantic_mutant_is_refused(self):
        survivors = [m.__name__ for m in MUTANTS if not self._refused(m)]
        self.assertEqual(survivors, [], 'mutants survived: ' + ','.join(survivors))

    def test_mutant_count_is_the_documented_scope(self):
        self.assertEqual(len(MUTANTS), 33)


class HonestReviewRecordTests(unittest.TestCase):
    def test_valid_nonauthor_record_reaches_aligned_lane_without_promotion(self):
        tree = _Tree()
        try:
            comp = _component(tree.status, KERNEL)
            comp['formalization_review'] = 'nonauthor-aligned'
            comp['review_record'] = {'path': 'formal/reviews/ok.json'}
            (tree.dir / 'formal' / 'reviews').mkdir(exist_ok=True)
            (tree.dir / 'formal' / 'reviews' / 'ok.json').write_text(json.dumps({
                'verdict': 'ALIGNED', 'component_id': KERNEL,
                'reviewed_module_sha256': tree.pins['files'][THEOREM_MODULE]['sha256'],
                'reviewed_lean_statement': comp['lean_statement'],
                'reviewer_provenance': {'provider': 'OpenAI', 'authored_formalization': False},
            }), encoding='utf-8')
            report = tree.run()
            self.assertTrue(report['passed'], report['failures'])
            res = next(c for o in report['objects'] for c in o['components'] if c['component_id'] == KERNEL)
            self.assertEqual(res['promotion_token'], fg.TOKEN_KERNEL_ALIGNED)
            self.assertFalse(res['non_discharge'])
            self.assertEqual(res['review']['organizational_independence'], 'ATTESTED_NOT_VALIDATED')
            # one aligned component does not satisfy the object lane
            self.assertFalse(report['objects'][0]['formal_lane_satisfied'])
            self.assertIs(report['lemma_closed'], False)
        finally:
            tree.cleanup()

    def test_same_provider_review_gets_no_independence_credit(self):
        tree = _Tree()
        try:
            comp = _component(tree.status, KERNEL)
            comp['formalization_review'] = 'nonauthor-aligned'
            comp['review_record'] = {'path': 'formal/reviews/same.json'}
            (tree.dir / 'formal' / 'reviews').mkdir(exist_ok=True)
            (tree.dir / 'formal' / 'reviews' / 'same.json').write_text(json.dumps({
                'verdict': 'ALIGNED', 'component_id': KERNEL,
                'reviewed_module_sha256': tree.pins['files'][THEOREM_MODULE]['sha256'],
                'reviewed_lean_statement': comp['lean_statement'],
                'reviewer_provenance': {'provider': 'Anthropic / Claude (Cursor cloud agent)', 'authored_formalization': False},
            }), encoding='utf-8')
            report = tree.run()
            res = next(c for o in report['objects'] for c in o['components'] if c['component_id'] == KERNEL)
            self.assertIs(res['review']['organizational_independence'], False)
        finally:
            tree.cleanup()

    def test_assumed_axiom_with_scope_note_yields_conditional_token(self):
        tree = _Tree()
        try:
            text = tree.module(THEOREM_MODULE).read_text(encoding='utf-8')
            tree.rewrite_module(THEOREM_MODULE, text.replace('namespace Side24\n', 'namespace Side24\naxiom parent_theorem : True\n', 1))
            tree.status['assumed_axioms'] = [{'name': 'Side24.parent_theorem', 'scope_note': 'parent main #63 assumed; not independently verified'}]
            tree.evidence['declarations']['Side24.image_constant_eq']['axioms'].append('Side24.parent_theorem')
            report = tree.run()
            self.assertTrue(report['passed'], report['failures'])
            res = next(c for o in report['objects'] for c in o['components'] if c['component_id'] == KERNEL)
            self.assertEqual(res['promotion_token'], fg.TOKEN_KERNEL_CONDITIONAL)
            self.assertEqual(res['conditional_on'], ['Side24.parent_theorem'])
            self.assertTrue(res['non_discharge'])
        finally:
            tree.cleanup()


if __name__ == '__main__':
    unittest.main()
