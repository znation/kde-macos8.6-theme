"""Validate the org.macos8.desktop look-and-feel global theme package."""

import json
import os
import shutil
import subprocess
import tempfile
import unittest

from kde_config import read as read_kde_config
from theme_install import ROOT, install, uninstall

LNF_ID = "org.macos8.desktop"
PACKAGE = os.path.join(ROOT, "theme", "look-and-feel", LNF_ID)
METADATA = os.path.join(PACKAGE, "metadata.json")
DEFAULTS = os.path.join(PACKAGE, "contents", "defaults")
SCHEME = os.path.join(ROOT, "theme", "color-schemes", "MacOS8.colors")

# configparser reads the KDE `[kdeglobals][General]` header greedily, so the
# section key includes the inner bracket pair.
DEFAULTS_SECTION = "kdeglobals][General"
PLASMA_SECTION = "plasmarc][Theme"


def load_metadata():
    with open(METADATA, encoding="utf-8") as handle:
        return json.load(handle)


def load_defaults():
    return read_kde_config(DEFAULTS)


class TestMetadata(unittest.TestCase):
    def setUp(self):
        self.metadata = load_metadata()

    def test_package_structure(self):
        self.assertEqual(
            self.metadata.get("KPackageStructure"), "Plasma/LookAndFeel"
        )

    def test_plugin_id_and_name(self):
        plugin = self.metadata["KPlugin"]
        self.assertEqual(plugin["Id"], LNF_ID)
        self.assertEqual(plugin["Name"], "Mac OS 8.6")

    def test_plugin_version(self):
        self.assertTrue(self.metadata["KPlugin"].get("Version"))

    def test_plasma_api_version(self):
        self.assertEqual(self.metadata.get("X-Plasma-APIVersion"), "2")

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


class TestInstall(unittest.TestCase):
    def test_make_install_copies_package_byte_for_byte(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = install(tmp)
            self.assertEqual(result.returncode, 0, result.stderr)
            installed = os.path.join(
                tmp, "share", "plasma", "look-and-feel", LNF_ID
            )
            for name in ("metadata.json", os.path.join("contents", "defaults")):
                source = os.path.join(PACKAGE, name)
                target = os.path.join(installed, name)
                self.assertTrue(os.path.isfile(target), target)
                with open(source, "rb") as a, open(target, "rb") as b:
                    self.assertEqual(a.read(), b.read(), name)

    def test_make_install_is_repeatable(self):
        with tempfile.TemporaryDirectory() as tmp:
            first = install(tmp)
            self.assertEqual(first.returncode, 0, first.stderr)
            second = install(tmp)
            self.assertEqual(second.returncode, 0, second.stderr)

    def test_make_uninstall_removes_the_installed_package(self):
        with tempfile.TemporaryDirectory() as tmp:
            installed = install(tmp)
            self.assertEqual(installed.returncode, 0, installed.stderr)
            package = os.path.join(
                tmp, "share", "plasma", "look-and-feel", LNF_ID
            )
            self.assertTrue(os.path.isdir(package), package)

            removed = uninstall(tmp)
            self.assertEqual(removed.returncode, 0, removed.stderr)
            self.assertFalse(os.path.exists(package), package)

            again = uninstall(tmp)
            self.assertEqual(again.returncode, 0, again.stderr)

    def test_failed_reinstall_keeps_the_previous_package(self):
        """A copy that dies partway must not delete or damage the working install.

        `make install` replaces the package in place. If the copy fails after
        the old package was removed, Plasma is left with a partial theme; stage
        the copy and swap it in so a failure leaves the old package intact.
        """
        with tempfile.TemporaryDirectory() as tmp:
            first = install(tmp)
            self.assertEqual(first.returncode, 0, first.stderr)
            installed = os.path.join(
                tmp, "share", "plasma", "look-and-feel", LNF_ID
            )
            metadata = os.path.join(installed, "metadata.json")
            with open(metadata, "rb") as handle:
                good = handle.read()

            # Shadow `cp` with a fake that writes part of the tree, then fails,
            # simulating a copy killed or out of space halfway through.
            bindir = os.path.join(tmp, "fakebin")
            os.makedirs(bindir)
            fake_cp = os.path.join(bindir, "cp")
            with open(fake_cp, "w", encoding="utf-8") as handle:
                handle.write(
                    '#!/bin/sh\n'
                    '# Copy part of the tree, then die, like a killed `cp` would.\n'
                    'src="$2"\n'
                    'dest="$3/$(basename "$src")"\n'
                    'mkdir -p "$dest"\n'
                    'printf partial > "$dest/metadata.json"\n'
                    'exit 1\n'
                )
            os.chmod(fake_cp, 0o755)

            env = dict(os.environ)
            env["PATH"] = bindir + os.pathsep + os.environ.get("PATH", "")
            result = subprocess.run(
                ["make", "install", f"DESTDIR={tmp}", "XDG_DATA_HOME=/share"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                env=env,
            )
            self.assertNotEqual(result.returncode, 0, result.stdout)
            self.assertFalse(
                os.path.exists(
                    os.path.join(
                        tmp, "share", "plasma", "look-and-feel",
                        "." + LNF_ID + ".staging",
                    )
                ),
                "staging directory leaked after a failed install",
            )
            self.assertTrue(os.path.isdir(installed), installed)
            with open(metadata, "rb") as handle:
                self.assertEqual(handle.read(), good)

    def test_make_install_prunes_files_removed_from_the_package(self):
        """A reinstall must replace the package, not merge into the old one."""
        with tempfile.TemporaryDirectory() as tmp:
            first = install(tmp)
            self.assertEqual(first.returncode, 0, first.stderr)
            stale = os.path.join(
                tmp, "share", "plasma", "look-and-feel", LNF_ID,
                "contents", "removed.qml",
            )
            with open(stale, "w", encoding="utf-8") as handle:
                handle.write("// deleted from the package\n")
            second = install(tmp)
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertFalse(os.path.exists(stale), stale)


@unittest.skipUnless(shutil.which("kpackagetool6"), "needs kpackagetool6")
class TestPackageValid(unittest.TestCase):
    def test_kpackagetool6_installs_package(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                [
                    "kpackagetool6", "-t", "Plasma/LookAndFeel",
                    "-p", tmp, "-i", PACKAGE,
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(
                os.path.isfile(os.path.join(tmp, LNF_ID, "metadata.json"))
            )


if __name__ == "__main__":
    unittest.main()
