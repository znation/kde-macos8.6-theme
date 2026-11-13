"""Uninstall diagnostic tests for the `_uninstall` GTK settings latch.

`make apply-gtk` publishes `gtk-theme-name=org.macos8.desktop` under
`[Settings]` in `<config>/gtk-3.0/settings.ini` and
`<config>/gtk-4.0/settings.ini`; `make uninstall` removes the installed
sheets and warns when a settings file it removed the theme for still holds a
`gtk-theme-name=org.macos8.desktop` line. That hold latches on any
`[Settings]` line, as the recipe's original awk did (`found=1` set once and
never unset): a later duplicate key naming a foreign theme never unmarks an
earlier one of ours, and `tools/gtk_settings.py::-remove_theme_name` deletes
those duplicate-key spellings too. The ini lookup rule the module's other
diagnostics share is last-value-wins (``tests/support/kde_ini_corpus.py``
pins it); the latch is the GTK diagnostic's own contract, pinned here
through ``tools/uninstall_diagnostics.py``'s ``diagnostics``, through
``tools/uninstall_config.py``'s ``latched_match`` and through ``_uninstall``
itself, without editing any file.
"""

import os
import unittest

from support import theme_install
from support.theme_install import read_bytes, write_config_file
from support.process_assertions import assert_succeeded
from support.tmp_dir import make_config_home, make_tmp_dir
from tools import uninstall_config, uninstall_diagnostics
from tools.gtk_user_files import GTK4_CSS_MARKER

# The published sheet's first line, spelled by the publisher: a fixture
# hand-copy would keep testing a spelling the apply side could rename.
CSS_MARKER = GTK4_CSS_MARKER
GTK_ID = "org.macos8.desktop"
IDS = dict(
    scheme_id="MacOS8",
    icon_theme_id="org.macos8.desktop",
    kvantum_id="org.macos8.desktop",
    gtk_id=GTK_ID,
    dtheme_id="org.macos8.desktop",
    lnf_id="org.macos8.desktop",
    aurorae_id="org.macos8.desktop",
    css_marker=CSS_MARKER,
)

GTK_TAIL = (
    f"uninstall: a GTK selection still names {GTK_ID} after removal in"
)

OURS = f"gtk-theme-name={GTK_ID}"
FOREIGN = "gtk-theme-name=Adwaita"


def gtk_messages(config):
    """Return the messages `diagnostics` prints for *config* that name GTK."""
    return [m for m in uninstall_diagnostics.diagnostics(str(config), **IDS)
            if m.startswith(GTK_TAIL)]


def write_settings(config, name, body):
    """Write *body* as `<config>/<name>/settings.ini`; return its path."""
    return write_config_file(config, os.path.join(name, "settings.ini"), body)



class TestGtkSettingsLatch(unittest.TestCase):
    """The GTK diagnostic keeps an early `[Settings]` line of ours latched."""

    def test_latches_when_a_later_duplicate_names_a_foreign_theme(self):
        # The recipe's original awk set `found=1` on any matching line and
        # never unset it; `read_selected_values` keeps only the last value,
        # so reusing it here would go silent on ours first, foreign last --
        # the spelling a hand-edit or a foreign selector leaves behind.
        self.assertTrue(
            uninstall_config.latched_match(
                f"[Settings]\n{OURS}\n{FOREIGN}\n",
                "Settings",
                "gtk-theme-name",
                GTK_ID,
            )
        )

    def test_latches_when_a_later_section_holds_only_the_foreign_name(self):
        # The awk latched across a section switch too: only `[Settings]`
        # lines set `found`, so our line in the earlier section keeps the
        # file marked even when `[Other]` carries the foreign value.
        self.assertTrue(
            uninstall_config.latched_match(
                f"[Settings]\n{OURS}\n[Other]\n{FOREIGN}\n",
                "Settings",
                "gtk-theme-name",
                GTK_ID,
            )
        )

    def test_a_foreign_section_or_value_alone_never_latches(self):
        self.assertFalse(
            uninstall_config.latched_match(
                f"[Other]\n{OURS}\n", "Settings", "gtk-theme-name", GTK_ID
            )
        )
        self.assertFalse(
            uninstall_config.latched_match(
                f"[Settings]\n{FOREIGN}\n", "Settings", "gtk-theme-name", GTK_ID
            )
        )

    def test_last_duplicate_named_ours_still_warns(self):
        # Calibration: the last-value-wins spelling the corpus pins here
        # warns either way, so the latch only widens the marked set, never
        # silently narrows it.
        tmp = make_tmp_dir(self)
        path = write_settings(
            tmp, "gtk-3.0", f"[Settings]\n{FOREIGN}\n{OURS}\n"
        )
        self.assertEqual(len(gtk_messages(tmp)), 1)
        self.assertIn(path, gtk_messages(tmp)[0])

    def test_diagnostics_warn_with_ours_first_foreign_last(self):
        tmp = make_tmp_dir(self)
        path = write_settings(
            tmp, "gtk-4.0", f"[Settings]\n{OURS}\n{FOREIGN}\n"
        )
        messages = gtk_messages(tmp)
        self.assertEqual(len(messages), 1)
        self.assertIn(path, messages[0])
        self.assertIn("make remove-gtk", messages[0])

    def test_a_foreign_name_alone_stays_silent(self):
        tmp = make_tmp_dir(self)
        write_settings(tmp, "gtk-3.0", f"[Settings]\n{FOREIGN}\n")
        self.assertEqual(gtk_messages(tmp), [])


class TestGtkLatchThroughTheRecipe(unittest.TestCase):
    """`make _uninstall` keeps the warning on the latched file, untouched."""

    def test_warns_when_the_last_duplicate_names_a_foreign_theme(self):
        tmp, config = make_config_home(self)
        path = write_settings(
            config, "gtk-3.0", f"[Settings]\n{OURS}\n{FOREIGN}\n"
        )
        original = read_bytes(path)

        result = theme_install.uninstall_recipe(
            tmp,
            env=dict(os.environ, XDG_CONFIG_HOME=config),
        )

        assert_succeeded(self, result)
        self.assertIn(GTK_TAIL, result.stderr)
        self.assertIn(path, result.stderr)
        self.assertIn("make remove-gtk", result.stderr)
        self.assertEqual(original, read_bytes(path), "uninstall must not edit the ini")


if __name__ == "__main__":
    unittest.main()
