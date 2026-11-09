"""The ``uninstall`` diagnostics scan prints contributor text escaped.

The scan's messages name the config-file paths it read and the selection ids
it matched. The path comes from the environment (``XDG_CONFIG_HOME``, or the
``$HOME/.config`` fallback) and the ids comes from the command line, both
contributor-supplied, so the diagnostics contract requires the scan to route
each printed message through ``tools.terminal.escape_controls``: a control
character in the config-home's own name must reach the operator escaped, not
driving the terminal. The ``make uninstall`` recipe guards these values at
make parse time, but the scan child is directly runnable
(``python3 tools/uninstall_diagnostics.py``) and its own entry point owns
what it prints, so these tests exercise ``main`` through the supported
direct-run path.
"""

import os
import subprocess
import sys
import unittest

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.cli_fixtures import run_main
from support.theme_install import write_file
from support.tmp_dir import make_tmp_dir
from tools import uninstall_diagnostics

TOOL = os.path.join(repo_root.ROOT, "tools", "uninstall_diagnostics.py")

COMMON_IDS = [
    "--scheme-id", "TestScheme",
    "--icon-id", "org.macos8.desktop",
    "--kvantum-id", "org.macos8.desktop",
    "--gtk-id", "org.macos8.desktop",
    "--desktop-id", "org.macos8.desktop",
    "--lnf-id", "org.macos8.desktop",
    "--aurorae-id", "org.macos8.desktop",
    "--css-marker", "org.macos8.desktop",
]


def _scan_env(config_home: str) -> dict[str, str]:
    env = {
        key: value
        for key, value in os.environ.items()
        if key not in ("XDG_CONFIG_HOME", "HOME")
    }
    env["XDG_CONFIG_HOME"] = config_home
    env["HOME"] = config_home
    return env


def _run(config_home: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, TOOL, *COMMON_IDS],
        env=_scan_env(config_home),
        capture_output=True,
        text=True,
        cwd=repo_root.ROOT,
    )


class TestScanEscapesAControlByteInTheConfigHomeName(unittest.TestCase):
    """A hostile config-home name cannot drive the operator's terminal."""

    def test_a_matching_selection_in_a_hostile_named_home_is_escaped(self):
        # ESC is legal in a directory name; a config home that carries it
        # still reaches the scan (xdg_homes accepts any absolute name), so
        # the scheme diagnostic for a matching selection embeds those bytes.
        # Escaped, the message shows the ESC literally instead of sending it.
        tmp = make_tmp_dir(self)
        config = os.path.join(str(tmp), "config\u001b")
        write_file(
            os.path.join(config, "kdeglobals"), "[General]\nColorScheme=TestScheme\n"
        )

        result = _run(config)

        self.assertEqual(0, result.returncode)
        self.assertIn(
            "uninstall: color scheme TestScheme is still selected in",
            result.stderr,
        )
        self.assertNotIn("\u001b", result.stderr)
        self.assertIn(r"\u001b", result.stderr)


class TestScanEscapesAControlByteInAnUnrecognizedArgument(unittest.TestCase):
    """argparse's own diagnostics escape the raw argv they echo.

    ``unrecognized arguments: ...`` is formatted from the command line as
    given, so a control byte in a flag the scan does not know would print
    raw through argparse itself. The scan parses with the shared
    ``EscapingArgumentParser`` like every other CLI here; the parse error
    fires before any environment read, so this test calls ``main``
    in-process with no staged config.
    """

    def test_an_unknown_flag_carrying_esc_prints_escaped(self):
        result = run_main(
            uninstall_diagnostics.main,
            "uninstall_diagnostics.py",
            [*COMMON_IDS, "--be\u001bad"],
        )

        self.assertEqual(2, result.returncode)
        self.assertIn("error: unrecognized arguments:", result.stderr)
        self.assertNotIn("\u001b", result.stderr)
        self.assertIn(r"\u001b", result.stderr)


class TestScanPrintsABenignConfigHomeUnchanged(unittest.TestCase):
    """Escaping must not reword a diagnostic whose text is all printable."""

    def test_a_printable_path_prints_byte_for_byte(self):
        tmp = make_tmp_dir(self)
        config = os.path.join(str(tmp), "config")
        write_file(
            os.path.join(config, "kdeglobals"), "[General]\nColorScheme=TestScheme\n"
        )

        result = _run(config)

        self.assertEqual(0, result.returncode)
        self.assertIn(
            f"uninstall: color scheme TestScheme is still selected in "
            f"""{os.path.join(config, "kdeglobals")} after removal;""",  # noqa: E501
            result.stderr,
        )
        self.assertNotIn("\\", result.stderr)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
