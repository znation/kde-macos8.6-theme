"""`make uninstall`'s diagnostics-only config reader bounds its reads.

The uninstall recipe's config scan must succeed on at most one read of each
file it inspects, so a corrupt or grown config file cannot exhaust memory
inside a reader whose contract is "always succeed" and "edit nothing".
Watched here: the reader applies the project's shared 1 MiB cap, a file at
the cap is still parsed whole, an over-cap file keeps its bytes and stays
silent like an unreadable one, the GTK marker scan shares that cap, and a
config holding bytes utf-8 cannot decode is kept as surrogate escapes so a
foreign file is never silently empty and never crashes the recipe.
"""

from unittest import mock

import io
import os
import unittest

from support import theme_install
from support.fifo_fixtures import fifo_swap_opener
from support.process_assertions import assert_succeeded
from support.tmp_dir import make_tmp_dir
from tools import containment, uninstall_config, uninstall_diagnostics
from tools.gtk_user_files import GTK4_CSS_MARKER

STYLE_RESET = "kwriteconfig6 --file kdeglobals --group KDE --key widgetStyle --delete"
STYLE_RULE_TAIL = (
    "([KDE] widgetStyle=kvantum) is still in {} after removal;"
)
# The published sheet's first line, spelled by the publisher: a fixture
# hand-copy would keep testing a spelling the apply side could rename.
CSS_MARKER = GTK4_CSS_MARKER
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
    """Write *body* to *path*, creating parent directories first."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as handle:
        handle.write(body)
    return path


class TestReaderCap(unittest.TestCase):
    def read_case(self, body):
        tmp = str(make_tmp_dir(self))
        path = write_bytes(os.path.join(tmp, "config", "kdeglobals"), body)
        return tmp, path, uninstall_config.read_text(path)

    def test_a_config_at_the_cap_is_read_whole(self):
        cap = uninstall_config._MAX_CONFIG_BYTES
        _tmp, _path, text = self.read_case(kdeglobals_bytes(cap, False))
        self.assertEqual(len(text), cap)

    def test_a_config_one_byte_past_the_cap_is_left_unread(self):
        cap = uninstall_config._MAX_CONFIG_BYTES
        _tmp, _path, text = self.read_case(kdeglobals_bytes(cap, True))
        self.assertIsNone(text)

    def test_an_over_cap_file_keeps_every_byte_it_had(self):
        cap = uninstall_config._MAX_CONFIG_BYTES
        tmp, path, _text = self.read_case(kdeglobals_bytes(cap, True))
        self.assertEqual(
            os.path.getsize(path), len(kdeglobals_bytes(cap, True))
        )
        self.assertTrue(os.path.exists(os.path.join(tmp, "config")))


class TestReaderFifo(unittest.TestCase):
    def test_a_fifo_swapped_in_for_a_regular_file_is_refused(self):
        # A regular file can become a FIFO between the path check and the
        # open (tests/test_apply_gtk_errors.py pins the same race for the
        # GTK settings reader). The patch set routes whichever open the
        # reader uses at the FIFO while os.path.isfile still reports a
        # regular file, through non-blocking descriptor opens, so a missing
        # descriptor check fails this assertion instead of blocking the run:
        # a reader that opens the pipe returns its held bytes instead of
        # refusing the swap, and a reader that refuses when only the path is
        # checked returns its None early and never sees the swap.
        if not hasattr(os, "mkfifo"):
            self.skipTest("os.mkfifo is not available on this platform")
        tmp = str(make_tmp_dir(self))
        fifo = os.path.join(tmp, "config", "kdeglobals")
        os.makedirs(os.path.dirname(fifo), exist_ok=True)
        os.mkfifo(fifo)
        body = b"[KDE]\nwidgetStyle=kvantum\n"
        open_the_fifo = fifo_swap_opener(fifo)

        with mock.patch.object(os.path, "isfile", return_value=True), \
                mock.patch.object(
                    uninstall_config, "open", create=True,
                    return_value=io.BytesIO(body),
                ), \
                mock.patch.object(
                    containment.os, "open", side_effect=open_the_fifo,
                ):
            # A reader that opens the pipe and reads its held bytes does not
            # refuse the swap: it answers with selections instead of None.
            self.assertIsNone(uninstall_config.read_text(fifo))

    def test_a_fifo_at_the_path_is_silent_without_a_swap(self):
        # Calibration: an unswapped FIFO stays silent either way -- the
        # interrupted swap is the only case a missing descriptor check
        # blocks on.
        if not hasattr(os, "mkfifo"):
            self.skipTest("os.mkfifo is not available on this platform")
        tmp = str(make_tmp_dir(self))
        fifo = os.path.join(tmp, "config", "kdeglobals")
        os.makedirs(os.path.dirname(fifo), exist_ok=True)
        os.mkfifo(fifo)
        self.assertIsNone(uninstall_config.read_text(fifo))


class TestReaderMalformedBytes(unittest.TestCase):
    def read_case(self, body):
        tmp = str(make_tmp_dir(self))
        path = write_bytes(os.path.join(tmp, "config", "kdeglobals"), body)
        return tmp, path, uninstall_config.read_text(path)

    def test_an_unmappable_config_is_kept_whole_including_its_unmapped_bytes(self):
        # The decode sits after the cap check and outside the open's try, so
        # read_text's only promise against a decode error escaping this
        # always-succeeds reader is its non-strict decode. The docstring pins
        # the exact escape: unmappable bytes are kept as surrogate escapes, so
        # a foreign file is not silently empty (errors="ignore" would drop the
        # bytes) and never raise. The valid lines around them stay parseable.
        _tmp, _path, text = self.read_case(
            b"[KDE]\nwidgetStyle=kvantum\n\xff\xfe\n"
        )
        self.assertEqual(
            text, "[KDE]\nwidgetStyle=kvantum\n\udcff\udcfe\n"
        )
        self.assertEqual(
            uninstall_config.read_selected_values(
                text, {"KDE": ("widgetStyle",)}
            ),
            {("KDE", "widgetStyle"): "kvantum"},
        )


class TestRecipeCap(theme_install.UninstallRecipeTestCase):
    def test_a_config_at_the_cap_still_warns(self):
        cap = uninstall_config._MAX_CONFIG_BYTES
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
        cap = uninstall_config._MAX_CONFIG_BYTES
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


class TestRecipeMalformedBytes(theme_install.UninstallRecipeTestCase):
    def test_unmappable_bytes_still_name_the_reset_and_the_recipe_succeeds(self):
        # The unmapped bytes stand before the selection line, so a strict
        # decode would raise on the whole file and stop the scan before any
        # diagnostic; the non-strict decode keeps the reset visible.
        tmp = str(make_tmp_dir(self))
        config = os.path.join(tmp, "config")
        path = write_bytes(
            os.path.join(config, "kdeglobals"),
            b"\xff\xfe\n[KDE]\nwidgetStyle=kvantum\n",
        )
        with open(path, "rb") as handle:
            original = handle.read()

        result = self.uninstall_with_config(tmp, config)

        assert_succeeded(self, result)
        self.assertIn(STYLE_RULE_TAIL.format(path), result.stderr)
        self.assertIn(STYLE_RESET, result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        with open(path, "rb") as handle:
            self.assertEqual(original, handle.read())

    def test_an_unmapped_selection_value_is_never_reported_and_the_recipe_succeeds(self):
        # The escaped value cannot equal one of the ids, so the file stays
        # silent; the recipe must still succeed without a traceback.
        tmp = str(make_tmp_dir(self))
        config = os.path.join(tmp, "config")
        path = write_bytes(
            os.path.join(config, "kdeglobals"), b"[KDE]\nwidgetStyle=\xff\xfe\n"
        )

        result = self.uninstall_with_config(tmp, config)

        assert_succeeded(self, result)
        self.assertNotIn(STYLE_RULE_TAIL.format(path), result.stderr)
        self.assertNotIn(STYLE_RESET, result.stderr)
        self.assertNotIn("Traceback", result.stderr)


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
            uninstall_config._MAX_CONFIG_BYTES - len(CSS_MARKER) - 1
        )
        messages = self.messages_for((CSS_MARKER + unit + "\n").encode("utf-8"))
        self.assertEqual(len([m for m in messages if "gtk.css" in m]), 1)

    def test_a_marker_css_past_the_cap_is_not_reported(self):
        # One byte past the cap, the reader leaves the marker unseen.
        unit = "x" * (
            uninstall_config._MAX_CONFIG_BYTES - len(CSS_MARKER)
        )
        messages = self.messages_for((CSS_MARKER + unit + "\n").encode("utf-8"))
        self.assertEqual([m for m in messages if "gtk.css" in m], [])


if __name__ == "__main__":
    unittest.main()
