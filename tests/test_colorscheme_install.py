"""Install/uninstall lifecycle tests for the Mac OS 8.6 color scheme.

`make install` copies the scheme under its source basename and `make uninstall`
removes only that file; these tests exercise that path in a throwaway DESTDIR
and, when Plasma's CLI is available, that the applied scheme id survives a
restart.
"""

import os
import shutil
import unittest

from support.colorscheme_fixtures import SCHEME
from support.process_assertions import assert_failed, assert_succeeded
from support.theme_install import (
    assert_files_identical,
    install,
    installed_color_scheme,
    installed_color_scheme_dir,
    installed_destdir,
    run_captured,
    shadow_command_env,
    staging_sibling,
    uninstall,
)
from support.tmp_dir import make_tmp_dir


def write_selected_scheme(tmp, scheme_id):
    """Create `<tmp>/config` selecting *scheme_id* as the user's scheme.

    Writes `<tmp>/config/kdeglobals` with `[General] ColorScheme=<scheme_id>`,
    the value `plasma-apply-colorscheme` leaves behind and KDE resolves on the
    next start. Returns the config directory, for use as `XDG_CONFIG_HOME`
    (and for reading the file back to prove a command did not edit it).
    """
    config = os.path.join(tmp, "config")
    os.makedirs(config, exist_ok=True)
    with open(
        os.path.join(config, "kdeglobals"), "w", encoding="utf-8"
    ) as handle:
        handle.write(f"[General]\nColorScheme={scheme_id}\n")
    return config


def uninstall_with_config(tmp, config, extra=()):
    """Run `make uninstall` with *config* as the user's `XDG_CONFIG_HOME`."""
    return uninstall(
        tmp, extra=extra, env=dict(os.environ, XDG_CONFIG_HOME=config)
    )


def install_renamed_scheme(case, tmp, filename):
    """Copy the scheme to `<tmp>/<filename>` and `make install` it from there.

    Asserts the install succeeds. Returns `(source, extra)`: the copied scheme
    and the `COLOR_SCHEME=<source>` argument list a later `uninstall` needs to
    target the same basename.
    """
    source = os.path.join(tmp, filename)
    shutil.copy(SCHEME, source)
    extra = [f"COLOR_SCHEME={source}"]
    assert_succeeded(case, install(tmp, extra=extra))
    return source, extra


