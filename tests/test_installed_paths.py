"""Direct tests for ``tests/support/installed_paths.py``'s install layout.

The package suites use these helpers as the oracle for where ``make install``
puts an artifact, and the color-scheme suite builds a killed install's hidden
leftovers through ``staging_sibling``/``old_sibling``. A helper that drifts
from the Makefile turns a suite's failure into a confusing missing-path or
unrelated-leftover report, because every assertion is written against the
helper. These tests derive the expected directories from the Makefile's own
``*_INSTALL_DIR`` definitions, so the test-side layout cannot disagree with
the recipe it checks.
"""

from __future__ import annotations

import os
import re
import unittest

from support import containment
from support import installed_paths
from support import repo_root

MAKEFILE = os.path.join(repo_root.ROOT, "Makefile")
DESTDIR = "/staging"
# One MAKE definition per line, e.g. ``LNF_INSTALL_DIR := $(DESTDIR)...``.
DEFINITION = re.compile(r"^([A-Z][A-Z0-9_]*)\s*:=\s*(.+?)\s*$", re.MULTILINE)
REFERENCE = re.compile(r"\$\(([A-Z][A-Z0-9_]*)\)")

# The Makefile's install directory for each helper that names a family.
FAMILY_HELPERS = {
    "INSTALL_DIR": installed_paths.installed_color_scheme_dir,
    "LNF_INSTALL_DIR": lambda destdir: installed_paths.installed_plasma_dir(
        destdir, "look-and-feel"
    ),
    "DTHEME_INSTALL_DIR": lambda destdir: installed_paths.installed_plasma_dir(
        destdir, "desktoptheme"
    ),
    "AURORAE_INSTALL_DIR": installed_paths.installed_aurorae_dir,
    "WALLPAPER_INSTALL_DIR": installed_paths.installed_wallpaper_dir,
    "ICON_THEME_INSTALL_DIR": installed_paths.installed_icons_dir,
    "FONT_INSTALL_DIR": installed_paths.installed_fonts_dir,
    "GTK_INSTALL_DIR": installed_paths.installed_gtk_theme,
}


def _definitions(text):
    """Return the Makefile's simple ``NAME := value`` definitions."""
    return dict(DEFINITION.findall(text))


def _expand(value, definitions, seen=()):
    """Expand ``$(NAME)`` references with the test's DESTDIR/XDG data home.

    ``DESTDIR`` and ``XDG_DATA_HOME`` are environment inputs, not Makefile
    definitions, so they get the values the helper is called with. Other names
    resolve through *definitions* (``GTK_ID`` and friends). A self-referential
    chain stops rather than recursing forever.
    """

    def replace(match):
        name = match.group(1)
        if name == "DESTDIR":
            return DESTDIR
        if name == "XDG_DATA_HOME":
            return installed_paths.XDG_DATA_HOME
        if name in definitions and name not in seen:
            return _expand(definitions[name], definitions, seen + (name,))
        return match.group(0)

    return REFERENCE.sub(replace, value)


class TestFamiliesMatchTheMakefile(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = containment.read_text(MAKEFILE, repo_root.ROOT)
        cls.definitions = _definitions(cls.text)

    def test_the_data_home_is_the_xdg_default_subtree(self):
        self.assertEqual(installed_paths.XDG_DATA_HOME, "/share")

    def test_each_family_directory_is_the_makefile_install_directory(self):
        for variable, helper in FAMILY_HELPERS.items():
            with self.subTest(variable=variable):
                self.assertIn(variable, self.definitions)
                expected = _expand(self.definitions[variable], self.definitions)
                self.assertEqual(helper(DESTDIR), expected)

    def test_package_helpers_append_the_package_id(self):
        for kind in ("look-and-feel", "desktoptheme"):
            with self.subTest(kind=kind):
                self.assertEqual(
                    installed_paths.installed_package(DESTDIR, kind, "an-id"),
                    os.path.join(
                        installed_paths.installed_plasma_dir(DESTDIR, kind),
                        "an-id",
                    ),
                )
        for helper, family in (
            (installed_paths.installed_aurorae_theme,
             installed_paths.installed_aurorae_dir),
            (installed_paths.installed_wallpaper,
             installed_paths.installed_wallpaper_dir),
            (installed_paths.installed_icon_theme,
             installed_paths.installed_icons_dir),
            (installed_paths.installed_font_package,
             installed_paths.installed_fonts_dir),
        ):
            with self.subTest(helper=helper.__name__):
                self.assertEqual(
                    helper(DESTDIR, "an-id"),
                    os.path.join(family(DESTDIR), "an-id"),
                )

    def test_the_color_scheme_helper_joins_the_file_name(self):
        directory = installed_paths.installed_color_scheme_dir(DESTDIR)
        self.assertEqual(
            installed_paths.installed_color_scheme(DESTDIR),
            os.path.join(directory, "MacOS8.colors"),
        )
        self.assertEqual(
            installed_paths.installed_color_scheme(DESTDIR, "Renamed.colors"),
            os.path.join(directory, "Renamed.colors"),
        )


class TestInstalledPackageLocation(unittest.TestCase):
    def test_defaults_resolve_from_kind_and_package_id(self):
        class Location(installed_paths.InstalledPackageLocation):
            KIND = "look-and-feel"
            PACKAGE_ID = "org.macos8.desktop"

        location = Location()
        self.assertEqual(
            location.installed_parent(DESTDIR),
            installed_paths.installed_plasma_dir(DESTDIR, "look-and-feel"),
        )
        self.assertEqual(
            location.installed_package_dir(DESTDIR),
            installed_paths.installed_package(
                DESTDIR, "look-and-feel", "org.macos8.desktop"
            ),
        )

    def test_a_suite_can_override_both_methods_together(self):
        class Location(installed_paths.InstalledPackageLocation):
            KIND = "desktoptheme"
            PACKAGE_ID = "elsewhere"

            def installed_parent(self, tmp):
                return installed_paths.installed_aurorae_dir(tmp)

            def installed_package_dir(self, tmp):
                return installed_paths.installed_aurorae_theme(
                    tmp, self.PACKAGE_ID
                )

        location = Location()
        self.assertEqual(
            location.installed_parent(DESTDIR),
            installed_paths.installed_aurorae_dir(DESTDIR),
        )
        self.assertEqual(
            location.installed_package_dir(DESTDIR),
            installed_paths.installed_aurorae_theme(DESTDIR, "elsewhere"),
        )


class TestHiddenSiblings(unittest.TestCase):
    def test_staging_and_old_names_have_the_makefile_shape(self):
        # `define install_package` stages `$(3)/.$(1).staging` and moves the
        # working copy to `$(3)/.$(1).old`; the leftover tests recreate those
        # exact siblings, so name them literally here.
        parent = "/data/plasma/look-and-feel"
        name = "org.macos8.desktop"
        self.assertEqual(
            installed_paths.staging_sibling(parent, name),
            os.path.join(parent, "." + name + ".staging"),
        )
        self.assertEqual(
            installed_paths.old_sibling(parent, name),
            os.path.join(parent, "." + name + ".old"),
        )

    def test_the_makefile_recipe_uses_the_same_sibling_names(self):
        text = containment.read_text(MAKEFILE, repo_root.ROOT)
        self.assertIn('staging="$(3)/.$(1).staging"', text)
        self.assertIn('old="$(3)/.$(1).old"', text)


if __name__ == "__main__":
    unittest.main()
