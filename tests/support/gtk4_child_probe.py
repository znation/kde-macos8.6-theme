"""Parent-side runner for the GTK 4 rendered pixel probes.

The seven ``tests/test_gtk4_*_probe.py`` suites render their widgets in a
child interpreter and assert on the pixels it samples. This module holds
the parent half they share: the child's environment (X11 backend, cairo
renderer), the theme directory it is handed as ``sys.argv[1]``, the
120-second bound, and the exit-77 skip. The child program itself stays in
the suite that owns it.

``tests/test_gtk_view_census.py`` runs its own GTK 4 children and reads
their result itself, so it does not use this runner (deliberately left).
"""

import os
import subprocess
import sys

from support.gtk4_sheet import THEME_DIR


def run_gtk4_probe(test, program):
    """Run the GTK 4 pixel *program* in a fresh child interpreter.

    The child receives ``THEME_DIR`` as ``sys.argv[1]``. Exit 77 skips
    *test* (introspection or an X11 display is missing); any other
    non-zero exit fails it with the child's output attached.
    """
    result = subprocess.run(
        [sys.executable, "-c", program, str(THEME_DIR)],
        env={**os.environ, "GDK_BACKEND": "x11", "GSK_RENDERER": "cairo"},
        capture_output=True,
        text=True,
        timeout=120,
    )
    if result.returncode == 77:
        test.skipTest("GTK 4 introspection or an X11 display is missing")
    test.assertEqual(result.returncode, 0, result.stdout + result.stderr)
