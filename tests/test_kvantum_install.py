"""Validate the org.macos8.desktop Kvantum package and its install lifecycle.

The package ships exactly the `.kvconfig` and `.svg`, and `make install` copies
both byte for byte into `themes/org.macos8.desktop/Kvantum/`, where Kvantum
looks for them. The artwork and settings those files hold are covered by the
other `test_kvantum_*` modules.
"""

from __future__ import annotations

import os
import shutil
import unittest

from support.kvantum_fixtures import KVANTUM_ID, PACKAGE, SHIPPED_FILES
from support.process_assertions import assert_failed, assert_succeeded
from support.shipped_files import shipped_files
from support.theme_install import (
    XDG_DATA_HOME,
    assert_files_identical,
    install,
    installed_destdir,
    shadow_command_env,
    uninstall,
)


def _installed_dir(destdir):
    """Directory `make install` writes the Kvantum theme into."""
    return os.path.join(
        destdir, XDG_DATA_HOME.lstrip("/"), "themes", KVANTUM_ID, "Kvantum"
    )


class TestPackage(unittest.TestCase):
    def test_package_ships_exactly_the_theme_files(self):
        shipped = shipped_files(PACKAGE)
        self.assertEqual(shipped, set(SHIPPED_FILES))


class TestInstall(unittest.TestCase):
    def test_make_install_copies_both_files_byte_for_byte(self):
        with installed_destdir(self, packages="kvantum") as tmp:
            installed = _installed_dir(tmp)
            for name in SHIPPED_FILES:
                assert_files_identical(
                    self,
                    os.path.join(PACKAGE, name),
                    os.path.join(installed, name),
                    name,
                )

    def test_make_install_is_repeatable(self):
        with installed_destdir(self, packages="kvantum") as tmp:
            assert_succeeded(self, install(tmp, packages="kvantum"))

    def test_failed_install_keeps_the_previous_files(self):
        """A copy that dies partway must not damage the installed Kvantum files.

        `_install` stages each Kvantum file as a hidden sibling and renames it
        in, so a copy that fails or is interrupted leaves the working files
        intact and removes the staging file. The two files are installed by a
        shell loop distinct from `install_package`, so its `|| exit 1` and EXIT
        trap need their own failure case.
        """
        with installed_destdir(self, packages="kvantum") as tmp:
            installed = _installed_dir(tmp)
            good = {}
            for name in SHIPPED_FILES:
                with open(os.path.join(installed, name), "rb") as handle:
                    good[name] = handle.read()

            # Shadow `install` so a copy of a Kvantum file writes part of the
            # file then dies, like a killed or out-of-space install would.
            # Directory creation and the color scheme still pass through.
            real_install = shutil.which("install")
            env = shadow_command_env(
                tmp,
                "install",
                "#!/bin/sh\n"
                'case "$2" in\n'
                "  theme/kvantum/*)\n"
                '    dest="$3"\n'
                '    mkdir -p "$(dirname "$dest")"\n'
                '    printf partial > "$dest"\n'
                "    exit 1;;\n"
                "esac\n"
                'exec "%s" "$@"\n' % real_install,
            )
            result = install(tmp, env=env, packages="kvantum")
            assert_failed(self, result)
            for name in SHIPPED_FILES:
                staging = os.path.join(installed, f".{name}.staging")
                self.assertFalse(
                    os.path.exists(staging),
                    f"staging file leaked after a failed install: {staging}",
                )
                with open(os.path.join(installed, name), "rb") as handle:
                    self.assertEqual(
                        handle.read(),
                        good[name],
                        f"{name} was damaged by a failed install",
                    )

    def test_make_uninstall_removes_the_installed_files(self):
        with installed_destdir(self, packages="kvantum") as tmp:
            installed = _installed_dir(tmp)
            self.assertTrue(os.path.isdir(installed), installed)
            assert_succeeded(self, uninstall(tmp))
            for name in SHIPPED_FILES:
                path = os.path.join(installed, name)
                self.assertFalse(os.path.exists(path), path)
            again = uninstall(tmp)
            assert_succeeded(self, again)

    def test_make_uninstall_removes_staging_leftovers(self):
        with installed_destdir(self, packages="kvantum") as tmp:
            installed = _installed_dir(tmp)
            staging = [
                os.path.join(installed, f".{name}.staging")
                for name in SHIPPED_FILES
            ]
            for path in staging:
                with open(path, "w", encoding="utf-8") as handle:
                    handle.write("partial")
            assert_succeeded(self, uninstall(tmp))
            for path in staging:
                self.assertFalse(os.path.exists(path), path)


if __name__ == "__main__":
    unittest.main()
