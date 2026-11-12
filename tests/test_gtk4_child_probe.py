"""The shared GTK 4 probe runner's skip, failure and child contract.

The probe suites themselves skip when GTK is absent, so these cases use
plain child programs that never import ``gi``: they pin how the runner
maps the child's exit status onto the test, what argv and environment the
child receives, and nothing about the rendered pixels.
"""

import unittest

from support.gtk4_child_probe import run_gtk4_probe
from support.gtk4_sheet import THEME_DIR


class TestRunGtk4Probe(unittest.TestCase):
    def test_exit_77_skips_the_test(self):
        case = unittest.TestCase()
        with self.assertRaises(unittest.SkipTest):
            run_gtk4_probe(case, "import sys; sys.exit(77)")

    def test_other_nonzero_exit_fails_with_child_output(self):
        case = unittest.TestCase()
        with self.assertRaises(AssertionError) as raised:
            run_gtk4_probe(case, "print('pin missed'); import sys; sys.exit(3)")
        self.assertIn("pin missed", str(raised.exception))

    def test_zero_exit_passes(self):
        run_gtk4_probe(unittest.TestCase(), "import sys; sys.exit(0)")

    def test_child_receives_theme_dir_as_argv_one(self):
        program = (
            "import sys\n"
            f"sys.exit(0 if sys.argv[1] == {str(THEME_DIR)!r} else 5)\n"
        )
        run_gtk4_probe(unittest.TestCase(), program)

    def test_child_runs_under_the_x11_backend_and_cairo_renderer(self):
        program = (
            "import os, sys\n"
            "ok = (os.environ.get('GDK_BACKEND') == 'x11'\n"
            "      and os.environ.get('GSK_RENDERER') == 'cairo')\n"
            "sys.exit(0 if ok else 6)\n"
        )
        run_gtk4_probe(unittest.TestCase(), program)


if __name__ == "__main__":
    unittest.main()
