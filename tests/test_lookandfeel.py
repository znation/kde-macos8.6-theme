"""Validate the org.macos8.desktop look-and-feel global theme package."""

import fcntl
import os
import shlex
import shutil
import subprocess
import tempfile
import time
import unittest

from install_failure_cases import FailedInstallPreservesPackage
from install_lifecycle_cases import InstallLifecycleCases
from kpackage_install_case import KPackageInstallCase
from package_metadata import PackageMetadata
import theme_install
from kde_config import read as read_kde_config
from theme_install import (
    ROOT,
    install,
    installed_package,
    shadow_command_env,
)

LNF_ID = "org.macos8.desktop"
PACKAGE = os.path.join(ROOT, "theme", "look-and-feel", LNF_ID)
METADATA = os.path.join(PACKAGE, "metadata.json")
DEFAULTS = os.path.join(PACKAGE, "contents", "defaults")
SCHEME = os.path.join(ROOT, "theme", "color-schemes", "MacOS8.colors")

# configparser reads the KDE `[kdeglobals][General]` header greedily, so the
# section key includes the inner bracket pair.
DEFAULTS_SECTION = "kdeglobals][General"
PLASMA_SECTION = "plasmarc][Theme"


def load_defaults():
    return read_kde_config(DEFAULTS)


class TestMetadata(PackageMetadata, unittest.TestCase):
    METADATA_PATH = METADATA
    PACKAGE_STRUCTURE = "Plasma/LookAndFeel"
    PACKAGE_ID = LNF_ID
    PLASMA_API_KEY = "X-Plasma-APIVersion"
    PLASMA_API_VERSION = "2"

    def test_keywords_non_empty(self):
        self.assertTrue(self.metadata.get("Keywords"))


class TestDefaults(unittest.TestCase):
    def setUp(self):
        self.parser = load_defaults()

    def test_the_expected_sections_and_keys_are_set(self):
        self.assertEqual(
            self.parser.sections(), [DEFAULTS_SECTION, PLASMA_SECTION]
        )
        self.assertEqual(self.parser.options(DEFAULTS_SECTION), ["ColorScheme"])
        self.assertEqual(self.parser.options(PLASMA_SECTION), ["name"])

    def test_color_scheme_matches_the_scheme_file(self):
        """The package must apply the scheme this repository actually ships.

        The value is resolved as `<value>.colors`, so it has to equal the
        scheme's own `ColorScheme` and name a file beside it; that keeps the
        pairing true if the scheme is renamed later.
        """
        value = self.parser.get(DEFAULTS_SECTION, "ColorScheme")
        scheme = read_kde_config(SCHEME)
        self.assertEqual(value, scheme.get("General", "ColorScheme"))
        self.assertTrue(
            os.path.isfile(
                os.path.join(os.path.dirname(SCHEME), value + ".colors")
            ),
            value,
        )


