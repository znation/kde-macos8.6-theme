"""One KDE INI corpus, read through all three of the project's readers.

The theme tests read KDE INI with `support.kde_config.read`, the global
theme's `contents/defaults` with `tools.theme_defaults.defaults_groups`, and
`make uninstall` reads `kdeglobals` with an inline `awk`. Each reader used to
learn a quirk on its own, so a rule fixed in one was not checked in the other
two. This module feeds the shared corpus in `support.kde_ini_corpus` through
every reader and asserts they resolve the same selection, except that
`defaults_groups` refuses a malformed heading the KDE-facing readers skip
because its headings name output files.
"""

from __future__ import annotations

import os
import unittest

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support import kde_config
from support.kde_ini_corpus import CASES, SCHEME_ID, as_defaults
from support.process_assertions import assert_succeeded
from support.theme_install import installed_destdir, uninstall_recipe
from support.tmp_dir import make_tmp_dir
from tools import theme_defaults  # noqa: E402


def _kde_config_value(path):
    """Return the ``[General] ColorScheme`` value `kde_config.read` resolves."""
    parser = kde_config.read(path)
    if not parser.has_section("General"):
        return None
    return parser.get("General", "ColorScheme", fallback=None)


class TestReadersAgree(unittest.TestCase):
    def test_the_corpus_is_read_the_same_way_by_every_reader(self):
        scratch = make_tmp_dir(self)
        ini = scratch / "kdeglobals"
        defaults = scratch / "defaults"
        config = scratch / "config"
        config.mkdir()
        with installed_destdir(self, packages="color-scheme") as destdir:
            for case in CASES:
                with self.subTest(case=case.name):
                    ini.write_text(case.text, encoding="utf-8")
                    self._assert_kde_config_agrees(case, ini)

                    defaults.write_text(
                        as_defaults(case.text), encoding="utf-8"
                    )
                    self._assert_defaults_agrees(case, defaults)

                    (config / "kdeglobals").write_text(
                        case.text, encoding="utf-8"
                    )
                    self._assert_uninstall_warns(case, destdir, config)

    def _assert_kde_config_agrees(self, case, ini):
        """Assert `kde_config.read` resolves the case's expected selection."""
        self.assertEqual(
            case.expected,
            _kde_config_value(ini),
            "kde_config.read disagreed with the corpus",
        )

    def _assert_defaults_agrees(self, case, defaults):
        """Assert `defaults_groups` resolves the case's expected selection.

        A malformed heading names no output file, so `defaults_groups` refuses
        it rather than dropping a whole config section; the KDE-facing readers
        skip the line as KConfig does.
        """
        if case.defaults_raises:
            with self.assertRaises(ValueError):
                theme_defaults.defaults_groups(defaults)
            return
        groups = theme_defaults.defaults_groups(defaults)
        self.assertEqual(
            case.expected,
            groups.get(("kdeglobals", "General"), {}).get("ColorScheme"),
            "defaults_groups disagreed with the corpus",
        )

    def _assert_uninstall_warns(self, case, destdir, config):
        """Assert the uninstall recipe's warning matches the case.

        `make uninstall` only exposes the selection by warning when it equals
        the scheme id it removed, so this passes the case's expected value as
        that id: the warning then pins the exact value the recipe's awk read,
        including `%`, `=`, spaces and `#` inside a value. A case with no
        selection uses the real id and must stay silent; an empty expected
        value uses an empty id and must warn.
        """
        scheme_id = SCHEME_ID if case.expected is None else case.expected
        removed = uninstall_recipe(
            destdir,
            extra=(f"COLOR_SCHEME_ID={scheme_id}",),
            env=dict(os.environ, XDG_CONFIG_HOME=str(config)),
        )
        assert_succeeded(self, removed)
        self.assertEqual(
            case.expected is not None,
            "is still selected" in removed.stderr,
            "the uninstall recipe disagreed with the corpus",
        )

        if case.expected is not None:
            return

        # The non-empty id above makes no selection silent.
        # An empty id tells it apart only if the recipe
        # reports a present, empty value differently from a
        # missing key; an awk that skips `ColorScheme=` stays
        # silent and fails here. An empty expected value
        # already ran with an empty id above, so it needs no
        # second run.
        removed = uninstall_recipe(
            destdir,
            extra=("COLOR_SCHEME_ID=",),
            env=dict(os.environ, XDG_CONFIG_HOME=str(config)),
        )
        assert_succeeded(self, removed)
        self.assertEqual(
            case.expected == "",
            "is still selected" in removed.stderr,
            "the uninstall recipe cannot tell an empty "
            "selection from no selection",
        )


if __name__ == "__main__":
    unittest.main()
