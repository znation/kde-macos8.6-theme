"""`make install INSTALL_PACKAGES=ghostty` and `make uninstall` for the Ghostty theme.

The Platinum theme file installs byte-identical to its source under
`$XDG_DATA_HOME/ghostty/themes/<id>/`. Uninstall removes that package and the
`ghostty/themes` and `ghostty` directories only once they are empty, so a file
a user placed there survives with its directories.
"""

import os
import unittest

from support import installed_paths, theme_install
from support.process_assertions import assert_succeeded
from support.repo_root import ROOT
from support.tmp_dir import make_tmp_dir

SOURCE = os.path.join(
    ROOT, "theme", "ghostty", "org.macos8.desktop", "Platinum"
)


def _ghostty_dirs(tmp):
    data_home = os.path.join(tmp, installed_paths.XDG_DATA_HOME.lstrip("/"))
    ghostty = os.path.join(data_home, "ghostty")
    return ghostty, os.path.join(ghostty, "themes")


def _installed_platinum(tmp):
    return os.path.join(
        _ghostty_dirs(tmp)[1], "org.macos8.desktop", "Platinum"
    )


class TestGhosttyInstall(unittest.TestCase):
    def test_install_copies_platinum_byte_identical(self):
        tmp = str(make_tmp_dir(self))
        assert_succeeded(self, theme_install.install(tmp, packages="ghostty"))
        theme_install.assert_files_identical(
            self, SOURCE, _installed_platinum(tmp)
        )

    def test_default_install_includes_the_ghostty_family(self):
        # No INSTALL_PACKAGES: the Makefile's default family list must name
        # `ghostty`, so a plain `make install` ships the theme file too.
        tmp = str(make_tmp_dir(self))
        assert_succeeded(self, theme_install.install(tmp))
        theme_install.assert_files_identical(
            self, SOURCE, _installed_platinum(tmp)
        )

    def test_install_writes_nothing_outside_the_ghostty_directory(self):
        tmp = str(make_tmp_dir(self))
        assert_succeeded(self, theme_install.install(tmp, packages="ghostty"))
        data_home = os.path.join(tmp, installed_paths.XDG_DATA_HOME.lstrip("/"))
        self.assertEqual(sorted(os.listdir(data_home)), ["ghostty"])


class TestGhosttyUninstall(unittest.TestCase):
    def test_uninstall_removes_the_theme_and_its_empty_directories(self):
        tmp = str(make_tmp_dir(self))
        assert_succeeded(self, theme_install.install(tmp, packages="ghostty"))
        assert_succeeded(self, theme_install.uninstall(tmp))
        ghostty, themes = _ghostty_dirs(tmp)
        self.assertFalse(os.path.exists(_installed_platinum(tmp)))
        self.assertFalse(os.path.exists(themes))
        self.assertFalse(os.path.exists(ghostty))

    def test_a_foreign_file_under_themes_keeps_its_directories(self):
        tmp = str(make_tmp_dir(self))
        assert_succeeded(self, theme_install.install(tmp, packages="ghostty"))
        ghostty, themes = _ghostty_dirs(tmp)
        foreign = os.path.join(themes, "user-theme")
        with open(foreign, "w", encoding="utf-8") as handle:
            handle.write("background = #123456\n")
        assert_succeeded(self, theme_install.uninstall(tmp))
        self.assertFalse(os.path.exists(_installed_platinum(tmp)))
        self.assertTrue(os.path.isfile(foreign), foreign)
        self.assertTrue(os.path.isdir(themes), themes)
        self.assertTrue(os.path.isdir(ghostty), ghostty)


if __name__ == "__main__":
    unittest.main()
