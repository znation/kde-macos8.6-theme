"""Order pin for the `_uninstall` coordinator's eleven config handlers.

`tools/uninstall_diagnostics.py::diagnostics` promises "the diagnostics to
print, in the recipe's order": every handler's wording is pinned by its own
surface's suite, and pairs of lines inside one file or across the mirror
files are pinned there, but no test staged all eleven config surfaces in one
run, so a refactor that swapped two of the coordinator's handler calls would
keep every message printing while changing the order `make uninstall` prints
them in. This module stages every surface once, so each handler emits exactly
one message, and pins the full ordered list; it also re-pins the family-wide
contract that a diagnostic run edits nothing. ``main``'s own CLI surface has
its class here too: the recipe appends ``|| true``, so a renamed flag or a
swapped flag-to-handler mapping would deaden the scan silently -- the
recipe-level family tests stage the same shared id in every surface, which
makes a mapping swap invisible there.
"""

import os
import unittest
from unittest import mock

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.cli_fixtures import run_main
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


# The recipe's flag spellings, each with a distinct sentinel value so a test
# that captures them sees which named slot a value reached. The "main:"
# prefix marks every synthetic id; the real recipe's values all read
# org.macos8.desktop and the ColorScheme id derives from MacOS8, so
# mapping-swap bugs here would be invisible in value.
RECIPE_FLAGS = (
    ("--scheme-id", "main:scheme"),
    ("--icon-id", "main:icon"),
    ("--kvantum-id", "main:kvantum"),
    ("--gtk-id", "main:gtk"),
    ("--desktop-id", "main:desktop"),
    ("--lnf-id", "main:lnf"),
    ("--aurorae-id", "main:aurorae"),
    ("--css-marker", "/* main marker */"),
)

DIAGNOSTIC_PARAMS = (
    "config_home",
    "scheme_id",
    "icon_theme_id",
    "kvantum_id",
    "gtk_id",
    "dtheme_id",
    "lnf_id",
    "aurorae_id",
    "css_marker",
)


def capturing_diagnostics(captured):
    """Record ``diagnostics``'s positional slot names and return no messages."""

    def fake(*args):
        captured.update(dict(zip(DIAGNOSTIC_PARAMS, args)))
        return []

    return fake


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


class TestMainWiring(unittest.TestCase):
    """``main`` passes the recipe's flags into ``diagnostics`` by slot.

    ``make _uninstall`` runs this CLI with eight named flags and wraps the
    call in ``|| true``, so a flag the parser rejects is a scan that never
    prints, not an uninstall failure. No test may run that scan through the
    recipe with distinct values (every family stages org.macos8.desktop),
    and the order test above calls ``diagnostics`` directly, so only these
    tests bind the recipe's spellings to ``diagnostics``'s nine parameters.
    """

    def run_with(self, argv, captured, config_home=None):
        """Run ``main`` with *argv* and a patched ``diagnostics``."""
        if config_home is None:
            # no absolute root: the config home cannot resolve
            patched_env = {}
        else:
            patched_env = {
                "XDG_CONFIG_HOME": config_home,
                "HOME": os.path.join(os.path.dirname(config_home), "home"),
            }
        with mock.patch.dict(os.environ, patched_env, clear=True), \
                mock.patch.object(
                    uninstall_diagnostics, "diagnostics",
                    capturing_diagnostics(captured),
                ):
            return run_main(uninstall_diagnostics.main, "uninstall", argv)

    def test_the_recipe_flags_reach_their_named_slots(self):
        captured = {}
        config = str(make_tmp_dir(self))
        argv = [f"{flag}={value}" for flag, value in RECIPE_FLAGS]

        result = self.run_with(argv, captured, config_home=config)

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual("", result.stderr)
        self.assertEqual(config, captured.pop("config_home"))
        self.assertEqual(
            dict(
                scheme_id="main:scheme",
                icon_theme_id="main:icon",
                kvantum_id="main:kvantum",
                gtk_id="main:gtk",
                dtheme_id="main:desktop",
                lnf_id="main:lnf",
                aurorae_id="main:aurorae",
                css_marker="/* main marker */",
            ),
            captured,
            "each recipe flag must reach its own diagnostics parameter",
        )

    def test_every_recipe_flag_is_required_to_run_a_scan(self):
        for flag, value in RECIPE_FLAGS:
            with self.subTest(flag=flag):
                captured = {}
                config = str(make_tmp_dir(self))
                argv = [
                    f"{name}={item}"
                    for name, item in RECIPE_FLAGS
                    if name != flag
                ]

                result = self.run_with(argv, captured, config_home=config)

                self.assertEqual(2, result.returncode)
                self.assertIn(
                    "the following arguments are required", result.stderr
                )
                self.assertEqual({}, captured)

    def test_a_config_home_that_cannot_be_resolved_scans_nothing(self):
        captured = {}
        argv = [f"{flag}={value}" for flag, value in RECIPE_FLAGS]

        result = self.run_with(argv, captured)

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual("", result.stderr)
        self.assertEqual({}, captured)


if __name__ == "__main__":
    unittest.main()
