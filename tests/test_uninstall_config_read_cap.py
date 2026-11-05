"""`make uninstall`'s diagnostics-only config reader bounds its reads.

The uninstall recipe's config scan must succeed on at most one read of each
file it inspects, so a corrupt or grown config file cannot exhaust memory
inside a reader whose contract is "always succeed" and "edit nothing".
Watched here: the reader applies the project's shared 1 MiB cap, a file at
the cap is still parsed whole, an over-cap file keeps its bytes and stays
silent like an unreadable one, and the GTK marker scan shares that cap.
"""

import os
import unittest

from support import theme_install
from support.process_assertions import assert_succeeded
from support.tmp_dir import make_tmp_dir
from tools import uninstall_diagnostics

STYLE_RESET = "kwriteconfig6 --file kdeglobals --group KDE --key widgetStyle --delete"
STYLE_RULE_TAIL = (
    "([KDE] widgetStyle=kvantum) is still in {} after removal;"
)
CSS_MARKER = "/* org.macos8.desktop GTK 4 user CSS */"
# Same ids the family tests publish; the diagnostics compare these strings.
IDS = dict(
    scheme_id="MacOS8",
    icon_theme_id="org.macos8.desktop",
    kvantum_id="org.macos8.desktop",
    gtk_id="org.macos8.desktop",
    dtheme_id="org.macos8.desktop",
    lnf_id="org.macos8.desktop",
    aurorae_id="org.macos8.desktop",
    css_marker=CSS_MARKER,
)


def kdeglobals_bytes(cap, one_past):
    """Return a kdeglobals body of exactly *cap* bytes (+1 when *one_past*).

    The widget-style selection stands on the first lines, so a prefix read
    would still find it: only the cap, and never the parse, decides silence.
    """
    head = b"[KDE]\nwidgetStyle=kvantum\n"
    pad = cap - len(head) + (1 if one_past else 0)
    return head + b"\n" * pad


def write_bytes(path, body):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as handle:
        handle.write(body)
    return path


class TestReaderCap(unittest.TestCase):
    def read_case(self, body):
        tmp = str(make_tmp_dir(self))
        path = write_bytes(os.path.join(tmp, "config", "kdeglobals"), body)
        return tmp, path, uninstall_diagnostics.read_text(path)

    def test_a_config_at_the_cap_is_read_whole(self):
        cap = uninstall_diagnostics._MAX_CONFIG_BYTES
        _tmp, _path, text = self.read_case(kdeglobals_bytes(cap, False))
        self.assertEqual(len(text), cap)

    def test_a_config_one_byte_past_the_cap_is_left_unread(self):
        cap = uninstall_diagnostics._MAX_CONFIG_BYTES
        _tmp, _path, text = self.read_case(kdeglobals_bytes(cap, True))
        self.assertIsNone(text)

    def test_an_over_cap_file_keeps_every_byte_it_had(self):
        cap = uninstall_diagnostics._MAX_CONFIG_BYTES
        tmp, path, _text = self.read_case(kdeglobals_bytes(cap, True))
        self.assertEqual(
            os.path.getsize(path), len(kdeglobals_bytes(cap, True))
        )
        self.assertTrue(os.path.exists(os.path.join(tmp, "config")))


class TestRecipeCap(unittest.TestCase):
    def uninstall_with_config(self, tmp, config):
        return theme_install.uninstall_recipe(
            tmp,
            extra=(),
            env=dict(os.environ, XDG_CONFIG_HOME=config),
        )

    def test_a_config_at_the_cap_still_warns(self):
        cap = uninstall_diagnostics._MAX_CONFIG_BYTES
        tmp = str(make_tmp_dir(self))
        config = os.path.join(tmp, "config")
        path = write_bytes(
            os.path.join(config, "kdeglobals"), kdeglobals_bytes(cap, False)
        )
        with open(path, "rb") as handle:
            original = handle.read()

        result = self.uninstall_with_config(tmp, config)

        assert_succeeded(self, result)
        self.assertIn(STYLE_RULE_TAIL.format(path), result.stderr)
        self.assertIn(STYLE_RESET, result.stderr)
        with open(path, "rb") as handle:
            self.assertEqual(original, handle.read())

    def test_an_over_cap_config_stays_silent_and_the_recipe_succeeds(self):
        cap = uninstall_diagnostics._MAX_CONFIG_BYTES
        tmp = str(make_tmp_dir(self))
        config = os.path.join(tmp, "config")
        path = write_bytes(
            os.path.join(config, "kdeglobals"), kdeglobals_bytes(cap, True)
        )
        with open(path, "rb") as handle:
            original = handle.read()

        result = self.uninstall_with_config(tmp, config)

        assert_succeeded(self, result)
        # The reader must not report on a file it did not read whole, and the
        # bounded read holds without a traceback escaping the recipe.
        self.assertNotIn(STYLE_RULE_TAIL.format(path), result.stderr)
        self.assertNotIn(STYLE_RESET, result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        with open(path, "rb") as handle:
            self.assertEqual(original, handle.read())


class TestGtkMarkerSharesTheCap(unittest.TestCase):
    def messages_for(self, css_bytes):
        tmp = str(make_tmp_dir(self))
        config = os.path.join(tmp, "config")
        write_bytes(os.path.join(config, "gtk-4.0", "gtk.css"), css_bytes)
        return uninstall_diagnostics.diagnostics(config, **IDS)

    def test_a_marker_css_at_the_cap_names_the_reset(self):
        # The trailing newline is one of the cap's bytes: the file stays at
        # exactly _MAX_CONFIG_BYTES and must be read and named.
        unit = "x" * (
            uninstall_diagnostics._MAX_CONFIG_BYTES - len(CSS_MARKER) - 1
        )
        messages = self.messages_for((CSS_MARKER + unit + "\n").encode("utf-8"))
        self.assertEqual(len([m for m in messages if "gtk.css" in m]), 1)

    def test_a_marker_css_past_the_cap_is_not_reported(self):
        # One byte past the cap, the reader leaves the marker unseen.
        unit = "x" * (
            uninstall_diagnostics._MAX_CONFIG_BYTES - len(CSS_MARKER)
        )
        messages = self.messages_for((CSS_MARKER + unit + "\n").encode("utf-8"))
        self.assertEqual([m for m in messages if "gtk.css" in m], [])


if __name__ == "__main__":
    unittest.main()
