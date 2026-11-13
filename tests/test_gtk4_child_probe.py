"""The shared GTK 4 probe runner's skip, failure and child contract.

The probe suites themselves skip when GTK is absent, so these cases use
plain child programs that never import ``gi``: they pin how the runner
maps the child's exit status onto the test, what argv and environment the
child receives, and nothing about the rendered pixels.
"""

import unittest
from pathlib import Path

from support.gtk4_child_probe import GTK4_PROBE_PROLOGUE, run_gtk4_probe
from support.gtk4_sheet import THEME_DIR

# The six suites whose child programs interpolate the shared prologue; the
# spin probe's child never sets ``gtk-theme-name``, so it keeps its own.
_PROLOGUE_SUITES = (
    "test_gtk4_button_probe.py",
    "test_gtk4_indicators_probe.py",
    "test_gtk4_notebook_probe.py",
    "test_gtk4_progressbar_probe.py",
    "test_gtk4_scale_probe.py",
    "test_gtk4_scrollbar_probe.py",
)


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

    def test_prologue_boots_gtk_and_loads_the_theme_sheet(self):
        # The bootstrap's contract: init GTK 4 and skip on a missing gi
        # module or X11 display, select Adwaita so the sheet's provider
        # races a real theme, then load gtk-4.0/gtk.css with the asset URIs
        # rewritten, at the priority above GTK's USER.
        self.assertTrue(GTK4_PROBE_PROLOGUE.startswith("\nimport sys, time\n"))
        self.assertEqual(GTK4_PROBE_PROLOGUE.count("sys.exit(77)"), 2)
        self.assertIn(
            'Gtk.Settings.get_default().set_property("gtk-theme-name",'
            ' "Adwaita")',
            GTK4_PROBE_PROLOGUE,
        )
        self.assertIn('root / "gtk-4.0/gtk.css"', GTK4_PROBE_PROLOGUE)
        self.assertIn("b\"../assets/\", (root / \"assets\").as_uri()", GTK4_PROBE_PROLOGUE)
        self.assertIn("provider, 801)", GTK4_PROBE_PROLOGUE)

    def test_theme_loading_probe_suites_use_the_shared_prologue(self):
        # A suite that copy-pastes the bootstrap back into its child program
        # would drift from the shared constant; each of the six suites must
        # interpolate exactly once and keep no inline copy of the sheet
        # load.
        for name in _PROLOGUE_SUITES:
            source = (Path(__file__).parent / name).read_text()
            self.assertIn(
                "from support.gtk4_child_probe import GTK4_PROBE_PROLOGUE,"
                " run_gtk4_probe",
                source,
                name,
            )
            self.assertEqual(
                source.count("GTK4_PROBE_PROLOGUE"),
                2,
                f"{name} must interpolate the prologue exactly once",
            )
            self.assertNotIn('provider.load_from_data', source, name)

    def test_spin_probe_keeps_its_own_prologue(self):
        # The spin child never sets ``gtk-theme-name``; pin that it keeps
        # its own bootstrap so a future edit cannot silently adopt the
        # theme-name line (or lose its difference) unnoticed.
        source = (Path(__file__).parent / "test_gtk4_spin_probe.py").read_text()
        self.assertNotIn("GTK4_PROBE_PROLOGUE", source)
        self.assertIn("Gtk.init()", source)
        self.assertNotIn("gtk-theme-name", source)

    def test_every_gtk4_probe_suite_is_accounted_for(self):
        # Any new test_gtk4_*_probe.py suite must either interpolate the
        # shared prologue or (like spin_probe) justify its own bootstrap in
        # this test; an unaccounted suite fails here.
        suites = sorted(
            p.name
            for p in Path(__file__).parent.glob("test_gtk4_*_probe.py")
            if p.name != Path(__file__).name
        )
        self.assertEqual(
            suites,
            sorted(_PROLOGUE_SUITES + ("test_gtk4_spin_probe.py",)),
        )


if __name__ == "__main__":
    unittest.main()
