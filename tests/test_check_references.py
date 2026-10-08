"""Regression tests for the reference checker's self-test diagnostics."""

import contextlib
import importlib.util
import io
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHECKER = os.path.join(ROOT, "tools", "check_references.py")


def load_checker():
    spec = importlib.util.spec_from_file_location("check_references", CHECKER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestSelfTestDiagnostics(unittest.TestCase):
    def test_failure_names_the_case_not_the_last_image(self):
        module = load_checker()
        # Force every fixture to fail so _self_test prints its diagnostics.
        module.check_references = lambda directory: ["boom"]
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = module._self_test()
        self.assertEqual(code, 1)
        printed = out.getvalue()
        self.assertIn("self-test 'undeclared image'", printed)
        self.assertNotIn("self-test 'extra.png'", printed)


if __name__ == "__main__":
    unittest.main()
