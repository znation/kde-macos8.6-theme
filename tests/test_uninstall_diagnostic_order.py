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
from support.theme_install import read_bytes, write_file
from support.tmp_dir import make_config_home, make_tmp_dir
from tools import uninstall_diagnostics
from tools.gtk_user_files import GTK4_CSS_MARKER

IDS = dict(
    scheme_id="org.macos8.desktop",
    icon_theme_id="org.macos8.desktop",
    kvantum_id="org.macos8.desktop",
    gtk_id="org.macos8.desktop",
    dtheme_id="org.macos8.desktop",
    lnf_id="org.macos8.desktop",
    aurorae_id="org.macos8.desktop",
    css_marker=GTK4_CSS_MARKER,
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
        tmp, config = make_config_home(self)
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
        tmp, config = make_config_home(self)
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


# The coordinator's eleven handler calls, in the recipe order, with the
# `diagnostics` parameter each one forwards in argument order. Each handler
# sees the value of these slots and of nothing else; the DIAGNOSTIC_PARAMS
# tuple above lists the parameter names once, and these tuples are how the
# forwarding reads them per handler call.
HANDLER_SLOTS = (
    ("kdeglobals_messages", ("config_home", "scheme_id", "icon_theme_id", "lnf_id")),
    ("gtk_messages", ("config_home", "gtk_id", "css_marker")),
    ("kvantum_messages", ("config_home", "kvantum_id")),
    ("plasmarc_messages", ("config_home", "dtheme_id")),
    ("kcminputrc_messages", ("config_home", "icon_theme_id")),
    ("kwinrc_messages", ("config_home", "aurorae_id")),
    ("ksplashrc_messages", ("config_home", "lnf_id")),
    ("package_messages", ("config_home", "lnf_id")),
    ("kdedefaults_kdeglobals_messages", ("config_home", "icon_theme_id")),
    ("kdedefaults_kwinrc_messages", ("config_home", "aurorae_id")),
    ("kdedefaults_plasmarc_messages", ("config_home", "dtheme_id")),
)

# One distinct sentinel per forwarded parameter. Every id the recipe passes
# bar the color-scheme id reads org.macos8.desktop, so the family tests
# staging that value in every surface see nothing change when two id slots
# swap between handlers; forward the sentinels instead and each swapped slot
# yields no message at all.
FORWARD_SENTINELS = {
    "config_home": "forward:config",
    "scheme_id": "forward:scheme",
    "icon_theme_id": "forward:icon",
    "kvantum_id": "forward:kvantum",
    "gtk_id": "forward:gtk",
    "dtheme_id": "forward:desktop",
    "lnf_id": "forward:lnf",
    "aurorae_id": "forward:aurorae",
    "css_marker": "/* forward marker */",
}


class TestHandlerForwarding(unittest.TestCase):
    """`diagnostics` gives each handler exactly the slots it is documented for.

    The order test above pins the eleven calls only through each message's
    wording prefix, and every family suite stages the one shared theme value
    in every id, so swapping two same-valued id arguments between two handler
    calls (say, the pointer check reading the desktop-theme id) keeps every
    message printing with the values today; the same swap changes behavior
    the moment any recipe id stops matching its handler's surface. These
    tests patch all eleven handlers and pin each call's positional arguments
    against the forwarding tuples above, one distinct sentinel per
    parameter, so a swapped or dropped argument changes what a handler is
    called with.
    """

    def run_forwarding(self, calls):
        """Patch every handler to record its call and return no message."""

        def recorder(name):
            def record(*args):
                calls.append(name)
                return []

            return record

        with mock.patch.multiple(
            uninstall_diagnostics,
            **{name: mock.DEFAULT for name, _ in HANDLER_SLOTS},
        ) as mocks:
            for name, _ in HANDLER_SLOTS:
                mocks[name].side_effect = recorder(name)
            messages = uninstall_diagnostics.diagnostics(
                FORWARD_SENTINELS["config_home"],
                scheme_id=FORWARD_SENTINELS["scheme_id"],
                icon_theme_id=FORWARD_SENTINELS["icon_theme_id"],
                kvantum_id=FORWARD_SENTINELS["kvantum_id"],
                gtk_id=FORWARD_SENTINELS["gtk_id"],
                dtheme_id=FORWARD_SENTINELS["dtheme_id"],
                lnf_id=FORWARD_SENTINELS["lnf_id"],
                aurorae_id=FORWARD_SENTINELS["aurorae_id"],
                css_marker=FORWARD_SENTINELS["css_marker"],
            )
        return mocks, messages

    def test_each_handler_receives_exactly_its_own_slots(self):
        calls = []
        mocks, messages = self.run_forwarding(calls)

        self.assertEqual([], messages)
        self.assertEqual(
            [name for name, _ in HANDLER_SLOTS],
            calls,
            "each handler must be called exactly once, and in recipe order",
        )
        for name, slots in HANDLER_SLOTS:
            with self.subTest(handler=name):
                self.assertEqual(
                    {}, mocks[name].call_args.kwargs,
                    f"{name} must be called positionally",
                )
                expected = tuple(FORWARD_SENTINELS[slot] for slot in slots)
                self.assertEqual(
                    expected,
                    mocks[name].call_args.args,
                    f"{name} must receive exactly the {slots} values",
                )


if __name__ == "__main__":
    unittest.main()
