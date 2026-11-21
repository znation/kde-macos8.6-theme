"""Tests for Konsole profile resolution and the font write.

The helper runs stub Konsole tools against a scratch XDG home. Shared stubs
live in ``support/konsole_font_case.py``; refusal cases live in
``test_apply_konsole_font_refusals.py``.
"""

from __future__ import annotations

import unittest
from pathlib import Path

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.konsole_font_case import (
    FOREIGN_PROFILE,
    StubKonsoleToolsTestCase,
)
from tools import apply_konsole_font
from tools.apply_theme import FIXED_VALUE as FONT


class TestUserDefault(StubKonsoleToolsTestCase):
    def setUp(self):
        super().setUp()
        self.write_konsolerc("[Desktop Entry]\nDefaultProfile=Mine.profile\n")
        self.profile = self.write_profile(self.data, "Mine.profile", FOREIGN_PROFILE)

    def test_a_user_default_profile_gets_the_font(self):
        status, stderr = self.apply_font()
        self.assertIsNone(status, stderr)
        text = self.read(self.profile)
        self.assertIn(f"Font={FONT}\n", text)
        self.assertNotIn("Liberation Mono", text)

    def test_only_the_font_entry_changes(self):
        # Every other key -- the profile name, its shell command, its key
        # tab (Konsole's keyboard mapping) and its interaction options --
        # must survive a font apply untouched, in place.
        before = self.without_font_lines(self.read(self.profile))
        status, stderr = self.apply_font()
        self.assertIsNone(status, stderr)
        self.assertEqual(
            before, self.without_font_lines(self.read(self.profile))
        )

    def test_konsolerc_is_untouched(self):
        before = self.read(self.konsolerc)
        status, stderr = self.apply_font()
        self.assertIsNone(status, stderr)
        self.assertEqual(before, self.read(self.konsolerc))

    def test_a_repeat_apply_leaves_the_profile_the_same(self):
        status, stderr = self.apply_font()
        self.assertIsNone(status, stderr)
        once = self.read(self.profile)
        status, stderr = self.apply_font()
        self.assertIsNone(status, stderr)
        self.assertEqual(once, self.read(self.profile))


class TestSystemDefault(StubKonsoleToolsTestCase):
    def setUp(self):
        super().setUp()
        self.write_konsolerc("[Desktop Entry]\nDefaultProfile=Mine.profile\n")
        self.system_profile = self.write_profile(
            self.system, "Mine.profile", FOREIGN_PROFILE
        )
        self.local_profile = self.profile_dir / "Mine.profile"

    def test_a_system_default_profile_is_copied_then_edited(self):
        before = self.system_profile.read_bytes()
        status, stderr = self.apply_font()
        self.assertIsNone(status, stderr)
        self.assertEqual(before, self.system_profile.read_bytes())
        self.assertEqual(
            self.without_font_lines(FOREIGN_PROFILE),
            self.without_font_lines(self.read(self.local_profile)),
        )
        self.assertIn(f"Font={FONT}\n", self.read(self.local_profile))

    def test_a_data_home_profile_shadows_the_same_named_system_one(self):
        # Konsole reads konsole/ under the data home first, so an existing
        # local profile is the one new sessions load: it is edited in place
        # and no copy may overwrite the user's edits with the system text.
        marker = FOREIGN_PROFILE.replace(
            "[Appearance]", "[General]\nExtra=user edit\n\n[Appearance]", 1
        )
        self.write_profile(self.data, "Mine.profile", marker)
        before = self.system_profile.read_bytes()
        status, stderr = self.apply_font()
        self.assertIsNone(status, stderr)
        self.assertEqual(before, self.system_profile.read_bytes())
        text = self.read(self.local_profile)
        self.assertIn("Extra=user edit\n", text)
        self.assertIn(f"Font={FONT}\n", text)

    def test_a_repeat_apply_keeps_the_earlier_copy(self):
        status, stderr = self.apply_font()
        self.assertIsNone(status, stderr)
        copied = self.local_profile.read_bytes()
        status, stderr = self.apply_font()
        self.assertIsNone(status, stderr)
        self.assertEqual(copied, self.local_profile.read_bytes())
        self.assertNotEqual(
            self.system_profile.read_bytes(), self.local_profile.read_bytes()
        )

    def test_other_profiles_are_untouched(self):
        other = self.write_profile(
            self.data, "Other.profile", FOREIGN_PROFILE
        )
        before = other.read_bytes()
        status, stderr = self.apply_font()
        self.assertIsNone(status, stderr)
        self.assertEqual(before, other.read_bytes())


