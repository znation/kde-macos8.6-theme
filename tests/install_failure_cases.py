"""Shared cases for a failed `make install` that must preserve the old package.

The look-and-feel and desktop-theme installers both copy into a hidden staging
sibling and swap it in with a rename, so the same two failure modes apply to
either package. Each suite subclasses `FailedInstallPreservesPackage`, sets
`KIND`/`PACKAGE_ID`, and supplies the copy-failure environment; the flow and
assertions live here once.
"""

import os
import shutil
import tempfile

from theme_install import (
    install,
    installed_package,
    installed_plasma_dir,
    shadow_command_env,
)


class FailedInstallPreservesPackage:
    """Mixin: a failed `make install` must leave the previous package installed.

    Subclasses set `KIND` (`look-and-feel` or `desktoptheme`) and `PACKAGE_ID`,
    and override `reinstall_failure_env` for the copy-failure case. It is a
    plain mixin, not a `TestCase`, so importing it into a test module does not
    collect the unconfigured base.
    """

    KIND = None
    PACKAGE_ID = None

    def _staging_path(self, tmp):
        return os.path.join(
            installed_plasma_dir(tmp, self.KIND),
            "." + self.PACKAGE_ID + ".staging",
        )

    def _snapshot(self, tmp):
        """Return the installed package directory, metadata path and bytes."""
        installed = installed_package(tmp, self.KIND, self.PACKAGE_ID)
        metadata = os.path.join(installed, "metadata.json")
        with open(metadata, "rb") as handle:
            return installed, metadata, handle.read()

    def _assert_package_intact(self, installed, metadata, good):
        self.assertTrue(os.path.isdir(installed), installed)
        with open(metadata, "rb") as handle:
            self.assertEqual(handle.read(), good)

    def reinstall_failure_env(self, tmp):
        """Environment whose `cp` fails while copying this package.

        Subclasses override this: a single `make install` also copies the other
        package family, so each suite's failure script matches differently.
        """
        raise NotImplementedError

    def swap_failure_env(self, tmp):
        """Environment whose `mv` fails only on the final package rename."""
        real_mv = shutil.which("mv")
        return shadow_command_env(
            tmp,
            "mv",
            "#!/bin/sh\n"
            'case "$2" in\n'
            f"  */plasma/{self.KIND}/{self.PACKAGE_ID})\n"
            '    case "$1" in\n'
            f"      */.{self.PACKAGE_ID}.staging) exit 1;;\n"
            "    esac;;\n"
            "esac\n"
            f'exec "{real_mv}" "$@"\n',
        )

    def test_reinstall_after_killed_swap_recovers_the_old_package(self):
        """A SIGKILL mid-swap leaves the package absent and its bytes in `.old`.

        `make install` moves the working package to a hidden sibling, then
        renames the staged copy into place; a SIGKILL between the two renames
        runs neither the trap nor the final rename, so the package is absent
        and `.old` holds the only copy. The next install must move `.old` back
        before it removes anything, so a copy that then fails leaves the last
        working package installed rather than deleting it.
        """
        with tempfile.TemporaryDirectory() as tmp:
            first = install(tmp)
            self.assertEqual(first.returncode, 0, first.stderr)
            installed, metadata, good = self._snapshot(tmp)

            # Reproduce the kill window: the working package was moved aside,
            # but the staged copy was never renamed into place.
            old = os.path.join(
                installed_plasma_dir(tmp, self.KIND),
                "." + self.PACKAGE_ID + ".old",
            )
            os.rename(installed, old)

            result = install(tmp, env=self.reinstall_failure_env(tmp))
            self.assertNotEqual(result.returncode, 0, result.stdout)
            self._assert_package_intact(installed, metadata, good)

    def test_failed_reinstall_keeps_the_previous_package(self):
        """A copy that dies partway must not delete or damage the working install.

        `make install` copies into a sibling staging directory and swaps it in
        with a rename, so a copy that fails or is interrupted leaves the working
        package installed.
        """
        with tempfile.TemporaryDirectory() as tmp:
            first = install(tmp)
            self.assertEqual(first.returncode, 0, first.stderr)
            installed, metadata, good = self._snapshot(tmp)

            result = install(tmp, env=self.reinstall_failure_env(tmp))
            self.assertNotEqual(result.returncode, 0, result.stdout)
            self.assertFalse(
                os.path.exists(self._staging_path(tmp)),
                "staging directory leaked after a failed install",
            )
            self._assert_package_intact(installed, metadata, good)

    def test_failed_swap_keeps_the_previous_package(self):
        """A rename that fails after the old package is moved aside restores it.

        `make install` moves the working package to a hidden sibling before
        renaming the staged copy into place. If that final rename fails, the
        EXIT trap must move the old package back, so a failed swap leaves the
        working install rather than deleting it.
        """
        with tempfile.TemporaryDirectory() as tmp:
            first = install(tmp)
            self.assertEqual(first.returncode, 0, first.stderr)
            installed, metadata, good = self._snapshot(tmp)

            result = install(tmp, env=self.swap_failure_env(tmp))
            self.assertNotEqual(result.returncode, 0, result.stdout)
            parent = installed_plasma_dir(tmp, self.KIND)
            for leaked in (
                "." + self.PACKAGE_ID + ".staging",
                "." + self.PACKAGE_ID + ".old",
            ):
                self.assertFalse(
                    os.path.exists(os.path.join(parent, leaked)),
                    f"{leaked} leaked after a failed swap",
                )
            self._assert_package_intact(installed, metadata, good)
