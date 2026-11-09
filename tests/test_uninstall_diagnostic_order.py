"""Order pin for the `_uninstall` coordinator's eleven config handlers.

`tools/uninstall_diagnostics.py::diagnostics` promises "the diagnostics to
print, in the recipe's order": every handler's wording is pinned by its own
surface's suite, and pairs of lines inside one file or across the mirror
files are pinned there, but no test staged all eleven config surfaces in one
run, so a refactor that swapped two of the coordinator's handler calls would
keep every message printing while changing the order `make uninstall` prints
them in. This module stages every surface once, so each handler emits exactly
one message, and pins the full ordered list; it also re-pins the family-wide
contract that a diagnostic run edits nothing.
"""

import os
import unittest

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.tmp_dir import make_tmp_dir
from tools import uninstall_diagnostics

IDS = dict(
    scheme_id="org.macos8.desktop",
    icon_theme_id="org.macos8.desktop",
    kvantum_id="org.macos8.desktop",
    gtk_id="org.macos8.desktop",
    dtheme_id="org.macos8.desktop",
    lnf_id="org.macos8.desktop",
    aurorae_id="org.macos8.desktop",
    css_marker="/* org.macos8.desktop GTK 4 user CSS */",
)

# One prefix per handler, in the recipe order the coordinator documents. The
# full wordings are the contract their own suites pin; the prefixes here only
# tell the eleven handlers apart.
ORDER = (
    "uninstall: the global theme the look-and-feel apply step selected",
    "uninstall: a GTK selection still names",
    "uninstall: the Kvantum selection still names",
    "uninstall: the desktop theme selection still names",
    "uninstall: the pointer selection still names",
    "uninstall: the window-decoration selection still names",
    "uninstall: the splash selection",
    "uninstall: the look-and-feel package default",
    "uninstall: the icon-theme selection the look-and-feel apply left in defaults",
    "uninstall: the window-decoration selection [library=org.kde.kwin.aurorae",
    "uninstall: the desktop theme selection the look-and-feel apply left in defaults",
)

OURS = "org.macos8.desktop"


def write_file(path, body):
    """Write *body* at *path*, creating parent directories as needed."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as handle:
        handle.write(body.encode("utf-8") if isinstance(body, str) else body)
    return path


def stage_every_surface(config):
    """Stage one still-standing selection per handler; return the paths."""
    return (
        write_file(
            os.path.join(config, "kdeglobals"),
            "[KDE]\nLookAndFeelPackage=" + OURS + "\n",
        ),
        write_file(
            os.path.join(config, "gtk-3.0", "settings.ini"),
            "[Settings]\ngtk-theme-name=" + OURS + "\n",
        ),
        write_file(
            os.path.join(config, "Kvantum", "kvantum.kvconfig"),
            "[General]\ntheme=" + OURS + "\n",
        ),
        write_file(os.path.join(config, "plasmarc"), "[Theme]\nname=" + OURS + "\n"),
        write_file(
            os.path.join(config, "kcminputrc"), "[Mouse]\ncursorTheme=" + OURS + "\n"
        ),
        write_file(
            os.path.join(config, "kwinrc"),
            "[org.kde.kdecoration2]\ntheme=" + OURS + "\n",
        ),
        write_file(
            os.path.join(config, "kdedefaults", "ksplashrc"),
            "[KSplash]\nTheme=" + OURS + "\n",
        ),
        write_file(os.path.join(config, "kdedefaults", "package"), OURS),
        write_file(
            os.path.join(config, "kdedefaults", "kdeglobals"),
            "[Icons]\nTheme=" + OURS + "\n",
        ),
        write_file(
            os.path.join(config, "kdedefaults", "kwinrc"),
            "[org.kde.kdecoration2]\nlibrary=org.kde.kwin.aurorae\ntheme=" + OURS + "\n",
        ),
        write_file(
            os.path.join(config, "kdedefaults", "plasmarc"),
            "[Theme]\nname=" + OURS + "\n",
        ),
    )


def read_bytes(path):
    with open(path, "rb") as handle:
        return handle.read()


class TestUninstallDiagnosticOrder(unittest.TestCase):
    """`diagnostics` prints one line per handler, in the recipe's order."""

    def test_the_eleven_handlers_print_in_the_recipe_order(self):
        tmp = str(make_tmp_dir(self))
        config = os.path.join(tmp, "config")
        stage_every_surface(config)

        messages = uninstall_diagnostics.diagnostics(config, **IDS)

        self.assertEqual(
            len(messages),
            len(ORDER),
            f"expected one message per handler, got: {messages}",
        )
        positions = []
        for prefix in ORDER:
            matches = [m for m in messages if m.startswith(prefix)]
            self.assertEqual(
                len(matches), 1, f"expected exactly one {prefix!r} line"
            )
            positions.append(messages.index(matches[0]))
        self.assertEqual(positions, sorted(positions))

    def test_a_full_scan_edits_no_staged_file(self):
        tmp = str(make_tmp_dir(self))
        config = os.path.join(tmp, "config")
        paths = stage_every_surface(config)
        original = {path: read_bytes(path) for path in paths}

        uninstall_diagnostics.diagnostics(config, **IDS)

        for path in paths:
            with self.subTest(path=path):
                self.assertEqual(original[path], read_bytes(path))


if __name__ == "__main__":
    unittest.main()
