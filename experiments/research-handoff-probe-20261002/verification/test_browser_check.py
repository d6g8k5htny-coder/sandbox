"""Negative controls for the evidence gates, without launching a browser."""
import importlib.util
from pathlib import Path
import unittest

PATH = Path(__file__).with_name('browser_check.py')

class GateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = None
        if PATH.exists():
            spec = importlib.util.spec_from_file_location('browser_check', PATH)
            cls.module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(cls.module)

    def gate(self, name):
        self.assertIsNotNone(self.module, 'browser evidence gate implementation is missing')
        self.assertTrue(callable(getattr(self.module, name, None)), f'{name} gate implementation is missing')
        return getattr(self.module, name)

    def test_request_gate_allows_only_fixed_local_gets(self):
        check = self.gate('validate_requests')
        allowed = [{'url': 'http://127.0.0.1:9876/' + p, 'method': 'GET', 'has_post_data': False} for p in ['', 'index.html', 'app.mjs', 'packet.mjs', 'style.css', 'fixtures/packet.json', 'synthetic-away', 'favicon.ico']]
        check(allowed, 'http://127.0.0.1:9876/')
        for change in [{'url': 'https://example.invalid/x'}, {'url': 'http://127.0.0.1:9876/x'}, {'url': 'http://127.0.0.1:9876/?payload=1'}, {'method': 'POST'}, {'has_post_data': True}]:
            with self.subTest(change=change), self.assertRaises(ValueError):
                check([{**allowed[0], **change}], 'http://127.0.0.1:9876/')
        with self.assertRaises(ValueError):
            check([], 'http://127.0.0.1:9876/')

    def test_storage_gate_refuses_every_persistent_store(self):
        check = self.gate('validate_storage')
        blank = {'local': [], 'session': [], 'cookies': [], 'indexedDB': [], 'caches': [], 'serviceWorkers': []}
        check(blank)
        for key in blank:
            with self.subTest(key=key), self.assertRaises(ValueError):
                check({**blank, key: ['unexpected']})

    def test_result_gate_never_calls_no_browser_or_partial_cases_a_pass(self):
        check = self.gate('report_passes')
        report = {'browser_run_started': True, 'cases': [{'passed': True}] * 16}
        self.assertTrue(check(report))
        self.assertFalse(check({**report, 'browser_run_started': False}))
        self.assertFalse(check({**report, 'cases': report['cases'][:-1]}))
        self.assertFalse(check({**report, 'cases': [{'passed': False}] + report['cases'][1:]}))

    def test_comparison_refuses_incorrect_saturated_or_different_semantic_outputs(self):
        compare = self.gate('comparison_summary')
        rows = []
        for condition in ['desktop', 'mobile390', 'mobile320', 'large390', 'large320']:
            for mode in ['BASELINE', 'CANDIDATE']:
                rows.append({'condition': condition, 'mode': mode, 'task_correct': True,
                    'ui_activations': ['open-B', 'close', 'restore', 'preview'],
                    'telemetry': {'saturated': False, 'comparisonEligible': True, 'counts': {'sourceOpens': 1, 'sourceReopens': 0, 'rawEvidenceExpansions': 0, 'recheckRequests': 1, 'previewPassportExposures': 2}},
                    'semantic_output': {'preview': 'same exact semantic output'},
                    'geometry_default': {'preview_height_px': 4500, 'document_height_px': 18000},
                    'geometry_expanded': {'preview_height_px': 6000, 'document_height_px': 19500}})
        result = compare(rows)
        self.assertEqual(result['status'], 'COMPARABLE_DESCRIPTIVE_ONLY')
        self.assertTrue(all(x['action_difference_candidate_minus_baseline'] == 0 for x in result['pairs']))
        self.assertTrue(all(x['identity_exposure_difference_candidate_minus_baseline'] == 0 for x in result['pairs']))
        import copy
        for kind in ['incorrect', 'saturated', 'semantics', 'missing']:
            bad = copy.deepcopy(rows)
            if kind == 'incorrect': bad[0]['task_correct'] = False
            if kind == 'saturated': bad[0]['telemetry']['saturated'] = True
            if kind == 'semantics': bad[0]['semantic_output']['preview'] = 'different'
            if kind == 'missing': bad.pop()
            with self.subTest(kind=kind), self.assertRaises(ValueError): compare(bad)

if __name__ == '__main__':
    unittest.main()