class TestFallback(StubKonsoleToolsTestCase):
    def test_an_unset_default_creates_and_selects_the_platinum_profile(self):
        self.write_konsolerc("[General]\nColorScheme=BreezeLight\n")
        status, stderr = self.apply_font()
        self.assertIsNone(status, stderr)
        profile = self.profile_dir / "Platinum.profile"
        text = self.read(profile)
        self.assertIn("Name=Platinum\n", text)
        self.assertIn("Parent=FALLBACK/\n", text)
        self.assertIn(f"Font={FONT}\n", text)
        self.assertEqual(
            "[General]\nColorScheme=BreezeLight\n\n"
            "[Desktop Entry]\nDefaultProfile=Platinum.profile\n",
            self.read(self.konsolerc),
        )

    def test_a_missing_config_home_is_created_before_the_selection(self):
        # A first-time user has no config home yet: the fallback branch
        # creates it, so the konsolerc selection write cannot fail on a
        # missing parent directory.
        status, stderr = self.apply_font()
        self.assertIsNone(status, stderr)
        self.assertTrue(self.konsolerc.is_file(), self.konsolerc)
        self.assertIn(
            "[Desktop Entry]\nDefaultProfile=Platinum.profile\n",
            self.read(self.konsolerc),
        )

    def test_a_repeat_apply_rewrites_the_same_keys(self):
        status, stderr = self.apply_font()
        self.assertIsNone(status, stderr)
        konsolerc = self.read(self.konsolerc)
        profile = self.read(self.profile_dir / "Platinum.profile")
        status, stderr = self.apply_font()
        self.assertIsNone(status, stderr)
        self.assertEqual(konsolerc, self.read(self.konsolerc))
        self.assertEqual(profile, self.read(self.profile_dir / "Platinum.profile"))
        for key in ("Name", "Parent", "Font"):
            with self.subTest(key=key):
                self.assertEqual(
                    1,
                    sum(
                        1
                        for line in profile.splitlines()
                        if line.startswith(key + "=")
                    ),
                    profile,
                )

    def test_an_explicit_platinum_default_only_writes_the_font(self):
        # Once the fallback profile exists and is selected, the next apply
        # takes the named-profile path: konsolerc keeps naming the profile
        # and only the font entry is rewritten.
        self.apply_font()
        profile = self.profile_dir / "Platinum.profile"
        konsolerc = self.read(self.konsolerc)
        status, stderr = self.apply_font()
        self.assertIsNone(status, stderr)
        self.assertEqual(konsolerc, self.read(self.konsolerc))
        self.assertIn(f"Font={FONT}\n", self.read(profile))


class TestSearchBases(StubKonsoleToolsTestCase):
    """The profile search visits the data home, then absolute XDG_DATA_DIRS.

    Relative and empty entries are invalid under the XDG Base Directory spec,
    so they are skipped; an unset or empty XDG_DATA_DIRS means the spec's
    default pair, ``/usr/local/share`` then ``/usr/share``.
    """

    def test_an_unset_data_dirs_searches_the_spec_defaults(self):
        bases = apply_konsole_font._search_bases({}, self.data)
        self.assertEqual(
            bases, [self.data, Path("/usr/local/share"), Path("/usr/share")]
        )

    def test_an_empty_data_dirs_searches_the_spec_defaults(self):
        bases = apply_konsole_font._search_bases({"XDG_DATA_DIRS": ""}, self.data)
        self.assertEqual(
            bases, [self.data, Path("/usr/local/share"), Path("/usr/share")]
        )

    def test_relative_and_empty_entries_are_skipped(self):
        env = {"XDG_DATA_DIRS": "relative/share::/opt/share:"}
        bases = apply_konsole_font._search_bases(env, self.data)
        self.assertEqual(bases, [self.data, Path("/opt/share")])

    def test_only_relative_entries_leave_the_data_home_alone(self):
        bases = apply_konsole_font._search_bases(
            {"XDG_DATA_DIRS": "relative/share"}, self.data
        )
        self.assertEqual(bases, [self.data])


if __name__ == "__main__":
    unittest.main()
