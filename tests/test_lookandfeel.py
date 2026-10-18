"""Validate the org.macos8.desktop look-and-feel global theme package."""

import fcntl
import json
import os
import shlex
import shutil
import time
import unittest

from support.install_failure_cases import FailedInstallPreservesPackage
from support.install_lifecycle_cases import InstallLifecycleCases
from support.kpackage_install_case import KPackageInstallCase
from support.package_metadata import PackageMetadata
from support.process_assertions import assert_failed, assert_succeeded
from support.tmp_dir import make_tmp_dir
from support import process_runner
from support import theme_install
from support.kde_config import read as read_kde_config
from support.theme_install import (
    ROOT,
    install,
    installed_destdir,
    installed_package,
    shadow_command_env,
)

LNF_ID = "org.macos8.desktop"
PACKAGE = os.path.join(ROOT, "theme", "look-and-feel", LNF_ID)
METADATA = os.path.join(PACKAGE, "metadata.json")
DEFAULTS = os.path.join(PACKAGE, "contents", "defaults")
SCHEME = os.path.join(ROOT, "theme", "color-schemes", "MacOS8.colors")
AURORAE_DIR = os.path.join(
    ROOT, "theme", "aurorae", "themes", "org.macos8.desktop"
)
ICON_THEME_DIR = os.path.join(ROOT, "theme", "icons", "org.macos8.desktop")

# configparser reads a KDE header such as `[kdeglobals][General]` greedily, so
# the section key includes the inner bracket pair.
STYLE_SECTION = "kdeglobals][KDE"
DEFAULTS_SECTION = "kdeglobals][General"
ICONS_SECTION = "kdeglobals][Icons"
PLASMA_SECTION = "plasmarc][Theme"
KWIN_SECTION = "kwinrc][org.kde.kdecoration2"
WALLPAPER_SECTION = "Wallpaper"
WALLPAPER_METADATA = os.path.join(
    ROOT, "theme", "wallpapers", "org.macos8.desktop", "metadata.json"
)


def load_defaults():
    return read_kde_config(DEFAULTS)


class _DataHomeLock:
    """A data home whose install lock this process holds.

    `make install` stages under fixed hidden names in the data home and takes
    an exclusive `flock` over it, so two overlapping runs would share them. A
    test that means to hold that lock must take the same kernel lock before it
    starts the install, which this does on construction. `release` drops the
    lock early (the waiting-install test must release it before it joins the
    blocked install); `close` releases it if still held and closes the
    descriptor, so it can be registered with `addCleanup`.
    """

    def __init__(self, tmp):
        self.data_home = os.path.join(tmp, "share")
        os.makedirs(self.data_home)
        self.package = installed_package(tmp, "look-and-feel", LNF_ID)
        self._fd = os.open(self.data_home, os.O_RDONLY)
        self._locked = False
        try:
            fcntl.flock(self._fd, fcntl.LOCK_EX)
        except OSError:
            os.close(self._fd)
            raise
        self._locked = True

    def release(self):
        if self._locked:
            fcntl.flock(self._fd, fcntl.LOCK_UN)
            self._locked = False

    def close(self):
        self.release()
        os.close(self._fd)


class TestMetadata(PackageMetadata, unittest.TestCase):
    METADATA_PATH = METADATA
    PACKAGE_STRUCTURE = "Plasma/LookAndFeel"
    PACKAGE_ID = LNF_ID
    PLASMA_API_KEY = "X-Plasma-APIVersion"
    PLASMA_API_VERSION = "2"

    def test_keywords_non_empty(self):
        # A metadata.json that drops Keywords used to fail as ``None is not
        # true``, naming neither the file nor the key; a non-string or blank
        # value named neither either. Name the file and key for all three.
        keywords = self._top_level_field("Keywords")
        self.assertIsInstance(
            keywords, str, f"{METADATA}: top-level 'Keywords'"
        )
        self.assertTrue(
            keywords.strip(),
            f"{METADATA}: top-level 'Keywords' must not be blank",
        )


