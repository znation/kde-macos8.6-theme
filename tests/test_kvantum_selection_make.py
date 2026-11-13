"""Makefile tests for the ``remove-kvantum`` target and uninstall reset.

The recipes run under the real ``make`` with a throwaway ``DESTDIR`` and
config home: the tool target clears a temp selection, and `_uninstall`'s
Kvantum diagnostic prints the ``make remove-kvantum`` reset when the kept
selection still names our id, without editing the file. The tool's own
behaviour is pinned in ``tests/test_remove_kvantum.py``; the color scheme's
and GTK's warning behaviour keeps its own suites' pins, which this module
must not change.
"""

from __future__ import annotations

import os
import unittest

from support import theme_install
from support.theme_install import (
    assert_uninstall_diagnostics,
    read_bytes,
    write_config_file,
)
from support.config_home_cases import assert_home_fallback
from support.process_assertions import assert_succeeded
from support.tmp_dir import make_config_home

KVANTUM_ID = "org.macos8.desktop"
DIAGNOSTIC = (
    f"uninstall: the Kvantum selection still names {KVANTUM_ID} after removal in"
)
RESET = "Clear it with: make remove-kvantum"


def write_selection(config, body):
    """Write *body* as `<config>/Kvantum/kvantum.kvconfig`; return its path."""
    return write_config_file(config, os.path.join("Kvantum", "kvantum.kvconfig"), body)



class TestMakeTarget(unittest.TestCase):
    """`make remove-kvantum` runs the tool against the caller's config home."""

    def test_dry_run_prints_the_script(self):
        result = theme_install.run_make(
            ["-n", "remove-kvantum"], env=theme_install.make_env()
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("tools/kvantum_selection.py", result.stdout)

    def test_help_lists_the_target(self):
        result = theme_install.run_make(["help"], env=theme_install.make_env())
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertRegex(result.stdout, r"  remove-kvantum .*Kvantum")

    def test_the_target_clears_a_selection_in_the_temp_config_home(self):
        tmp, config = make_config_home(self)
        path = write_selection(config, "[General]\nBuilder=kvantummanager\ntheme=org.macos8.desktop\n")

        result = theme_install.run_make(
            ["remove-kvantum"], env=dict(os.environ, XDG_CONFIG_HOME=config)
        )

        assert_succeeded(self, result)
        self.assertEqual(
            b"[General]\nBuilder=kvantummanager\n", read_bytes(path)
        )


class TestUninstallDiagnostic(theme_install.UninstallRecipeTestCase):
    """`make _uninstall` names the reset when the selection still names ours."""

    def test_warns_and_names_the_reset_for_a_kept_selection(self):
        tmp, config = make_config_home(self)
        path = write_selection(
            config, "[General]\ntheme=" + KVANTUM_ID + "\n"
        )
        # A diagnostic must not edit the user's kvconfig.
        assert_uninstall_diagnostics(
            self, tmp, config, DIAGNOSTIC, RESET, unchanged=path
        )

    def test_not_warned_for_a_foreign_selection(self):
        tmp, config = make_config_home(self)
        write_selection(config, "[General]\ntheme=KvBreezeDark\n")

        assert_uninstall_diagnostics(self, tmp, config, absent=DIAGNOSTIC)

    def test_not_warned_when_a_later_foreign_value_overrides_ours(self):
        tmp, config = make_config_home(self)
        write_selection(
            config,
            "[General]\ntheme=org.macos8.desktop\ntheme=KvBreezeDark\n",
        )

        assert_uninstall_diagnostics(self, tmp, config, absent=DIAGNOSTIC)

    def test_warned_when_a_later_duplicate_names_ours(self):
        # KDE's config reader takes a later key's value, so the diagnostic
        # must read the same way the color-scheme one does.
        tmp, config = make_config_home(self)
        write_selection(
            config,
            "[General]\ntheme=KvBreezeDark\ntheme=org.macos8.desktop\n",
        )

        assert_uninstall_diagnostics(self, tmp, config, DIAGNOSTIC, RESET)

    def test_reads_the_home_fallback_when_the_config_variable_is_unset(self):
        assert_home_fallback(
            self,
            lambda config: write_selection(
                config, "[General]\ntheme=" + KVANTUM_ID + "\n"
            ),
            lambda path: RESET,
        )

    def test_silent_when_there_is_no_kvconfig(self):
        tmp, config = make_config_home(self)
        os.makedirs(config, exist_ok=True)

        assert_uninstall_diagnostics(self, tmp, config, absent=DIAGNOSTIC)


if __name__ == "__main__":
    unittest.main()
