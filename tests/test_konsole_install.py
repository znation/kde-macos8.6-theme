"""`make install INSTALL_PACKAGES=konsole` and `make uninstall` for the Konsole colorscheme.

The scheme installs byte-identical to its source as one flat file,
`$XDG_DATA_HOME/konsole/MacOS8.colorscheme`, with no other file beside it. A
later subset install adds beside what is there, and `make uninstall` removes
the file and then `konsole/` only once it is empty, so a file the user placed
there survives with its directory.
"""

import os
import unittest

from support import installed_paths, theme_install
from support.process_assertions import assert_succeeded
from support.repo_root import ROOT
from support.tmp_dir import make_tmp_dir

SOURCE = os.path.join(ROOT, "theme", "konsole", "MacOS8.colorscheme")


def _konsole_dir(tmp):
    data_home = os.path.join(tmp, installed_paths.XDG_DATA_HOME.lstrip("/"))
    return data_home, os.path.join(data_home, "konsole")


def _installed_scheme(tmp):
    return os.path.join(_konsole_dir(tmp)[1], "MacOS8.colorscheme")


class TestKonsoleInstall(unittest.TestCase):
    def test_install_copies_the_scheme_byte_identical_and_flat(self):
        tmp = str(make_tmp_dir(self))
        assert_succeeded(self, theme_install.install(tmp, packages="konsole"))
        theme_install.assert_files_identical(
            self, SOURCE, _installed_scheme(tmp)
        )
        data_home, konsole = _konsole_dir(tmp)
        self.assertEqual(os.listdir(konsole), ["MacOS8.colorscheme"])
        self.assertEqual(os.listdir(data_home), ["konsole"])

    def test_default_install_includes_the_konsole_family(self):
        # No INSTALL_PACKAGES: the Makefile's default family list must name
        # `konsole`, so a plain `make install` ships the scheme too.
        tmp = str(make_tmp_dir(self))
        assert_succeeded(self, theme_install.install(tmp))
        theme_install.assert_files_identical(
            self, SOURCE, _installed_scheme(tmp)
        )

    def test_a_later_subset_install_keeps_the_scheme(self):
        tmp = str(make_tmp_dir(self))
        assert_succeeded(self, theme_install.install(tmp, packages="konsole"))
        assert_succeeded(self, theme_install.install(tmp, packages="ghostty"))
        theme_install.assert_files_identical(
            self, SOURCE, _installed_scheme(tmp)
        )
        data_home, _ = _konsole_dir(tmp)
        self.assertEqual(sorted(os.listdir(data_home)), ["ghostty", "konsole"])


class TestKonsoleUninstall(unittest.TestCase):
    def test_uninstall_removes_the_scheme_and_its_empty_directory(self):
        tmp = str(make_tmp_dir(self))
        assert_succeeded(self, theme_install.install(tmp, packages="konsole"))
        assert_succeeded(self, theme_install.uninstall(tmp))
        data_home, konsole = _konsole_dir(tmp)
        self.assertFalse(os.path.exists(_installed_scheme(tmp)))
        self.assertFalse(os.path.exists(konsole))

    def test_a_foreign_file_under_konsole_keeps_the_directory(self):
        tmp = str(make_tmp_dir(self))
        assert_succeeded(self, theme_install.install(tmp, packages="konsole"))
        _, konsole = _konsole_dir(tmp)
        foreign = os.path.join(konsole, "user.colorscheme")
        with open(foreign, "w", encoding="utf-8") as handle:
            handle.write("[General]\nDescription=user\n")
        assert_succeeded(self, theme_install.uninstall(tmp))
        self.assertFalse(os.path.exists(_installed_scheme(tmp)))
        self.assertTrue(os.path.isfile(foreign), foreign)
        self.assertTrue(os.path.isdir(konsole), konsole)


if __name__ == "__main__":
    unittest.main()