class TestInstall(unittest.TestCase):
    def test_make_install_copies_scheme_byte_for_byte(self):
        with installed_destdir(self) as tmp:
            installed = installed_color_scheme(tmp)
            assert_files_identical(self, SCHEME, installed)

    def test_failed_reinstall_keeps_the_previous_scheme(self):
        """A copy that dies partway must not truncate the installed scheme.

        `make install` stages the scheme as a hidden sibling and renames it
        in, so a copy that fails or is interrupted leaves the working installed
        scheme intact.
        """
        with installed_destdir(self) as tmp:
            installed = installed_color_scheme(tmp)
            with open(installed, "rb") as handle:
                good = handle.read()

            # Shadow `install` so the scheme copy writes part of the file then
            # dies, like a killed or out-of-space install would. Directory
            # creation (`install -d`) still passes through to the real tool.
            real_install = shutil.which("install")
            env = shadow_command_env(
                tmp,
                "install",
                "#!/bin/sh\n"
                'case "$1" in\n'
                '  -d) exec "%s" "$@";;\n'
                "  -D*)\n"
                "    for last; do :; done\n"
                '    mkdir -p "$(dirname "$last")"\n'
                '    printf partial > "$last"\n'
                "    exit 1;;\n"
                "esac\n"
                'exec "%s" "$@"\n' % (real_install, real_install),
            )
            result = install(tmp, env=env)
            assert_failed(self, result)
            self.assertFalse(
                os.path.exists(
                    staging_sibling(
                        installed_color_scheme_dir(tmp), "MacOS8.colors"
                    )
                ),
                "staging file leaked after a failed install",
            )
            self.assertTrue(os.path.isfile(installed), installed)
            with open(installed, "rb") as handle:
                self.assertEqual(handle.read(), good)

    def test_make_install_names_the_scheme_after_its_source_basename(self):
        # KDE derives the scheme id from the installed filename, so install must
        # follow the source basename: a hardcoded destination name would install
        # a renamed scheme under the old id and break its restart resolution.
        tmp = str(make_tmp_dir(self))
        source, _ = install_renamed_scheme(self, tmp, "Platinum.colors")
        installed = installed_color_scheme(tmp, "Platinum.colors")
        assert_files_identical(self, source, installed)
        self.assertFalse(
            os.path.exists(installed_color_scheme(tmp)),
            "the old hardcoded name should not be installed",
        )

    def test_make_uninstall_removes_the_scheme_under_its_source_basename(self):
        # `uninstall` must remove the same basename `install` wrote: a hardcoded
        # name would leave a renamed scheme behind and delete the wrong file.
        tmp = str(make_tmp_dir(self))
        _, extra = install_renamed_scheme(self, tmp, "Platinum.colors")
        schemes = installed_color_scheme_dir(tmp)
        renamed = os.path.join(schemes, "Platinum.colors")
        self.assertTrue(os.path.isfile(renamed), renamed)
        decoy = os.path.join(schemes, "MacOS8.colors")
        with open(decoy, "w", encoding="utf-8") as handle:
            handle.write("[General]\nName=Decoy\n")

        removed = uninstall(tmp, extra=extra)
        assert_succeeded(self, removed)
        self.assertFalse(
            os.path.exists(renamed),
            "the renamed scheme should have been uninstalled",
        )
        self.assertTrue(
            os.path.isfile(decoy),
            "uninstall must not remove a file it did not install",
        )

    def test_make_uninstall_removes_only_the_scheme_it_installed(self):
        with installed_destdir(self) as tmp:
            schemes = installed_color_scheme_dir(tmp)
            other = os.path.join(schemes, "Other.colors")
            with open(other, "w", encoding="utf-8") as handle:
                handle.write("[General]\nName=Other\n")

            # SIGKILL cannot be trapped, so an install killed mid-copy leaves
            # the hidden staging file behind. `uninstall` must remove it too.
            staging = staging_sibling(schemes, "MacOS8.colors")
            with open(staging, "w", encoding="utf-8") as handle:
                handle.write("[General]\nName=Partial\n")

            removed = uninstall(tmp)
            assert_succeeded(self, removed)
            self.assertFalse(
                os.path.exists(os.path.join(schemes, "MacOS8.colors")),
                "the installed scheme should be gone",
            )
            self.assertFalse(
                os.path.exists(staging),
                "the staging file leaked after uninstall",
            )
            self.assertTrue(os.path.isfile(other), other)

            again = uninstall(tmp)
            assert_succeeded(self, again)

    def test_make_uninstall_warns_when_the_removed_scheme_is_still_selected(self):
        # Removing the scheme leaves `[General] ColorScheme=MacOS8` in the
        # user's kdeglobals; KDE then cannot resolve the id and falls back to
        # BreezeLight on every start. uninstall must warn and name the reset
        # command, without editing the user's config.
        with installed_destdir(self) as tmp:
            config = write_selected_scheme(tmp, "MacOS8")
            kdeglobals = os.path.join(config, "kdeglobals")
            original = "[General]\nColorScheme=MacOS8\n"

            removed = uninstall_with_config(tmp, config)
            assert_succeeded(self, removed)
            self.assertIn(
                "plasma-apply-colorscheme BreezeLight", removed.stderr
            )
            with open(kdeglobals, encoding="utf-8") as handle:
                self.assertEqual(
                    handle.read(),
                    original,
                    "uninstall must not edit the user's kdeglobals",
                )

    def test_make_uninstall_does_not_warn_for_a_different_selection(self):
        with installed_destdir(self) as tmp:
            config = write_selected_scheme(tmp, "BreezeLight")

            removed = uninstall_with_config(tmp, config)
            assert_succeeded(self, removed)
            self.assertNotIn("is still selected", removed.stderr)

    def test_make_uninstall_warns_for_a_scheme_id_with_a_space(self):
        # The scheme id is the basename before its first dot, spaces included:
        # whitespace word-splitting would compare `My Scheme` to `My` and miss
        # the warning for a renamed scheme.
        tmp = str(make_tmp_dir(self))
        _, extra = install_renamed_scheme(self, tmp, "My Scheme.colors")
        config = write_selected_scheme(tmp, "My Scheme")

        removed = uninstall_with_config(tmp, config, extra=extra)
        assert_succeeded(self, removed)
        self.assertIn(
            "color scheme My Scheme is still selected", removed.stderr
        )

    def _uninstall_with_kdeglobals(self, tmp, text):
        """Run `make uninstall` with *text* as the user's `kdeglobals`."""
        config = os.path.join(tmp, "config")
        os.makedirs(config, exist_ok=True)
        with open(
            os.path.join(config, "kdeglobals"), "w", encoding="utf-8"
        ) as handle:
            handle.write(text)
        return uninstall_with_config(tmp, config)

    def test_make_uninstall_warns_for_the_last_duplicate_selection(self):
        # KDE's config reader lets a later key override an earlier one, so a
        # kdeglobals with two ColorScheme lines selects the last. The warning
        # must read that value, not the first line.
        with installed_destdir(self) as tmp:
            removed = self._uninstall_with_kdeglobals(
                tmp, "[General]\nColorScheme=BreezeLight\nColorScheme=MacOS8\n"
            )

        assert_succeeded(self, removed)
        self.assertIn("is still selected", removed.stderr)

    def test_make_uninstall_does_not_warn_for_an_overridden_selection(self):
        # The inverse: an earlier MacOS8 overridden by a later BreezeLight
        # leaves KDE on BreezeLight, so uninstall must not warn.
        with installed_destdir(self) as tmp:
            removed = self._uninstall_with_kdeglobals(
                tmp, "[General]\nColorScheme=MacOS8\nColorScheme=BreezeLight\n"
            )

        assert_succeeded(self, removed)
        self.assertNotIn("is still selected", removed.stderr)

    def test_make_uninstall_warns_for_an_indented_general_section(self):
        # KDE trims each line before parsing it, so a `[General]` header with
        # leading whitespace still opens the section; the warning must find
        # the ColorScheme key under it. tests/support/kde_config.py reads the
        # file the same way through configparser, which also strips the line.
        with installed_destdir(self) as tmp:
            removed = self._uninstall_with_kdeglobals(
                tmp, "  [General]\nColorScheme=MacOS8\n"
            )

        assert_succeeded(self, removed)
        self.assertIn("is still selected", removed.stderr)

    def test_make_uninstall_warns_for_an_indented_color_scheme_key(self):
        # KDE trims each line before parsing it, so a `ColorScheme` key with
        # leading whitespace is still the live selection, and whitespace
        # around the `=` and after the value is stripped too. The warning
        # must read that value, not miss the indented key.
        with installed_destdir(self) as tmp:
            removed = self._uninstall_with_kdeglobals(
                tmp, "[General]\n  ColorScheme = MacOS8  \n"
            )

        assert_succeeded(self, removed)
        self.assertIn("is still selected", removed.stderr)


