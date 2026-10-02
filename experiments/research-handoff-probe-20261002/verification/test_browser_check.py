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
        report = {'browser_run_started': True, 'cases': [{'passed': True}] * 8}
        self.assertTrue(check(report))
        self.assertFalse(check({**report, 'browser_run_started': False}))
        self.assertFalse(check({**report, 'cases': report['cases'][:-1]}))
        self.assertFalse(check({**report, 'cases': [{'passed': False}] + report['cases'][1:]}))

if __name__ == '__main__':
    unittest.main()
