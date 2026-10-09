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

from process_assertions import assert_failed, assert_succeeded
from theme_install import (
    InstalledPackageLocation,
    install,
    old_sibling,
    shadow_command_env,
    staging_sibling,
)


def failing_cp_env(tmp, package_glob=None):
    """Environment whose `cp` writes a partial package then dies.

    ``package_glob`` selects the copy that fails, so an earlier package
    family's copies still succeed; with ``None`` the first copy fails. The
    fake writes part of the tree and exits non-zero, like a copy killed or out
    of space halfway through.
    """
    real_cp = shutil.which("cp")
    if package_glob is None:
        script = (
            "#!/bin/sh\n"
            'src="$2"\n'
            'dest="$3/$(basename "$src")"\n'
            'mkdir -p "$dest"\n'
            'printf partial > "$dest/metadata.json"\n'
            "exit 1\n"
        )
    else:
        script = (
            "#!/bin/sh\n"
            'case "$2" in\n'
            f"  {package_glob})\n"
            '    dest="$3/$(basename "$2")"\n'
            '    mkdir -p "$dest"\n'
            '    printf partial > "$dest/metadata.json"\n'
            "    exit 1;;\n"
            "esac\n"
            f'exec "{real_cp}" "$@"\n'
        )
    return shadow_command_env(tmp, "cp", script)


class FailedInstallPreservesPackage(InstalledPackageLocation):
    """Mixin: a failed `make install` must leave the previous package installed.

    `InstalledPackageLocation` supplies `installed_parent` and
    `installed_package_dir` from `KIND`/`PACKAGE_ID`; subclasses set
    `COPY_FAILURE_GLOB` for the copy-failure case. It is a plain mixin, not a
    `TestCase`, so importing it into a test module does not collect the
    unconfigured base.
    """

    def _staging_path(self, tmp):
        return staging_sibling(
            self.installed_parent(tmp), self.PACKAGE_ID
        )

    def _snapshot(self, tmp):
        """Return the installed package directory, metadata path and bytes."""
        installed = self.installed_package_dir(tmp)
        metadata = os.path.join(installed, "metadata.json")
        with open(metadata, "rb") as handle:
            return installed, metadata, handle.read()

    def _install_ok(self, tmp):
        """Install once into `tmp`, assert it succeeded, and snapshot it.

        Returns `_snapshot`'s (installed, metadata, good) triple.
        """
        first = install(tmp)
        assert_succeeded(self, first)
        return self._snapshot(tmp)

    def _assert_package_intact(self, installed, metadata, good):
        self.assertTrue(os.path.isdir(installed), installed)
        with open(metadata, "rb") as handle:
            self.assertEqual(handle.read(), good)

    # Path pattern selecting which `cp` fails in `reinstall_failure_env`; a
    # single `make install` copies several package families, so a suite whose
    # copy runs after an earlier family's sets its own pattern. `None` fails
    # the first copy.
    COPY_FAILURE_GLOB = None

    def reinstall_failure_env(self, tmp):
        """Environment whose `cp` fails while copying this package."""
        return failing_cp_env(tmp, self.COPY_FAILURE_GLOB)

    def swap_failure_env(self, tmp):
        """Environment whose `mv` fails only on the final package rename."""
        real_mv = shutil.which("mv")
        package_dir = self.installed_package_dir(tmp)
        return shadow_command_env(
            tmp,
            "mv",
            "#!/bin/sh\n"
            'case "$2" in\n'
            f'  "{package_dir}")\n'
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
            installed, metadata, good = self._install_ok(tmp)

            # Reproduce the kill window: the working package was moved aside,
            # but the staged copy was never renamed into place.
            old = old_sibling(
                self.installed_parent(tmp), self.PACKAGE_ID
            )
            os.rename(installed, old)

            result = install(tmp, env=self.reinstall_failure_env(tmp))
            assert_failed(self, result)
            self._assert_package_intact(installed, metadata, good)

    def test_failed_reinstall_keeps_the_previous_package(self):
        """A copy that dies partway must not delete or damage the working install.

        `make install` copies into a sibling staging directory and swaps it in
        with a rename, so a copy that fails or is interrupted leaves the working
        package installed.
        """
        with tempfile.TemporaryDirectory() as tmp:
            installed, metadata, good = self._install_ok(tmp)

            result = install(tmp, env=self.reinstall_failure_env(tmp))
            assert_failed(self, result)
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
            installed, metadata, good = self._install_ok(tmp)

            result = install(tmp, env=self.swap_failure_env(tmp))
            assert_failed(self, result)
            parent = self.installed_parent(tmp)
            for leaked in (
                staging_sibling(parent, self.PACKAGE_ID),
                old_sibling(parent, self.PACKAGE_ID),
            ):
                self.assertFalse(
                    os.path.exists(leaked),
                    f"{os.path.basename(leaked)} leaked after a failed swap",
                )
            self._assert_package_intact(installed, metadata, good)
