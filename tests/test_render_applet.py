"""Tests for tools/render_applet.py's KPackage applet-package preflight.

The finder's location rule is the XDG data-root layout KPackage searches:
``<root>/plasma/plasmoids/<id>/metadata.json``. These tests pass explicit
``data_roots`` lists so they never depend on this host's installed packages,
plus one derivation test over a synthetic environment mapping.
"""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from tools import render_applet  # noqa: E402

APPLET = "org.example.widget"
_RELATIVE = Path("plasma") / "plasmoids" / APPLET


def _make_root(directory: str, *, install: bool) -> Path:
    """Return a data root under *directory*, optionally holding the package."""
    root = Path(directory) / "data"
    package = root / _RELATIVE
    package.mkdir(parents=True)
    if install:
        (package / "metadata.json").write_text("{}", encoding="utf-8")
    return root


class TestAppletFinder(unittest.TestCase):
    """applet_problem against explicit data_roots lists."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="render-applet-test-")
        self.addCleanup(self.tmp.cleanup)
        self.homed_style = _make_root(self.tmp.name, install=True)
        self.dirs_style = _make_root(f"{self.tmp.name}/second", install=True)

    def test_found_via_an_xdg_data_home_style_root(self):
        self.assertIsNone(render_applet.applet_problem(APPLET, [self.homed_style]))

    def test_found_via_an_xdg_data_dirs_style_root(self):
        roots = [self.homed_style / "unused", self.dirs_style]
        self.assertIsNone(render_applet.applet_problem(APPLET, roots))

    def test_the_first_matching_root_wins(self):
        roots = [self.homed_style, self.dirs_style]
        self.assertIsNone(render_applet.applet_problem(APPLET, roots))

    def test_a_directory_without_metadata_json_still_misses(self):
        bare = _make_root(f"{self.tmp.name}/bare", install=False)
        problem = render_applet.applet_problem(APPLET, [bare])
        self.assertIsNotNone(problem)
        self.assertIn(APPLET, problem)

    def test_a_metadata_json_directory_does_not_match(self):
        root = Path(self.tmp.name) / "plain"
        package = root / _RELATIVE
        (package / "metadata.json").mkdir(parents=True)
        problem = render_applet.applet_problem(APPLET, [root])
        self.assertIsNotNone(problem)
        self.assertIn("plasma/plasmoids", problem)

    def test_the_problem_names_the_id_and_the_searched_roots(self):
        bare = _make_root(f"{self.tmp.name}/bare", install=False)
        other = Path(self.tmp.name) / "empty"
        other.mkdir()
        problem = render_applet.applet_problem(APPLET, [bare, other])
        self.assertIn(
            f"no plasma/plasmoids/{APPLET}/metadata.json under "
            f"{bare}, {other}",
            problem,
        )
        self.assertIn(APPLET, problem)

    def test_a_path_carrying_id_is_refused_without_a_search(self):
        for bad in ("a/b", "a\\b", "org.example\0widget", ""):
            with self.subTest(bad=bad):
                problem = render_applet.applet_problem(bad, [self.homed_style])
                self.assertIsNotNone(problem)
                self.assertIn("not a plasmoid id", problem)

    def test_a_non_str_id_is_a_type_error(self):
        with self.assertRaises(ValueError):
            render_applet.applet_problem(None)  # type: ignore[arg-type]


class TestDerivedRoots(unittest.TestCase):
    """data_roots_from_environment mirrors the XDG fallbacks."""

    def derived(self, **values):
        env = {
            key: value
            for key, value in os.environ.items()
            if key not in ("XDG_DATA_HOME", "XDG_DATA_DIRS")
        }
        env.update(values)
        return render_applet.data_roots_from_environment(env)

    def test_both_variables_unset_fall_back_to_the_xdg_defaults(self):
        self.assertEqual(
            [
                Path.home() / ".local" / "share",
                Path("/usr/local/share"),
                Path("/usr/share"),
            ],
            self.derived(),
        )

    def test_an_empty_data_home_falls_back_to_the_default_home(self):
        # The empty data-home value falls back to ~/.local/share while the
        # unset data-dirs value keeps its own default.
        self.assertEqual(
            [
                Path.home() / ".local" / "share",
                Path("/usr/local/share"),
                Path("/usr/share"),
            ],
            self.derived(XDG_DATA_HOME=""),
        )

    def test_an_empty_data_dirs_falls_back_to_the_default_dirs(self):
        self.assertEqual(
            [
                Path("/home/scratch"),
                Path("/usr/local/share"),
                Path("/usr/share"),
            ],
            self.derived(XDG_DATA_HOME="/home/scratch", XDG_DATA_DIRS=""),
        )

    def test_set_variables_are_taken_in_order_without_empty_entries(self):
        self.assertEqual(
            [Path("/one"), Path("/two"), Path("/three")],
            self.derived(XDG_DATA_HOME="/one", XDG_DATA_DIRS="/two::/three"),
        )


if __name__ == "__main__":
    unittest.main()
