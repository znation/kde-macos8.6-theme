"""Tests for the splash client argv in tools/render_clients.py.

``splash_client`` is the one argv the splash render mode hands the session
script. Its docstring pins the shape: ``ksplashqml --test --nofork`` followed
by the session-local installed look-and-feel package directory. ``--test``
keeps the client's lifetime deterministic, and a bare theme id would resolve
outside the scratch data home, so both are pinned exactly here rather than
through the workflow's substring checks.
"""

from __future__ import annotations

import unittest

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from tools import render_clients  # noqa: E402
from tools.render_session import Session  # noqa: E402


class TestSplashClient(unittest.TestCase):
    def test_is_ksplashqml_in_test_mode_without_forking_on_the_installed_package(self):
        # The argv is exactly the program, its two flags, then the package
        # directory under the session's data home; any extra or reordered
        # element changes what the client paints or how long it lives.
        with Session.create() as session:
            argv = render_clients.splash_client(session)
            expected_package = (
                session.data / "plasma" / "look-and-feel" / "org.macos8.desktop"
            )
            self.assertEqual(
                ("ksplashqml", "--test", "--nofork", str(expected_package)),
                argv,
            )

    def test_names_the_package_directory_not_a_bare_theme_id(self):
        # The last argument must be an absolute path inside the session's
        # data home, so ksplashqml loads the scratch copy rather than
        # resolving the id against the user's own look-and-feel packages.
        with Session.create() as session:
            package = render_clients.splash_client(session)[-1]
            self.assertTrue(package.startswith(str(session.data) + "/"))
            self.assertTrue(package.endswith("/org.macos8.desktop"))
            self.assertNotEqual("org.macos8.desktop", package)


if __name__ == "__main__":
    unittest.main()