@unittest.skipUnless(
    shutil.which("plasma-apply-colorscheme"), "needs plasma-apply-colorscheme"
)
class TestRestartRoundTrip(unittest.TestCase):
    """Applying the listed id must leave a config KDE resolves on restart.

    `plasma-apply-colorscheme <id>` writes `[General] ColorScheme=<id>`; the next
    start resolves that value to `<id>.colors`. A dotted filename makes the
    listed id differ from the resolvable value, so the scheme falls back to
    BreezeLight after a restart.
    """

    def test_applied_id_survives_restart(self):
        tmp = str(make_tmp_dir(self))
        data = os.path.join(tmp, "data")
        schemes = os.path.join(data, "color-schemes")
        os.makedirs(schemes)
        config = write_selected_scheme(tmp, "BreezeLight")
        shutil.copy(SCHEME, os.path.join(schemes, os.path.basename(SCHEME)))
        kdeglobals = os.path.join(config, "kdeglobals")
        env = dict(
            os.environ,
            XDG_DATA_HOME=data,
            XDG_CONFIG_HOME=config,
            XDG_DATA_DIRS=data + os.pathsep + "/usr/share",
        )
        cli_id = os.path.basename(SCHEME).split(".", 1)[0]
        applied = run_captured(
            ["plasma-apply-colorscheme", cli_id],
            env=env,
        )
        assert_succeeded(self, applied)
        with open(kdeglobals, encoding="utf-8") as handle:
            written = handle.read()
        self.assertIn(f"ColorScheme={cli_id}", written)
        restarted = run_captured(
            ["plasma-apply-colorscheme"],
            env=env,
        )
        self.assertNotIn(
            "Could not find",
            restarted.stdout + restarted.stderr,
            "applied scheme id did not resolve on restart",
        )


if __name__ == "__main__":
    unittest.main()