class TestDefaults(unittest.TestCase):
    def setUp(self):
        self.parser = load_defaults()

    def test_the_expected_sections_and_keys_are_set(self):
        self.assertEqual(
            self.parser.sections(),
            [
                STYLE_SECTION,
                DEFAULTS_SECTION,
                ICONS_SECTION,
                PLASMA_SECTION,
                KWIN_SECTION,
                WALLPAPER_SECTION,
            ],
        )
        self.assertEqual(self.parser.options(STYLE_SECTION), ["widgetStyle"])
        self.assertEqual(self.parser.options(DEFAULTS_SECTION), ["ColorScheme"])
        self.assertEqual(self.parser.options(ICONS_SECTION), ["Theme"])
        self.assertEqual(self.parser.options(PLASMA_SECTION), ["name"])
        self.assertEqual(
            self.parser.options(KWIN_SECTION),
            ["library", "theme", "ButtonsOnLeft", "ButtonsOnRight"],
        )
        self.assertEqual(self.parser.options(WALLPAPER_SECTION), ["Image"])

    def test_widget_style_is_kvantum(self):
        """The global theme selects our Kvantum widget style, which draws the
        Platinum bevels and scroll-bar arrows Qt's built-in styles only
        approximate. Kvantum is a separate engine the theme cannot install, so
        when it is absent the widgets fall back to another style."""
        self.assertEqual(self.parser.get(STYLE_SECTION, "widgetStyle"), "kvantum")

    def test_wallpaper_names_the_shipped_package(self):
        with open(WALLPAPER_METADATA, encoding="utf-8") as handle:
            package_id = json.load(handle)["KPlugin"]["Id"]
        self.assertEqual(
            self.parser.get(WALLPAPER_SECTION, "Image"), package_id
        )

    def test_icon_theme_names_the_shipped_package(self):
        """The global theme must select the icon theme this repo ships.

        KDE resolves `[Icons] Theme` to the directory under `icons/`, so
        renaming the package without updating `defaults` fails here instead of
        leaving the desktop on Breeze.
        """
        theme_id = os.path.basename(ICON_THEME_DIR)
        self.assertEqual(self.parser.get(ICONS_SECTION, "Theme"), theme_id)
        self.assertTrue(
            os.path.isfile(os.path.join(ICON_THEME_DIR, "index.theme")),
            "the icon theme lookup needs index.theme",
        )

    def test_window_decoration_names_the_shipped_theme(self):
        """The global theme must select the Aurorae theme this repo ships.

        The id is the directory holding the installed package's
        `metadata.desktop`, so renaming the Aurorae directory without updating
        `defaults` fails here instead of pointing KWin at a theme that is not
        installed.
        """
        self.assertEqual(
            self.parser.get(KWIN_SECTION, "library"), "org.kde.kwin.aurorae"
        )
        theme_id = os.path.basename(AURORAE_DIR)
        self.assertEqual(
            self.parser.get(KWIN_SECTION, "theme"),
            "__aurorae__svg__" + theme_id,
        )
        self.assertTrue(
            os.path.isfile(os.path.join(AURORAE_DIR, "metadata.desktop")),
            "KWin's Aurorae discovery needs metadata.desktop",
        )

    def test_titlebar_buttons_match_the_reference(self):
        """`systemprofiler_betawiki.png` shows close, zoom and collapse boxes.

        `X` is Close, `A` is Maximize (the zoom box) and `L` is Shade (the
        collapse box) in the KWin decoration button codes; close sits on the
        left and zoom then collapse at the far right.
        """
        self.assertEqual(self.parser.get(KWIN_SECTION, "ButtonsOnLeft"), "X")
        self.assertEqual(self.parser.get(KWIN_SECTION, "ButtonsOnRight"), "AL")

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
    INSTALLED_FILES = (
        "metadata.json",
        os.path.join("contents", "defaults"),
        os.path.join("contents", "layouts", "org.kde.plasma.desktop-layout.js"),
        os.path.join("contents", "splash", "Splash.qml"),
        os.path.join("contents", "splash", "images", "macos-logo.svg"),
    )

    @unittest.skipUnless(shutil.which("flock"), "needs flock")
    def test_make_install_waits_for_an_overlapping_install(self):
        """A second install must wait for the first, not clobber its staging.

        `install` stages under fixed hidden names in the data home, so two
        overlapping runs would share them. It takes an exclusive lock over the
        data home, so while another process holds that lock a new install makes
        no changes, then completes once the lock is released.
        """
        tmp = str(make_tmp_dir(self))
        lock = _DataHomeLock(tmp)
        self.addCleanup(lock.close)
        package = lock.package
        real_flock = shutil.which("flock")
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
        # `running` kills the install's whole process group if the poll
        # below raises, so an abandoned install cannot keep running and
        # holding the data-home lock after the test has failed.
        with process_runner.running(
            [
                "make", "install",
                f"DESTDIR={tmp}",
                f"XDG_DATA_HOME={theme_install.XDG_DATA_HOME}",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            env=env,
        ) as proc:
            try:
                deadline = time.monotonic() + process_runner.SUBPROCESS_TIMEOUT
                while (
                    not os.path.exists(invoked)
                    and proc.poll() is None
                    and time.monotonic() < deadline
                ):
                    time.sleep(0.05)
                reached_lock = os.path.exists(invoked)
                wrote = os.path.exists(package)
            finally:
                # Release the lock before `finish` waits, or the blocked
                # install would only time out.
                lock.release()
            _, err = process_runner.finish(proc)
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
        tmp = str(make_tmp_dir(self))
        lock = _DataHomeLock(tmp)
        self.addCleanup(lock.close)
        # FLOCK_TIMEOUT=0 makes the bounded wait expire immediately,
        # so the test does not spend the default 60s proving the bound.
        result = install(tmp, extra=["FLOCK_TIMEOUT=0"])
        assert_failed(self, result)
        self.assertIn("lock", result.stderr)
        self.assertFalse(os.path.exists(lock.package), lock.package)

    def test_make_install_prunes_files_removed_from_the_package(self):
        """A reinstall must replace the package, not merge into the old one."""
        with installed_destdir(self) as tmp:
            stale = os.path.join(
                installed_package(tmp, "look-and-feel", LNF_ID),
                "contents", "removed.qml",
            )
            with open(stale, "w", encoding="utf-8") as handle:
                handle.write("// deleted from the package\n")
            second = install(tmp)
            assert_succeeded(self, second)
            self.assertFalse(os.path.exists(stale), stale)


@unittest.skipUnless(shutil.which("kpackagetool6"), "needs kpackagetool6")
class TestPackageValid(KPackageInstallCase, unittest.TestCase):
    KPACKAGETOOL_TYPE = "Plasma/LookAndFeel"
    PACKAGE_DIR = PACKAGE
    PACKAGE_ID = LNF_ID


if __name__ == "__main__":
    unittest.main()
