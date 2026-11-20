"""Unit tests for the live Kvantum uninstall diagnostic.

`kvantum_messages` in `tools/uninstall_live_diagnostics.py` names the Kvantum reset
(`make remove-kvantum`) when the live `Kvantum/kvantum.kvconfig` still selects
our theme under `[General] theme=`. It reads through the shared scanner, so a
selection only counts inside the `[General]` group, the last `theme=` line in
that group decides, and a missing file stays silent. The Makefile-level suite
for the same handler lives in `tests/test_uninstall_diagnostic_order.py`; these
cases pin the handler's own branches directly.
"""

import os
import unittest

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.tmp_dir import make_tmp_dir
from support.theme_install import write_file
from tools import uninstall_live_diagnostics

KVANTUM_ID = "org.macos8.desktop"


class TestKvantumMessages(unittest.TestCase):
    """`kvantum_messages` warns only for a live `[General] theme=` naming our id."""

    def _config_with(self, body):
        """Write *body* as the live kvconfig under a fresh config home; return (config, path)."""
        config = str(make_tmp_dir(self))
        path = write_file(os.path.join(config, "Kvantum", "kvantum.kvconfig"), body)
        return config, path

    def test_warns_and_names_the_reset_for_a_kept_selection(self):
        config, path = self._config_with("[General]\ntheme=" + KVANTUM_ID + "\n")

        messages = uninstall_live_diagnostics.kvantum_messages(config, KVANTUM_ID)

        self.assertEqual(1, len(messages))
        self.assertIn("the Kvantum selection still names " + KVANTUM_ID, messages[0])
        self.assertIn(" in " + path + ";", messages[0])
        self.assertTrue(messages[0].endswith("Clear it with: make remove-kvantum"))

    def test_warns_when_spacing_around_the_key_only_trims_to_ours(self):
        config, _ = self._config_with("[General]\n  theme = " + KVANTUM_ID + "  \n")

        messages = uninstall_live_diagnostics.kvantum_messages(config, KVANTUM_ID)

        self.assertEqual(1, len(messages))

    def test_not_warned_for_a_foreign_theme(self):
        config, _ = self._config_with("[General]\ntheme=KvantumAlt\n")

        self.assertEqual(
            [], uninstall_live_diagnostics.kvantum_messages(config, KVANTUM_ID)
        )

    def test_not_warned_for_an_empty_theme_value(self):
        config, _ = self._config_with("[General]\ntheme=\n")

        self.assertEqual(
            [], uninstall_live_diagnostics.kvantum_messages(config, KVANTUM_ID)
        )

    def test_not_warned_when_the_theme_key_sits_in_another_group(self):
        config, _ = self._config_with(
            "[Other]\ntheme=" + KVANTUM_ID + "\n[General]\nreduceWindowOpacity=0\n"
        )

        self.assertEqual(
            [], uninstall_live_diagnostics.kvantum_messages(config, KVANTUM_ID)
        )

    def test_not_warned_when_a_later_foreign_value_overrides_ours(self):
        config, _ = self._config_with(
            "[General]\ntheme=" + KVANTUM_ID + "\ntheme=KvantumAlt\n"
        )

        self.assertEqual(
            [], uninstall_live_diagnostics.kvantum_messages(config, KVANTUM_ID)
        )

    def test_warned_when_a_later_duplicate_names_ours(self):
        config, _ = self._config_with(
            "[General]\ntheme=KvantumAlt\ntheme=" + KVANTUM_ID + "\n"
        )

        messages = uninstall_live_diagnostics.kvantum_messages(config, KVANTUM_ID)

        self.assertEqual(1, len(messages))

    def test_silent_when_there_is_no_kvantum_config(self):
        config = str(make_tmp_dir(self))

        self.assertEqual(
            [], uninstall_live_diagnostics.kvantum_messages(config, KVANTUM_ID)
        )


if __name__ == "__main__":
    unittest.main()
