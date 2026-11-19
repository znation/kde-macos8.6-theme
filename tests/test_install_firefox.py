"""Tests for the Firefox profile install and profile-lock workflow.

The tool runs in-process with ``HOME`` pointed at a temp root, so the sheet
copy and the ``user.js`` edit are pinned without touching a real
Firefox profile. Profile resolution has its own suite in
``tests/test_firefox_profile.py`` and the ``user.js`` marker-block transform in
``tests/test_firefox_user_js.py``; the removal cases live in
``tests/test_remove_firefox.py``, and the shared temp-home case is
``support.firefox_profile_case``.
"""

from __future__ import annotations

import errno
import unittest
from pathlib import Path
from unittest import mock

from support import containment
from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.theme_install import write_file as _write
from support.firefox_profile_case import FirefoxProfileTestCase, read_utf8 as _read
from support.flock_fixtures import assert_directory_flock_free, hold_directory_flock
from support.process_assertions import assert_lock_time_out
from tools import (
    file_lock,
    firefox_profile_actions,
    firefox_user_files,
    firefox_user_js,
    install_firefox,
)

SHEET_PATH = Path(repo_root.ROOT) / install_firefox.SHEET
CONTENT_SHEET_PATH = Path(repo_root.ROOT) / install_firefox.CONTENT_SHEET


