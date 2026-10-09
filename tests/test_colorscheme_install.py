"""Install/uninstall lifecycle tests for the Mac OS 8.6 color scheme.

`make install` copies the scheme under its source basename and `make uninstall`
removes only that file; these tests exercise that path in a throwaway DESTDIR
and, when Plasma's CLI is available, that the applied scheme id survives a
restart.
"""

import os
import shutil
import tempfile
import unittest

from colorscheme_fixtures import SCHEME
from theme_install import (
    assert_files_identical,
    install,
    installed_color_scheme,
    installed_color_scheme_dir,
    run_captured,
    shadow_command_env,
    staging_sibling,
    uninstall,
)


class TestInstall(unittest.TestCase):
    def test_make_install_copies_scheme_byte_for_byte(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = install(tmp)
            self.assertEqual(result.returncode, 0, result.stderr)
            installed = installed_color_scheme(tmp)
            assert_files_identical(self, SCHEME, installed)

    def test_failed_reinstall_keeps_the_previous_scheme(self):
        """A copy that dies partway must not truncate the installed scheme.

        `make install` stages the scheme as a hidden sibling and renames it
        in, so a copy that fails or is interrupted leaves the working installed
        scheme intact.
        """
        with tempfile.TemporaryDirectory() as tmp:
            first = install(tmp)
            self.assertEqual(first.returncode, 0, first.stderr)
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
            self.assertNotEqual(result.returncode, 0, result.stdout)
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
        with tempfile.TemporaryDirectory() as tmp:
            source = os.path.join(tmp, "Platinum.colors")
            shutil.copy(SCHEME, source)
            result = install(tmp, extra=[f"COLOR_SCHEME={source}"])
            self.assertEqual(result.returncode, 0, result.stderr)
            installed = installed_color_scheme(tmp, "Platinum.colors")
            assert_files_identical(self, source, installed)
            self.assertFalse(
                os.path.exists(installed_color_scheme(tmp)),
                "the old hardcoded name should not be installed",
            )

    def test_make_uninstall_removes_the_scheme_under_its_source_basename(self):
        # `uninstall` must remove the same basename `install` wrote: a hardcoded
        # name would leave a renamed scheme behind and delete the wrong file.
        with tempfile.TemporaryDirectory() as tmp:
            source = os.path.join(tmp, "Platinum.colors")
            shutil.copy(SCHEME, source)
            installed = install(tmp, extra=[f"COLOR_SCHEME={source}"])
            self.assertEqual(installed.returncode, 0, installed.stderr)
            schemes = installed_color_scheme_dir(tmp)
            renamed = os.path.join(schemes, "Platinum.colors")
            self.assertTrue(os.path.isfile(renamed), renamed)
            decoy = os.path.join(schemes, "MacOS8.colors")
            with open(decoy, "w", encoding="utf-8") as handle:
                handle.write("[General]\nName=Decoy\n")

            removed = uninstall(tmp, extra=[f"COLOR_SCHEME={source}"])
            self.assertEqual(removed.returncode, 0, removed.stderr)
            self.assertFalse(
                os.path.exists(renamed),
                "the renamed scheme should have been uninstalled",
            )
            self.assertTrue(
                os.path.isfile(decoy),
                "uninstall must not remove a file it did not install",
            )

    def test_make_uninstall_removes_only_the_scheme_it_installed(self):
        with tempfile.TemporaryDirectory() as tmp:
            installed = install(tmp)
            self.assertEqual(installed.returncode, 0, installed.stderr)
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
            self.assertEqual(removed.returncode, 0, removed.stderr)
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
            self.assertEqual(again.returncode, 0, again.stderr)


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
        with tempfile.TemporaryDirectory() as tmp:
            data = os.path.join(tmp, "data")
            config = os.path.join(tmp, "config")
            schemes = os.path.join(data, "color-schemes")
            os.makedirs(schemes)
            os.makedirs(config)
            shutil.copy(SCHEME, os.path.join(schemes, os.path.basename(SCHEME)))
            kdeglobals = os.path.join(config, "kdeglobals")
            with open(kdeglobals, "w", encoding="utf-8") as handle:
                handle.write("[General]\nColorScheme=BreezeLight\n")
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
            self.assertEqual(applied.returncode, 0, applied.stderr)
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