class TestInstall(
    FailedInstallPreservesPackage, InstallLifecycleCases, unittest.TestCase
):
    KIND = "look-and-feel"
    PACKAGE_ID = LNF_ID
    PACKAGE_DIR = PACKAGE
    INSTALLED_FILES = ("metadata.json", os.path.join("contents", "defaults"))

    def reinstall_failure_env(self, tmp):
        # Shadow `cp` with a fake that writes part of the tree, then fails,
        # simulating a copy killed or out of space halfway through.
        return shadow_command_env(
            tmp,
            "cp",
            '#!/bin/sh\n'
            '# Copy part of the tree, then die, like a killed `cp` would.\n'
            'src="$2"\n'
            'dest="$3/$(basename "$src")"\n'
            'mkdir -p "$dest"\n'
            'printf partial > "$dest/metadata.json"\n'
            'exit 1\n',
        )

    @unittest.skipUnless(shutil.which("flock"), "needs flock")
    def test_make_install_waits_for_an_overlapping_install(self):
        """A second install must wait for the first, not clobber its staging.

        `install` stages under fixed hidden names in the data home, so two
        overlapping runs would share them. It takes an exclusive lock over the
        data home, so while another process holds that lock a new install makes
        no changes, then completes once the lock is released.
        """
        with tempfile.TemporaryDirectory() as tmp:
            data_home = os.path.join(tmp, "share")
            os.makedirs(data_home)
            package = os.path.join(
                data_home, "plasma", "look-and-feel", LNF_ID
            )
            real_flock = shutil.which("flock")
            # Hold the same kernel lock the `flock` in the Makefile takes,
            # before starting the install, so the install can never win a race
            # for the lock the test means to hold.
            lock_fd = os.open(data_home, os.O_RDONLY)
            fcntl.flock(lock_fd, fcntl.LOCK_EX)
            # Shadow `flock` so the install records the moment it reaches the
            # lock step. The test waits for that record instead of guessing
            # with a sleep, so an install that skips the lock is caught when it
            # exits without one, however slow the host is.
            invoked = os.path.join(tmp, "flock-invoked")
            env = shadow_command_env(
                tmp,
                "flock",
                "#!/bin/sh\n"
                f": > {shlex.quote(invoked)}\n"
                f"exec {shlex.quote(real_flock)} \"$@\"\n",
            )
            proc = subprocess.Popen(
                [
                    "make", "install",
                    f"DESTDIR={tmp}",
                    f"XDG_DATA_HOME={theme_install.XDG_DATA_HOME}",
                ],
                cwd=ROOT,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env,
            )
            try:
                deadline = time.monotonic() + theme_install.SUBPROCESS_TIMEOUT
                while (
                    not os.path.exists(invoked)
                    and proc.poll() is None
                    and time.monotonic() < deadline
                ):
                    time.sleep(0.05)
                reached_lock = os.path.exists(invoked)
                wrote = os.path.exists(package)
            finally:
                fcntl.flock(lock_fd, fcntl.LOCK_UN)
                os.close(lock_fd)
            _, err = proc.communicate(timeout=theme_install.SUBPROCESS_TIMEOUT)
            self.assertTrue(
                reached_lock, "install did not take the data-home lock"
            )
            self.assertFalse(
                wrote, "install wrote the package while the lock was held"
            )
            self.assertEqual(proc.returncode, 0, err)
            self.assertTrue(
                os.path.isfile(os.path.join(package, "metadata.json"))
            )

    @unittest.skipUnless(shutil.which("flock"), "needs flock")
    def test_make_install_gives_up_on_a_held_lock(self):
        """A lock held by a live process must not hang a later install.

        flock releases the data-home lock when its holder dies, but a holder
        that stays alive -- stopped with SIGSTOP, or blocked in the kernel --
        keeps it. The lock wait is bounded, so a later install gives up with a
        diagnostic naming the lock instead of waiting forever, and writes
        nothing.
        """
        with tempfile.TemporaryDirectory() as tmp:
            data_home = os.path.join(tmp, "share")
            os.makedirs(data_home)
            package = os.path.join(
                data_home, "plasma", "look-and-feel", LNF_ID
            )
            lock_fd = os.open(data_home, os.O_RDONLY)
            fcntl.flock(lock_fd, fcntl.LOCK_EX)
            try:
                # FLOCK_TIMEOUT=0 makes the bounded wait expire immediately,
                # so the test does not spend the default 60s proving the bound.
                result = install(tmp, extra=["FLOCK_TIMEOUT=0"])
            finally:
                fcntl.flock(lock_fd, fcntl.LOCK_UN)
                os.close(lock_fd)
            self.assertNotEqual(result.returncode, 0, result.stdout)
            self.assertIn("lock", result.stderr)
            self.assertFalse(os.path.exists(package), package)

    def test_make_install_prunes_files_removed_from_the_package(self):
        """A reinstall must replace the package, not merge into the old one."""
        with tempfile.TemporaryDirectory() as tmp:
            first = install(tmp)
            self.assertEqual(first.returncode, 0, first.stderr)
            stale = os.path.join(
                installed_package(tmp, "look-and-feel", LNF_ID),
                "contents", "removed.qml",
            )
            with open(stale, "w", encoding="utf-8") as handle:
                handle.write("// deleted from the package\n")
            second = install(tmp)
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertFalse(os.path.exists(stale), stale)


@unittest.skipUnless(shutil.which("kpackagetool6"), "needs kpackagetool6")
class TestPackageValid(KPackageInstallCase, unittest.TestCase):
    KPACKAGETOOL_TYPE = "Plasma/LookAndFeel"
    PACKAGE_DIR = PACKAGE
    PACKAGE_ID = LNF_ID


if __name__ == "__main__":
    unittest.main()