class TestInstall(FirefoxProfileTestCase):
    def test_install_refuses_a_symlinked_chrome_directory(self):
        outside = self.root / "outside-chrome"
        outside.mkdir()
        sentinel = outside / "keep.txt"
        sentinel.write_text("outside profile", encoding="utf-8")
        self.create_symlink(self.profile / "chrome", outside, target_is_directory=True)

        result = self.run_tool("--profile", str(self.profile))

        self.assertEqual(2, result.returncode)
        self.assertIn(f"cannot write {self.profile / 'chrome'}", result.stderr)
        self.assertIn("symbolic link", result.stderr)
        self.assertEqual("outside profile", sentinel.read_text(encoding="utf-8"))
        self.assertFalse((outside / "userChrome.css").exists())
        self.assertFalse((self.profile / "user.js").exists())

    def test_install_and_remove_through_a_symlinked_profile_directory(self):
        profile_link = self.root / "linked-profile"
        self.create_symlink(profile_link, self.profile, target_is_directory=True)
        foreign = 'user_pref("keep.me", "caf\u00e9");\r\n'
        _write(self.user_js_path(), foreign)

        result = self.run_tool("--profile", str(profile_link))
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertTrue(profile_link.is_symlink())
        self.assertEqual(self.profile, profile_link.readlink())
        self.assertEqual(
            containment.read_bytes(SHEET_PATH, repo_root.ROOT),
            self.sheet_path().read_bytes(),
        )
        self.assertEqual(
            containment.read_bytes(CONTENT_SHEET_PATH, repo_root.ROOT),
            self.content_sheet_path().read_bytes(),
        )
        self.assertEqual(
            foreign + self._owned_user_js_block("\r\n"),
            _read(self.user_js_path()),
        )

        result = self.run_tool("--remove", "--profile", str(profile_link))
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertTrue(profile_link.is_symlink())
        self.assertEqual(self.profile, profile_link.readlink())
        self.assert_profile_absent(self.sheet_path(), self.content_sheet_path())
        self.assertEqual(foreign.encode("utf-8"), self.user_js_path().read_bytes())

    def test_install_copies_the_sheets_byte_for_byte_and_adds_one_block(self):
        result = self.run_tool("--profile", str(self.profile))
        self.assertEqual(0, result.returncode, result.stderr)
        for shipped, installed in (
            (SHEET_PATH, self.sheet_path()),
            (CONTENT_SHEET_PATH, self.content_sheet_path()),
        ):
            with self.subTest(sheet=installed.name):
                self.assertEqual(
                    containment.read_bytes(shipped, repo_root.ROOT),
                    installed.read_bytes(),
                )
        user_js = _read(self.user_js_path())
        self.assertEqual(self._owned_user_js_block(), user_js)
        self.assertEqual(1, user_js.count(firefox_user_js.USER_JS_MARKER))

    def test_environment_profile_is_used_by_the_target(self):
        result = self.run_tool(
            env={"HOME": str(self.home), "FIREFOX_PROFILE": str(self.profile)}
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertTrue(self.sheet_path().is_file())

    def test_optional_install_without_a_profile_skips_with_a_note(self):
        # `make apply` passes --optional, so a machine without Firefox still
        # applies every other surface and says why this one was skipped.
        result = self.run_tool("--optional")
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("no Firefox profile found; skipping", result.stdout)
        self.assert_profile_absent(self.sheet_path(), self.user_js_path())

    def test_optional_install_uses_a_discovered_profile(self):
        profile = self.firefox_root / "Profiles" / "active.default"
        profile.mkdir(parents=True)
        _write(
            self.firefox_root / "profiles.ini",
            "[Profile0]\nName=active\nPath=Profiles/active.default\nDefault=1\n",
        )
        result = self.run_tool("--optional")
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertTrue(
            (profile / "chrome" / "userChrome.css").is_file()
        )
        self.assertIn(
            firefox_user_js.USER_JS_MARKER,
            (profile / "user.js").read_text(encoding="utf-8"),
        )

    def test_optional_install_still_refuses_a_named_missing_profile(self):
        missing = self.root / "missing-profile"
        result = self.run_tool("--optional", "--profile", str(missing))
        self.assertEqual(2, result.returncode)
        self.assertIn(str(missing), result.stderr)

    def test_repeat_install_does_not_duplicate_the_block(self):
        self.assertEqual(0, self.run_tool("--profile", str(self.profile)).returncode)
        first = _read(self.user_js_path())
        self.assertEqual(
            0, self.run_tool("--profile", str(self.profile)).returncode
        )
        self.assertEqual(first, _read(self.user_js_path()))

    def test_an_empty_sheet_is_adopted(self):
        # An empty file holds nothing to preserve, so it is ours to fill
        # instead of being refused as a foreign sheet.
        for empty in (self.sheet_path(), self.content_sheet_path()):
            with self.subTest(sheet=empty.name):
                profile = self.root / ("empty-" + empty.name)
                profile.mkdir()
                path = profile / "chrome" / empty.name
                _write(path, b"")
                result = self.run_tool("--profile", str(profile))
                self.assertEqual(0, result.returncode, result.stderr)
                shipped = (
                    SHEET_PATH
                    if empty.name == "userChrome.css"
                    else CONTENT_SHEET_PATH
                )
                self.assertEqual(
                    containment.read_bytes(shipped, repo_root.ROOT),
                    path.read_bytes(),
                )
                self.assertIn(
                    firefox_user_js.USER_JS_MARKER,
                    _read(profile / "user.js"),
                )

    def test_a_foreign_sheet_is_refused_and_nothing_is_written(self):
        for relative in ("chrome/userChrome.css", "chrome/userContent.css"):
            with self.subTest(sheet=relative):
                profile = self.root / ("foreign-" + relative.replace("/", "-"))
                profile.mkdir()
                foreign_path = profile / relative
                other = (
                    profile / "chrome" / "userContent.css"
                    if relative.endswith("userChrome.css")
                    else profile / "chrome" / "userChrome.css"
                )
                foreign = "/* my own sheet */\nbody { color: red; }\n"
                _write(foreign_path, foreign)
                result = self.run_tool("--profile", str(profile))
                self.assertEqual(1, result.returncode)
                self.assertIn(str(foreign_path), result.stderr)
                self.assertEqual(foreign, _read(foreign_path))
                self.assertFalse(other.exists())
                self.assertFalse((profile / "user.js").exists())

    def test_install_refuses_symlinked_profile_files_before_writing_anything(self):
        # A dotfile manager commonly makes one of these profile files a symlink
        # to a file it manages. Replacing that link with a regular file would
        # detach the profile from the file the user meant to edit, so every
        # destination is refused before any of the three is written.
        destinations = (
            "chrome/userChrome.css",
            "chrome/userContent.css",
            "user.js",
        )
        for relative in destinations:
            with self.subTest(path=relative):
                profile = self.root / ("linked-" + relative.replace("/", "-"))
                profile.mkdir()
                link = profile / relative
                link.parent.mkdir(parents=True, exist_ok=True)
                target = self.root / "dotfiles" / profile.name / Path(relative).name
                target.parent.mkdir(parents=True)
                original = (
                    b'user_pref("keep.me", true);\n'
                    if relative == "user.js"
                    else b""
                )
                target.write_bytes(original)
                self.create_symlink(link, target)

                result = self.run_tool("--profile", str(profile))

                self.assertEqual(2, result.returncode)
                self.assertIn(f"cannot write {link}", result.stderr)
                self.assertIn("symbolic link", result.stderr)
                # The refused link and the file it names are untouched, and
                # neither sibling destination was written.
                self.assertTrue(link.is_symlink())
                self.assertEqual(original, target.read_bytes())
                self._assert_siblings_unwritten(profile, destinations, relative)

    def _assert_siblings_unwritten(self, profile, destinations, relative):
        """Assert no destination but *relative* was written under *profile*."""
        for other in destinations:
            if other != relative:
                self.assertFalse((profile / other).exists())

    def test_install_refuses_dangling_profile_links_before_writing_anything(self):
        for relative in (
            "chrome/userChrome.css",
            "chrome/userContent.css",
            "user.js",
        ):
            with self.subTest(path=relative):
                profile = self.root / relative.replace("/", "-")
                profile.mkdir()
                sheet = profile / "chrome" / "userChrome.css"
                js = profile / "user.js"
                sheet.parent.mkdir()
                link = profile / relative
                sibling = js if link == sheet else sheet
                original = (
                    b'user_pref("keep.me", true);\r\n'
                    if sibling == js
                    else (install_firefox.CSS_MARKER + "\r\n/* old sheet */\r\n").encode()
                )
                sibling.write_bytes(original)
                target = self.root / (profile.name + "-missing")
                self.create_symlink(link, target)

                result = self.run_tool("--profile", str(profile))

                self.assertEqual(2, result.returncode)
                self.assertIn(f"install_firefox: error: cannot write {link}", result.stderr)
                self.assertIn("symbolic link", result.stderr)
                self.assertTrue(link.is_symlink())
                self.assertEqual(target, link.readlink())
                self.assertFalse(target.exists())
                self.assertEqual(original, sibling.read_bytes())
                self.assertEqual(
                    {sheet.parent, link, sibling},
                    set(profile.rglob("*")),
                )

    def test_a_bom_before_our_marker_keeps_the_sheet_ours(self):
        # A UTF-8 BOM is valid in CSS and some editors add one. It must not
        # make our marker-led sheet look foreign: the install replaces it with
        # the shipped sheet, and the removal deletes it.
        for relative, marker, shipped in (
            ("chrome/userChrome.css", install_firefox.CSS_MARKER, SHEET_PATH),
            (
                "chrome/userContent.css",
                install_firefox.CONTENT_CSS_MARKER,
                CONTENT_SHEET_PATH,
            ),
        ):
            with self.subTest(sheet=relative):
                profile = self.root / ("bom-" + relative.replace("/", "-"))
                profile.mkdir()
                path = profile / relative
                _write(path, f"\ufeff{marker}\nbody {{}}\n")
                result = self.run_tool("--profile", str(profile))
                self.assertEqual(0, result.returncode, result.stderr)
                self.assertEqual(
                    containment.read_bytes(shipped, repo_root.ROOT),
                    path.read_bytes(),
                )

    def test_an_uncreatable_chrome_directory_is_reported_by_path(self):
        # _apply promises a by-name "cannot create" error when the chrome
        # directory cannot be made, rather than a traceback. The directory
        # does not exist yet, so the earlier reads return None and the mkdir
        # is reached; fail only that call.
        with mock.patch.object(Path, "mkdir", side_effect=OSError("simulated failure")):
            result = self.run_tool("--profile", str(self.profile))
        self.assertEqual(2, result.returncode)
        self.assertIn(f"cannot create {self.sheet_path().parent}", result.stderr)
        self.assert_profile_absent(*self.owned_profile_paths())

    def test_a_failed_user_js_write_is_reported_by_path(self):
        # A write failure must name the file that failed and stop the install.
        # The sheet is published first, so the failure must remove it again:
        # a failed install leaves neither half of the pair behind.
        self.run_with_failed_write(self.user_js_path())
        self.assert_profile_absent(*self.owned_profile_paths())

    def test_a_failed_user_js_write_restores_both_previous_sheets(self):
        # A repeat install over earlier sheets of ours must not replace them
        # when the user.js write fails: each previous sheet is put back, not
        # deleted and not left as the new one.
        previous = f"{install_firefox.CSS_MARKER}\n/* previous sheet */\n"
        previous_content = (
            f"{install_firefox.CONTENT_CSS_MARKER}\n/* previous content */\n"
        )
        _write(self.sheet_path(), previous)
        _write(self.content_sheet_path(), previous_content)
        self.run_with_failed_write(self.user_js_path())
        self.assertEqual(previous, _read(self.sheet_path()))
        self.assertEqual(previous_content, _read(self.content_sheet_path()))
        self.assert_profile_absent(self.user_js_path())

    def test_a_failed_user_js_write_keeps_a_block_that_was_already_installed(self):
        # A repeat install over an outdated sheet rewrites a user.js that
        # already holds our block unchanged. When that write fails, the
        # sheet goes back to its previous text and the block stays in place.
        first = self.run_tool("--profile", str(self.profile))
        self.assertEqual(0, first.returncode, first.stderr)
        installed_js = _read(self.user_js_path())
        previous_sheet = f"{install_firefox.CSS_MARKER}\n/* outdated sheet */\n"
        _write(self.sheet_path(), previous_sheet)
        self.run_with_failed_write(self.user_js_path())
        self.assertEqual(previous_sheet, _read(self.sheet_path()))
        self.assertEqual(installed_js, _read(self.user_js_path()))

    def test_a_failed_sheet_restore_is_reported_with_the_original_error(self):
        # When the user.js write and the sheet restore both fail, the restore
        # cannot put the profile back. The error must name both failures so
        # the half-applied sheet is visible instead of reported as clean, and
        # the failed restore leaves the shipped sheet in place.
        previous = f"{install_firefox.CSS_MARKER}\n/* previous sheet */\n"
        _write(self.sheet_path(), previous)
        real_write = firefox_user_files.write_atomically
        sheet_writes = []

        def flaky_write(path, writer):
            if Path(path) == self.user_js_path():
                raise OSError("simulated user.js failure")
            if Path(path) == self.sheet_path():
                sheet_writes.append(path)
                if len(sheet_writes) > 1:
                    raise OSError("simulated restore failure")
            return real_write(path, writer)

        with mock.patch.object(firefox_user_files, "write_atomically", flaky_write):
            result = self.run_tool("--profile", str(self.profile))
        self.assertEqual(2, result.returncode)
        self.assertIn(f"cannot write {self.user_js_path()}", result.stderr)
        self.assertIn(f"cannot write {self.sheet_path()}", result.stderr)
        self.assertEqual(
            containment.read_bytes(SHEET_PATH, repo_root.ROOT),
            self.sheet_path().read_bytes(),
        )
        self.assert_profile_absent(self.user_js_path())

    def test_an_interrupt_during_the_user_js_write_restores_the_previous_sheet(self):
        # An interrupt is not a ConfigError, but it must roll the published
        # sheet back all the same and then propagate instead of being
        # swallowed; otherwise Ctrl-C leaves a half-installed profile.
        previous = f"{install_firefox.CSS_MARKER}\n/* previous sheet */\n"
        _write(self.sheet_path(), previous)
        with mock.patch.object(
            firefox_user_files,
            "write_atomically",
            self.interrupt_write_to(self.user_js_path()),
        ):
            with self.assertRaises(KeyboardInterrupt):
                self.run_tool("--profile", str(self.profile))
        self.assertEqual(previous, _read(self.sheet_path()))
        self.assert_profile_absent(self.content_sheet_path(), self.user_js_path())

    def test_an_interrupt_after_the_user_js_write_takes_effect_restores_it(self):
        # The user.js write can publish the preference block and then raise
        # before the call returns. The install must put the previous user.js
        # back as well as the sheet, so the pair is not left half-applied.
        previous_sheet = f"{install_firefox.CSS_MARKER}\n/* previous sheet */\n"
        previous_js = 'user_pref("keep.me", true);\n'
        _write(self.sheet_path(), previous_sheet)
        _write(self.user_js_path(), previous_js)
        with mock.patch.object(
            firefox_user_files,
            "write_atomically",
            self.interrupt_write_to(self.user_js_path(), after_publish=True),
        ):
            with self.assertRaises(KeyboardInterrupt):
                self.run_tool("--profile", str(self.profile))
        self.assertEqual(previous_sheet, _read(self.sheet_path()))
        self.assert_profile_absent(self.content_sheet_path())
        self.assertEqual(previous_js, _read(self.user_js_path()))

    def test_an_interrupt_after_a_created_user_js_is_published_removes_it(self):
        # A first install has no previous user.js, so when the write
        # publishes it and then raises, the rollback removes the file it
        # created instead of leaving the preference block behind.
        with mock.patch.object(
            firefox_user_files,
            "write_atomically",
            self.interrupt_write_to(self.user_js_path(), after_publish=True),
        ):
            with self.assertRaises(KeyboardInterrupt):
                self.run_tool("--profile", str(self.profile))
        self.assert_profile_absent(*self.owned_profile_paths())

    def test_a_failed_user_js_restore_is_reported_with_the_original_error(self):
        # The user.js write publishes and then raises, and putting the
        # previous user.js back fails too. The error must name both
        # failures, and the sheet is still rolled back.
        previous_sheet = f"{install_firefox.CSS_MARKER}\n/* previous sheet */\n"
        previous_js = 'user_pref("keep.me", true);\n'
        _write(self.sheet_path(), previous_sheet)
        _write(self.user_js_path(), previous_js)
        real_write = firefox_user_files.write_atomically
        js_writes = []

        def flaky_write(path, writer):
            if Path(path) == self.user_js_path():
                js_writes.append(path)
                if len(js_writes) > 1:
                    raise OSError("simulated user.js restore failure")
                real_write(path, writer)
                raise OSError("simulated user.js failure")
            return real_write(path, writer)

        with mock.patch.object(firefox_user_files, "write_atomically", flaky_write):
            result = self.run_tool("--profile", str(self.profile))
        self.assertEqual(2, result.returncode)
        self.assertIn("simulated user.js failure", result.stderr)
        self.assertIn("simulated user.js restore failure", result.stderr)
        self.assertEqual(previous_sheet, _read(self.sheet_path()))

    def test_an_interrupt_after_the_sheet_write_takes_effect_removes_it(self):
        # The sheet write can publish its file and then raise before the
        # caller records any state. A rollback flag set after the write would
        # miss that interrupt and leave the sheet behind; the install must
        # remove the sheet it just published and propagate the interrupt.
        with mock.patch.object(
            firefox_user_files,
            "write_atomically",
            self.interrupt_write_to(self.sheet_path(), after_publish=True),
        ):
            with self.assertRaises(KeyboardInterrupt):
                self.run_tool("--profile", str(self.profile))
        self.assert_profile_absent(*self.owned_profile_paths())

    def test_a_failed_new_sheet_restore_is_reported_with_the_original_error(self):
        # A first install has no previous sheet, so its rollback removes the
        # shipped sheet it published. If that unlink also fails, the error
        # must name both failures and the sheet that could not be removed
        # stays visible instead of the rollback failure being swallowed.
        with mock.patch.object(
            Path, "unlink", self.fail_unlink_to(self.sheet_path())
        ):
            result = self.run_with_failed_write(self.user_js_path())
        self.assertIn(f"cannot restore {self.sheet_path()}", result.stderr)
        self.assertEqual(
            containment.read_bytes(SHEET_PATH, repo_root.ROOT),
            self.sheet_path().read_bytes(),
        )
        self.assert_profile_absent(self.user_js_path())

    def test_a_failed_sheet_write_is_reported_by_path(self):
        # _apply publishes userChrome.css before user.js; a failure on that
        # first write must name the sheet and leave no user.js behind instead
        # of escaping as a traceback. The existing user.js write-failure test
        # pins the second publication; this pins the first.
        self.run_with_failed_write(self.sheet_path())
        self.assert_profile_absent(*self.owned_profile_paths())

    def test_a_failed_user_content_write_removes_the_published_user_chrome(self):
        # The content sheet is published after userChrome.css; a failure on
        # that second write must name the content path and roll the already
        # published chrome sheet back, leaving no user.js behind.
        self.run_with_failed_write(self.content_sheet_path())
        self.assert_profile_absent(*self.owned_profile_paths())

    def test_an_interrupt_after_the_user_content_write_takes_effect_removes_both(self):
        # The content-sheet write can publish its file and then raise before
        # the call returns. The rollback must remove that sheet as well as the
        # already published chrome sheet, and leave no user.js behind.
        with mock.patch.object(
            firefox_user_files,
            "write_atomically",
            self.interrupt_write_to(self.content_sheet_path(), after_publish=True),
        ):
            with self.assertRaises(KeyboardInterrupt):
                self.run_tool("--profile", str(self.profile))
        self.assert_profile_absent(*self.owned_profile_paths())

    def test_a_missing_shipped_sheet_is_reported_by_path(self):
        # apply_profile reads the shipped userChrome.css before touching the profile
        # and promises a by-name "cannot read" error rather than a traceback
        # when the source tree is incomplete. Point ROOT at a tree with no
        # theme/ directory; neither profile file may be written.
        with mock.patch.object(firefox_profile_actions, "ROOT", self.root):
            result = self.run_tool("--profile", str(self.profile))
        self.assertEqual(2, result.returncode)
        sheet = self.root / install_firefox.SHEET
        self.assertIn(f"cannot read {sheet}", result.stderr)
        self.assert_profile_absent(self.sheet_path(), self.user_js_path())

    def test_a_shipped_sheet_that_is_a_directory_is_reported_by_path(self):
        # The shared regular-file reader refuses a directory with a
        # ValueError; apply_profile must wrap that in the same by-name diagnostic.
        sheet = self.root / install_firefox.SHEET
        sheet.mkdir(parents=True)
        with mock.patch.object(firefox_profile_actions, "ROOT", self.root):
            result = self.run_tool("--profile", str(self.profile))
        self.assertEqual(2, result.returncode)
        self.assertIn(f"cannot read {sheet}", result.stderr)
        self.assertIn("not a regular file", result.stderr)
        self.assert_profile_absent(self.sheet_path(), self.user_js_path())

    def test_an_oversize_user_chrome_is_refused_by_name(self):
        # The existing sheet is read only to compare its first line, so a
        # multi-gigabyte file at that path must be refused by name after one
        # byte past the cap. Reading it whole would exhaust memory, and a
        # MemoryError is not an OSError, so it would escape as a traceback
        # instead of the documented exit 2. A sparse file keeps the test
        # cheap without changing what the reader sees.
        path = self.sheet_path()
        path.parent.mkdir(parents=True)
        with path.open("wb") as handle:
            handle.truncate(firefox_user_files.MAX_PROFILE_FILE_BYTES + 1)
        result = self.run_tool("--profile", str(self.profile))
        self.assertEqual(2, result.returncode, result.stderr)
        self.assertIn(str(path), result.stderr)
        self.assertIn("larger than", result.stderr)
        self.assertEqual(
            firefox_user_files.MAX_PROFILE_FILE_BYTES + 1, path.stat().st_size
        )
        self.assert_profile_absent(self.user_js_path())

    def test_an_oversize_user_js_is_refused_by_name(self):
        # user.js goes through the same reader, so its read is bounded too;
        # no sheet may be published before the refusal.
        path = self.user_js_path()
        with path.open("wb") as handle:
            handle.truncate(firefox_user_files.MAX_PROFILE_FILE_BYTES + 1)
        result = self.run_tool("--profile", str(self.profile))
        self.assertEqual(2, result.returncode, result.stderr)
        self.assertIn(str(path), result.stderr)
        self.assertIn("larger than", result.stderr)
        self.assert_profile_absent(self.sheet_path())

    def test_a_user_chrome_at_the_1_mib_cap_is_accepted(self):
        # One byte past the cap is refused; exactly 1 MiB is the accepted
        # boundary, so the documented cap is pinned by an actual file rather
        # than only by one past the private constant.
        cap = 1 << 20
        path = self.sheet_path()
        path.parent.mkdir(parents=True)
        first_line = (install_firefox.CSS_MARKER + "\n").encode("utf-8")
        path.write_bytes(first_line + b"x" * (cap - len(first_line)))
        result = self.run_tool("--profile", str(self.profile))
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(
            containment.read_bytes(SHEET_PATH, repo_root.ROOT),
            path.read_bytes(),
        )

    def test_an_install_that_would_grow_user_js_past_the_1_mib_cap_is_refused(
        self,
    ):
        # The reader accepts exactly 1 MiB, but appending our marker block to
        # a file at that boundary would make a user.js the reader itself
        # refuses; a successful install must never create that state, or
        # every later install and removal would exit 2 and strand the sheet.
        cap = 1 << 20
        path = self.user_js_path()
        original = b"x" * (cap - 1) + b"\n"
        path.write_bytes(original)
        result = self.run_tool("--profile", str(self.profile))
        self.assertEqual(2, result.returncode, result.stderr)
        self.assertIn(str(path), result.stderr)
        self.assertIn("1048576-byte limit", result.stderr)
        self.assertEqual(original, path.read_bytes())
        self.assert_profile_absent(self.sheet_path())


class TestProfileLock(FirefoxProfileTestCase):
    """Concurrent installs and removals serialize on the profile directory."""

    def hold_profile_lock(self):
        """Take the lock a concurrent run would hold, and release it after."""
        hold_directory_flock(self, self.profile)

    def test_install_times_out_without_writing_while_another_run_holds_the_lock(
        self,
    ):
        self.hold_profile_lock()

        with mock.patch.object(install_firefox, "LOCK_TIMEOUT", 0.05):
            result = self.run_tool("--profile", str(self.profile))

        assert_lock_time_out(
            self,
            result,
            "waiting for another install-firefox/remove-firefox",
            self.profile,
        )
        self.assert_profile_absent(*self.owned_profile_paths())

    def test_remove_times_out_without_clearing_the_install(self):
        installed = self.run_tool("--profile", str(self.profile))
        self.assertEqual(0, installed.returncode, installed.stderr)
        before_sheet = self.sheet_path().read_bytes()
        before_js = self.user_js_path().read_bytes()
        self.hold_profile_lock()

        with mock.patch.object(install_firefox, "LOCK_TIMEOUT", 0.05):
            result = self.run_tool("--remove", "--profile", str(self.profile))

        assert_lock_time_out(
            self,
            result,
            "waiting for another install-firefox/remove-firefox",
            self.profile,
        )
        self.assertEqual(before_sheet, self.sheet_path().read_bytes())
        self.assertEqual(before_js, self.user_js_path().read_bytes())

    def test_install_releases_the_lock_for_the_next_run(self):
        result = self.run_tool("--profile", str(self.profile))
        self.assertEqual(0, result.returncode, result.stderr)

        assert_directory_flock_free(self.profile)

    def test_install_refuses_when_the_profile_lock_cannot_be_opened(self):
        def refuse_open(*args, **kwargs):
            raise PermissionError(errno.EACCES, "simulated refusal")

        with mock.patch.object(install_firefox.os, "open", side_effect=refuse_open):
            result = self.run_tool("--profile", str(self.profile))

        self.assertEqual(2, result.returncode)
        self.assertIn(f"cannot lock {self.profile}", result.stderr)
        self.assertIn("simulated refusal", result.stderr)
        self.assert_profile_absent(self.sheet_path())

    def test_install_refuses_a_lock_that_fails_for_another_reason(self):
        def refuse_lock(*args, **kwargs):
            raise OSError(errno.EIO, "simulated failure")

        with mock.patch.object(
            file_lock.fcntl, "flock", side_effect=refuse_lock
        ):
            result = self.run_tool("--profile", str(self.profile))

        self.assertEqual(2, result.returncode)
        self.assertIn(f"cannot lock {self.profile}", result.stderr)
        self.assertIn("simulated failure", result.stderr)
        self.assert_profile_absent(self.sheet_path())


if __name__ == "__main__":
    unittest.main()
