"""Makefile tests for the `_uninstall` diagnostics scan guard.

`make _uninstall` ends by running the config scan as one child
(``tools/uninstall_diagnostics.py``, the recipe tail the diagnostics suites
pin). The scan reads only a fixed set of paths under the resolved config
home, so the recipe first stats those paths and skips the child when none
exists: a skip saves the scan child's interpreter startup from every config
home without a surface file. The shell resolves the config home exactly the
way ``tools/uninstall_config.py``'s ``config_home`` does -- an absolute
``XDG_CONFIG_HOME`` wins, an unset, empty or relative one falls back to
``$HOME/.config``, and with neither the scan runs nowhere -- so these tests
pin those boundaries the diagnostics suites (which always supply a config
home whose file exists) leave open, through the real diagnostics wordings
when a selection still matches. The run/skip sides also use an interpreter
stub passed through ``PYTHON`` (a documented override), so a test can
observe the scan spawning -- the stub echoes one marker per spawn -- without
the scan reading anything. Because every handler read must stay reachable
through the guard, one test parses the handler modules'
``os.path.join(config_home, ...)`` calls and compares them against the
guard's config-file list, so a new diagnostic surface that forgets to join
the guard fails here instead of silently going unread.
"""

import os
import re
import unittest

from support import repo_root
from support import theme_install
from support.process_assertions import assert_succeeded
from support.tmp_dir import make_tmp_dir

SCAN_MARKER = "uninstall diagnostics scan child ran: the guard let it through"


def widget_style_rule(path):
    """The kdedefaults mirror's widget-style diagnostic (wording contract)."""
    return (
        "uninstall: the widget-style selection the look-and-feel apply left "
        "in defaults ([KDE] widgetStyle=kvantum) is still in " + path
    )


def write_file(path, body):
    """Write *body* at *path*, creating parent directories as needed."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as handle:
        handle.write(body.encode("utf-8"))
    return path


def scan_stub(case):
    """Write an executable stub that loudly reports being spawned."""
    tmp = make_tmp_dir(case)
    stub = write_file(
        os.path.join(tmp, "scan-stub"),
        f"#!/bin/sh\necho {SCAN_MARKER} >&2\nexit 0\n",
    )
    os.chmod(stub, 0o755)
    return tmp, stub


class TestScanGuardRunsTheChildWhenASurfaceExists(unittest.TestCase):
    """A config path in the guarded list still reaches the scan, once."""

    def test_a_surface_file_spawns_the_scan_child_exactly_once(self):
        tmp, stub = scan_stub(self)
        config = os.path.join(tmp, "config")
        write_file(os.path.join(config, "kdedefaults", "kdeglobals"), "[KDE]\n")
        env = theme_install.make_env("PYTHON")
        env["XDG_CONFIG_HOME"] = config

        result = theme_install.uninstall_recipe(
            tmp, extra=[f"PYTHON={stub}"], env=env
        )

        assert_succeeded(self, result)
        # Once per run, not once per stat'ed path: the scan is one child even
        # when several guarded paths exist.
        self.assertEqual(1, result.stderr.count(SCAN_MARKER))

    def test_the_fallback_config_home_still_reaches_the_scan(self):
        # `config_home` falls back to `$HOME/.config` when XDG_CONFIG_HOME is
        # unset, empty or relative; the fallback home here holds a surface
        # file with a matching selection, so the scan must run against it
        # exactly as it did without the guard.
        tmp = make_tmp_dir(self)
        config = os.path.join(tmp, "home", ".config")
        kdedefaults = os.path.join(config, "kdedefaults", "kdeglobals")
        write_file(kdedefaults, "[KDE]\nwidgetStyle=kvantum\n")
        env = dict(os.environ, XDG_CONFIG_HOME="relative-not-a-path")
        env["HOME"] = os.path.join(tmp, "home")

        result = theme_install.uninstall_recipe(tmp, env=env)

        assert_succeeded(self, result)
        self.assertIn(widget_style_rule(kdedefaults), result.stderr)

    def test_an_absolute_xdg_config_home_wins_over_home(self):
        # An absolute XDG_CONFIG_HOME bounds the scan even when `$HOME`'s
        # config home holds a matching surface: the guard must not fall back
        # to HOME and read that file.
        tmp = make_tmp_dir(self)
        kdedefaults = os.path.join(
            tmp, "home", ".config", "kdedefaults", "kdeglobals"
        )
        write_file(kdedefaults, "[KDE]\nwidgetStyle=kvantum\n")
        env = dict(os.environ, XDG_CONFIG_HOME=os.path.join(tmp, "config"))

        result = theme_install.uninstall_recipe(tmp, env=env)

        assert_succeeded(self, result)
        self.assertNotIn(widget_style_rule(kdedefaults), result.stderr)


class TestScanGuardSkipsTheChildWhenNoSurfaceExists(unittest.TestCase):
    """No guarded path under the resolved home means no scan child."""

    def test_an_empty_config_home_skips_the_scan_child(self):
        tmp, stub = scan_stub(self)
        env = theme_install.make_env("PYTHON")
        env["XDG_CONFIG_HOME"] = os.path.join(tmp, "config")

        result = theme_install.uninstall_recipe(
            tmp, extra=[f"PYTHON={stub}"], env=env
        )

        assert_succeeded(self, result)
        self.assertNotIn(SCAN_MARKER, result.stderr)

    def test_no_absolute_config_home_skips_the_scan_child(self):
        # With neither an absolute XDG value nor an absolute HOME the scan
        # resolved nowhere before the guard; now the child is not spawned at
        # all and the recipe still succeeds.
        tmp, _ = scan_stub(self)
        env = theme_install.make_env("PYTHON")
        env.pop("XDG_CONFIG_HOME", None)
        env.pop("HOME", None)

        result = theme_install.uninstall_recipe(tmp, env=env)

        assert_succeeded(self, result)
        self.assertNotIn(SCAN_MARKER, result.stderr)


def handler_surface_paths():
    """The file paths the diagnostic handlers read under *config_home*.

    Derived from the handler modules' own ``os.path.join(config_home, ...)``
    calls, so a new handler surface appears here without editing this test.
    """
    paths = set()
    pattern = re.compile(
        r"os\.path\.join\(config_home, ((?:\"[^\"]+\"(?:, )?)+)\)"
    )
    for source_path in (
        os.path.join(repo_root.ROOT, "tools", "uninstall_live_diagnostics.py"),
        os.path.join(
            repo_root.ROOT, "tools", "uninstall_defaults_diagnostics.py"
        ),
    ):
        with open(source_path) as handle:
            source = handle.read()
        for match in pattern.finditer(source):
            parts = re.findall(r"\"([^\"]+)\"", match.group(1))
            paths.add(os.path.join(*parts))
    return paths


class TestGuardListsEveryHandlerSurface(unittest.TestCase):
    """The guard's stat list names every path the handlers read."""

    def test_the_guard_list_and_the_handler_reads_coincide(self):
        makefile_path = os.path.join(repo_root.ROOT, "Makefile")
        with open(makefile_path) as handle:
            makefile = handle.read()
        guard_paths = set(re.findall(r"\"\$\$cfg/([^\"]+)\"", makefile))
        self.assertGreater(
            len(guard_paths),
            0,
            "_uninstall's guard rewording lost the $$cfg paths",
        )
        self.assertEqual(handler_surface_paths(), guard_paths)


if __name__ == "__main__":
    unittest.main()
