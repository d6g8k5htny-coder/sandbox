"""Tests for blueprint_check.py (software behavior only; scientific effect NONE)."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import blueprint_check as bc  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
CONTENT = (REPO / 'formal' / 'blueprint' / 'src' / 'content.tex').read_text(encoding='utf-8')
DECLS = (REPO / 'formal' / 'blueprint' / 'lean_decls').read_text(encoding='utf-8')


class BlueprintTests(unittest.TestCase):
    def test_committed_blueprint_aligns(self):
        result = bc.check(REPO)
        self.assertTrue(result['passed'], result['problems'])
        self.assertEqual(len(result['bound']), 22)

    def test_leanok_on_specified_component_is_refused(self):
        mutated = CONTENT.replace('\\lean{Side24.ratio_bound_statement}', '\\lean{Side24.ratio_bound_statement}\\leanok')
        self.assertFalse(bc.check(REPO, content=mutated, decls_text=DECLS)['passed'])

    def test_missing_leanok_on_kernel_checked_is_refused(self):
        mutated = CONTENT.replace('\\lean{Side24.image_constant_eq}\\leanok', '\\lean{Side24.image_constant_eq}')
        self.assertFalse(bc.check(REPO, content=mutated, decls_text=DECLS)['passed'])

    def test_unknown_declaration_is_refused(self):
        mutated = CONTENT.replace('\\lean{Side24.image_constant_eq}', '\\lean{Side24.parent_theorem}')
        self.assertFalse(bc.check(REPO, content=mutated, decls_text=DECLS)['passed'])

    def test_dropped_component_is_refused(self):
        start = CONTENT.index('\\begin{lemma}\\label{lem:truncation}')
        end = CONTENT.index('\\end{lemma}', start) + len('\\end{lemma}')
        mutated = CONTENT[:start] + CONTENT[end:]
        self.assertFalse(bc.check(REPO, content=mutated, decls_text=DECLS)['passed'])

    def test_stale_decl_list_is_refused(self):
        self.assertFalse(bc.check(REPO, content=CONTENT, decls_text=DECLS + 'Side24.extra\n')['passed'])


if __name__ == '__main__':
    unittest.main()
