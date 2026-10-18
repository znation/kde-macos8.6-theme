"""Tests for the org.macos8.desktop Aurorae package: metadata and install.

The `metadata.json` / `metadata.desktop` pair that KPackage and KWin's Aurorae
discovery read, the install lifecycle, and `kpackagetool6` acceptance. The
artwork the package ships is covered by `test_aurorae_frame`,
`test_aurorae_buttons` and `test_aurorae_rc`.
"""

from __future__ import annotations

import os
import shutil
import unittest

from support.aurorae_fixtures import AURORAE_DIR, AURORAE_ID
from support.install_failure_cases import FailedInstallPreservesPackage
from support.install_lifecycle_cases import InstallLifecycleCases
from support.kde_config import read as read_kde_config
from support.kpackage_install_case import KPackageInstallCase
from support.package_metadata import assert_named_authors, kplugin, load_metadata
from support.theme_install import installed_aurorae_dir, installed_aurorae_theme


METADATA = os.path.join(AURORAE_DIR, "metadata.json")
METADATA_DESKTOP = os.path.join(AURORAE_DIR, "metadata.desktop")


class TestMetadata(unittest.TestCase):
    def test_metadata_identifies_the_aurorae_package(self):
        metadata = load_metadata(METADATA)
        self.assertEqual(metadata["KPackageStructure"], "KWin/Aurorae")
        plugin = kplugin(metadata, METADATA)
        self.assertEqual(plugin["Id"], AURORAE_ID)
        self.assertEqual(plugin["Name"], "Mac OS 8.6")
        self.assertEqual(plugin["License"], "GPL-2.0-or-later")

    def test_metadata_desktop_names_the_theme(self):
        # KWin 6.3.6's Aurorae SVG-theme discovery
        # (`ThemeProvider::findAllSvgThemes`) lists only theme directories that
        # contain a `metadata.desktop`, and reads its `Name` for the visible
        # name. Without it the decoration is never offered in System Settings.
        parser = read_kde_config(METADATA_DESKTOP)
        self.assertEqual(parser.get("Desktop Entry", "Name"), "Mac OS 8.6")

    def test_metadata_desktop_matches_metadata_json(self):
        # metadata.json and metadata.desktop describe the same package to two
        # consumers -- KPackage and System Settings read the JSON, KWin's
        # Aurorae discovery reads the desktop file -- so their shared identity
        # fields must agree. Name is pinned on each file already, but nothing
        # checks the two files agree, and Version is pinned nowhere, so a
        # version bump that updates only one file would leave the two views
        # disagreeing silently. X-KDE-PluginInfo-Name is the KPlugin identity
        # (the theme directory name, the `org.macos8.desktoprc` stem and the id
        # the global theme's `[kwinrc]` defaults point KWin at), so pin it to
        # AURORAE_ID as well. The desktop file's `Comment` is the KPlugin
        # `Description` shown to the user, so a description edit that touches
        # only one file would show two different texts for one package.
        plugin = kplugin(load_metadata(METADATA), METADATA)
        parser = read_kde_config(METADATA_DESKTOP)
        for key, expected in (
            ("X-KDE-PluginInfo-Name", AURORAE_ID),
            ("X-KDE-PluginInfo-Version", plugin.get("Version")),
            ("X-KDE-PluginInfo-License", plugin.get("License")),
            ("Comment", plugin.get("Description")),
        ):
            self.assertEqual(
                parser.get("Desktop Entry", key),
                expected,
                f"{METADATA_DESKTOP}: {key} must match {METADATA}",
            )
        # The desktop file's `X-KDE-PluginInfo-Author` is one string; the JSON
        # `KPlugin.Authors` is the list KDE's About dialog reads. Both name the
        # package's author, so the desktop file's name must be one of them, or
        # the two consumers disagree. `assert_named_authors` validates the list
        # shape first (nothing else checks the Aurorae metadata.json's Authors)
        # and returns the names it accepted.
        authors = assert_named_authors(self, plugin.get("Authors"), METADATA)
        self.assertIn(
            parser.get("Desktop Entry", "X-KDE-PluginInfo-Author"),
            authors,
            f"{METADATA_DESKTOP}: X-KDE-PluginInfo-Author must name one of "
            f"{METADATA}'s KPlugin.Authors",
        )


class TestInstall(
    FailedInstallPreservesPackage, InstallLifecycleCases, unittest.TestCase
):
    KIND = "aurorae"
    PACKAGE_ID = AURORAE_ID
    PACKAGE_DIR = AURORAE_DIR
    INSTALLED_FILES = (
        "metadata.json",
        "metadata.desktop",
        "org.macos8.desktoprc",
        "decoration.svg",
        "decoration.svgz",
        "close.svg",
        "maximize.svg",
        "restore.svg",
        "shade.svg",
    )
    COPY_FAILURE_GLOB = "*/aurorae/themes/*"

    def installed_parent(self, tmp):
        return installed_aurorae_dir(tmp)

    def installed_package_dir(self, tmp):
        return installed_aurorae_theme(tmp, self.PACKAGE_ID)


@unittest.skipUnless(shutil.which("kpackagetool6"), "needs kpackagetool6")
class TestPackageValid(KPackageInstallCase, unittest.TestCase):
    KPACKAGETOOL_TYPE = "KWin/Aurorae"
    PACKAGE_DIR = AURORAE_DIR
    PACKAGE_ID = AURORAE_ID

if __name__ == "__main__":
    unittest.main()
