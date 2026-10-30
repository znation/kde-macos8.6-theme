"""Tests for the Firefox profile install and removal workflow.

The tool runs in-process with ``HOME`` pointed at a temp root, so the sheet
copy, the ``user.js`` edit and the removal are pinned without touching a real
Firefox profile. Profile resolution has its own suite in
``tests/test_firefox_profile.py`` and the ``user.js`` marker-block transform in
``tests/test_firefox_user_js.py``; the shared temp-home case is
``support.firefox_profile_case``.
"""

from __future__ import annotations

import errno
import fcntl
import os
import unittest
from pathlib import Path
from unittest import mock

from support import containment, snippet_child
from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.fifo_fixtures import assert_fifo_refused, make_fifo
from support.firefox_profile_case import FirefoxProfileTestCase
from tools import file_lock, firefox_user_files, firefox_user_js, install_firefox

SHEET_PATH = Path(repo_root.ROOT) / install_firefox.SHEET
CONTENT_SHEET_PATH = Path(repo_root.ROOT) / install_firefox.CONTENT_SHEET


def _read(path):
    return path.read_bytes().decode("utf-8")


def _write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))

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
            foreign + firefox_user_js.USER_JS_MARKER + "\r\n"
            + firefox_user_js.PREF_LINE + "\r\n",
            _read(self.user_js_path()),
        )

        result = self.run_tool("--remove", "--profile", str(profile_link))
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertTrue(profile_link.is_symlink())
        self.assertEqual(self.profile, profile_link.readlink())
        self.assertFalse(self.sheet_path().exists())
        self.assertFalse(self.content_sheet_path().exists())
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
        self.assertEqual(
            firefox_user_js.USER_JS_MARKER
            + "\n"
            + firefox_user_js.PREF_LINE
            + "\n",
            user_js,
        )
        self.assertEqual(1, user_js.count(firefox_user_js.USER_JS_MARKER))

    def test_environment_profile_is_used_by_the_target(self):
        result = self.run_tool(
            env={"HOME": str(self.home), "FIREFOX_PROFILE": str(self.profile)}
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertTrue(self.sheet_path().is_file())

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
                path.parent.mkdir(parents=True)
                path.write_bytes(b"")
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
        self.assertFalse(self.sheet_path().exists())
        self.assertFalse(self.content_sheet_path().exists())
        self.assertFalse(self.user_js_path().exists())

    def test_a_failed_user_js_write_is_reported_by_path(self):
        # A write failure must name the file that failed and stop the install.
        # The sheet is published first, so the failure must remove it again:
        # a failed install leaves neither half of the pair behind.
        with mock.patch.object(
            firefox_user_files,
            "write_atomically",
            self.fail_write_to(self.user_js_path()),
        ):
            result = self.run_tool("--profile", str(self.profile))
        self.assertEqual(2, result.returncode)
        self.assertIn(f"cannot write {self.user_js_path()}", result.stderr)
        self.assertFalse(self.sheet_path().exists())
        self.assertFalse(self.content_sheet_path().exists())
        self.assertFalse(self.user_js_path().exists())

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
        with mock.patch.object(
            firefox_user_files,
            "write_atomically",
            self.fail_write_to(self.user_js_path()),
        ):
            result = self.run_tool("--profile", str(self.profile))
        self.assertEqual(2, result.returncode)
        self.assertIn(f"cannot write {self.user_js_path()}", result.stderr)
        self.assertEqual(previous, _read(self.sheet_path()))
        self.assertEqual(previous_content, _read(self.content_sheet_path()))
        self.assertFalse(self.user_js_path().exists())

    def test_a_failed_user_js_write_keeps_a_block_that_was_already_installed(self):
        # A repeat install over an outdated sheet rewrites a user.js that
        # already holds our block unchanged. When that write fails, the
        # sheet goes back to its previous text and the block stays in place.
        first = self.run_tool("--profile", str(self.profile))
        self.assertEqual(0, first.returncode, first.stderr)
        installed_js = _read(self.user_js_path())
        previous_sheet = f"{install_firefox.CSS_MARKER}\n/* outdated sheet */\n"
        _write(self.sheet_path(), previous_sheet)
        with mock.patch.object(
            firefox_user_files,
            "write_atomically",
            self.fail_write_to(self.user_js_path()),
        ):
            result = self.run_tool("--profile", str(self.profile))
        self.assertEqual(2, result.returncode)
        self.assertIn(f"cannot write {self.user_js_path()}", result.stderr)
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
        self.assertFalse(self.user_js_path().exists())

    def test_an_interrupt_during_the_user_js_write_restores_the_previous_sheet(self):
        # An interrupt is not a ConfigError, but it must roll the published
        # sheet back all the same and then propagate instead of being
        # swallowed; otherwise Ctrl-C leaves a half-installed profile.
        previous = f"{install_firefox.CSS_MARKER}\n/* previous sheet */\n"
        _write(self.sheet_path(), previous)
        real_write = firefox_user_files.write_atomically

        def interrupt_the_user_js_write(path, writer):
            if Path(path) == self.user_js_path():
                raise KeyboardInterrupt
            return real_write(path, writer)

        with mock.patch.object(
            firefox_user_files, "write_atomically", interrupt_the_user_js_write
        ):
            with self.assertRaises(KeyboardInterrupt):
                self.run_tool("--profile", str(self.profile))
        self.assertEqual(previous, _read(self.sheet_path()))
        self.assertFalse(self.content_sheet_path().exists())
        self.assertFalse(self.user_js_path().exists())

    def test_an_interrupt_after_the_user_js_write_takes_effect_restores_it(self):
        # The user.js write can publish the preference block and then raise
        # before the call returns. The install must put the previous user.js
        # back as well as the sheet, so the pair is not left half-applied.
        previous_sheet = f"{install_firefox.CSS_MARKER}\n/* previous sheet */\n"
        previous_js = 'user_pref("keep.me", true);\n'
        _write(self.sheet_path(), previous_sheet)
        _write(self.user_js_path(), previous_js)
        real_write = firefox_user_files.write_atomically

        def interrupt_after_the_user_js_write(path, writer):
            if Path(path) == self.user_js_path():
                real_write(path, writer)
                raise KeyboardInterrupt
            return real_write(path, writer)

        with mock.patch.object(
            firefox_user_files, "write_atomically", interrupt_after_the_user_js_write
        ):
            with self.assertRaises(KeyboardInterrupt):
                self.run_tool("--profile", str(self.profile))
        self.assertEqual(previous_sheet, _read(self.sheet_path()))
        self.assertFalse(self.content_sheet_path().exists())
        self.assertEqual(previous_js, _read(self.user_js_path()))

    def test_an_interrupt_after_a_created_user_js_is_published_removes_it(self):
        # A first install has no previous user.js, so when the write
        # publishes it and then raises, the rollback removes the file it
        # created instead of leaving the preference block behind.
        real_write = firefox_user_files.write_atomically

        def interrupt_after_the_user_js_write(path, writer):
            if Path(path) == self.user_js_path():
                real_write(path, writer)
                raise KeyboardInterrupt
            return real_write(path, writer)

        with mock.patch.object(
            firefox_user_files, "write_atomically", interrupt_after_the_user_js_write
        ):
            with self.assertRaises(KeyboardInterrupt):
                self.run_tool("--profile", str(self.profile))
        self.assertFalse(self.sheet_path().exists())
        self.assertFalse(self.content_sheet_path().exists())
        self.assertFalse(self.user_js_path().exists())

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
        real_write = firefox_user_files.write_atomically

        def interrupt_after_the_sheet_write(path, writer):
            if Path(path) == self.sheet_path():
                real_write(path, writer)
                raise KeyboardInterrupt
            return real_write(path, writer)

        with mock.patch.object(
            firefox_user_files, "write_atomically", interrupt_after_the_sheet_write
        ):
            with self.assertRaises(KeyboardInterrupt):
                self.run_tool("--profile", str(self.profile))
        self.assertFalse(self.sheet_path().exists())
        self.assertFalse(self.content_sheet_path().exists())
        self.assertFalse(self.user_js_path().exists())

    def test_a_failed_new_sheet_restore_is_reported_with_the_original_error(self):
        # A first install has no previous sheet, so its rollback removes the
        # shipped sheet it published. If that unlink also fails, the error
        # must name both failures and the sheet that could not be removed
        # stays visible instead of the rollback failure being swallowed.
        with mock.patch.object(
            firefox_user_files,
            "write_atomically",
            self.fail_write_to(self.user_js_path()),
        ), mock.patch.object(
            Path, "unlink", self.fail_unlink_to(self.sheet_path())
        ):
            result = self.run_tool("--profile", str(self.profile))
        self.assertEqual(2, result.returncode)
        self.assertIn(f"cannot write {self.user_js_path()}", result.stderr)
        self.assertIn(f"cannot restore {self.sheet_path()}", result.stderr)
        self.assertEqual(
            containment.read_bytes(SHEET_PATH, repo_root.ROOT),
            self.sheet_path().read_bytes(),
        )
        self.assertFalse(self.user_js_path().exists())

    def test_a_failed_sheet_write_is_reported_by_path(self):
        # _apply publishes userChrome.css before user.js; a failure on that
        # first write must name the sheet and leave no user.js behind instead
        # of escaping as a traceback. The existing user.js write-failure test
        # pins the second publication; this pins the first.
        with mock.patch.object(
            firefox_user_files,
            "write_atomically",
            self.fail_write_to(self.sheet_path()),
        ):
            result = self.run_tool("--profile", str(self.profile))
        self.assertEqual(2, result.returncode)
        self.assertIn(f"cannot write {self.sheet_path()}", result.stderr)
        self.assertFalse(self.sheet_path().exists())
        self.assertFalse(self.content_sheet_path().exists())
        self.assertFalse(self.user_js_path().exists())

    def test_a_failed_user_content_write_removes_the_published_user_chrome(self):
        # The content sheet is published after userChrome.css; a failure on
        # that second write must name the content path and roll the already
        # published chrome sheet back, leaving no user.js behind.
        with mock.patch.object(
            firefox_user_files,
            "write_atomically",
            self.fail_write_to(self.content_sheet_path()),
        ):
            result = self.run_tool("--profile", str(self.profile))
        self.assertEqual(2, result.returncode)
        self.assertIn(f"cannot write {self.content_sheet_path()}", result.stderr)
        self.assertFalse(self.sheet_path().exists())
        self.assertFalse(self.content_sheet_path().exists())
        self.assertFalse(self.user_js_path().exists())

    def test_an_interrupt_after_the_user_content_write_takes_effect_removes_both(self):
        # The content-sheet write can publish its file and then raise before
        # the call returns. The rollback must remove that sheet as well as the
        # already published chrome sheet, and leave no user.js behind.
        real_write = firefox_user_files.write_atomically

        def interrupt_after_the_content_write(path, writer):
            if Path(path) == self.content_sheet_path():
                real_write(path, writer)
                raise KeyboardInterrupt
            return real_write(path, writer)

        with mock.patch.object(
            firefox_user_files, "write_atomically", interrupt_after_the_content_write
        ):
            with self.assertRaises(KeyboardInterrupt):
                self.run_tool("--profile", str(self.profile))
        self.assertFalse(self.sheet_path().exists())
        self.assertFalse(self.content_sheet_path().exists())
        self.assertFalse(self.user_js_path().exists())

    def test_a_missing_shipped_sheet_is_reported_by_path(self):
        # _apply reads the shipped userChrome.css before touching the profile
        # and promises a by-name "cannot read" error rather than a traceback
        # when the source tree is incomplete. Point ROOT at a tree with no
        # theme/ directory; neither profile file may be written.
        with mock.patch.object(install_firefox, "ROOT", self.root):
            result = self.run_tool("--profile", str(self.profile))
        self.assertEqual(2, result.returncode)
        sheet = self.root / install_firefox.SHEET
        self.assertIn(f"cannot read {sheet}", result.stderr)
        self.assertFalse(self.sheet_path().exists())
        self.assertFalse(self.user_js_path().exists())

    def test_a_shipped_sheet_that_is_a_directory_is_reported_by_path(self):
        # The shared regular-file reader refuses a directory with a
        # ValueError; _apply must wrap that in the same by-name diagnostic.
        sheet = self.root / install_firefox.SHEET
        sheet.mkdir(parents=True)
        with mock.patch.object(install_firefox, "ROOT", self.root):
            result = self.run_tool("--profile", str(self.profile))
        self.assertEqual(2, result.returncode)
        self.assertIn(f"cannot read {sheet}", result.stderr)
        self.assertIn("not a regular file", result.stderr)
        self.assertFalse(self.sheet_path().exists())
        self.assertFalse(self.user_js_path().exists())

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
        self.assertFalse(self.user_js_path().exists())

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
        self.assertFalse(self.sheet_path().exists())

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
        self.assertFalse(self.sheet_path().exists())


class TestProfileLock(FirefoxProfileTestCase):
    """Concurrent installs and removals serialize on the profile directory."""

    def hold_profile_lock(self):
        """Take the lock a concurrent run would hold, and release it after."""
        descriptor = os.open(
            self.profile, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
        )
        fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        self.addCleanup(os.close, descriptor)

    def test_install_times_out_without_writing_while_another_run_holds_the_lock(
        self,
    ):
        self.hold_profile_lock()

        with mock.patch.object(install_firefox, "LOCK_TIMEOUT", 0.05):
            result = self.run_tool("--profile", str(self.profile))

        self.assertEqual(2, result.returncode)
        self.assertIn(
            "waiting for another install-firefox/remove-firefox", result.stderr
        )
        self.assertIn(str(self.profile), result.stderr)
        self.assertFalse(self.sheet_path().exists())
        self.assertFalse(self.content_sheet_path().exists())
        self.assertFalse(self.user_js_path().exists())

    def test_remove_times_out_without_clearing_the_install(self):
        installed = self.run_tool("--profile", str(self.profile))
        self.assertEqual(0, installed.returncode, installed.stderr)
        before_sheet = self.sheet_path().read_bytes()
        before_js = self.user_js_path().read_bytes()
        self.hold_profile_lock()

        with mock.patch.object(install_firefox, "LOCK_TIMEOUT", 0.05):
            result = self.run_tool("--remove", "--profile", str(self.profile))

        self.assertEqual(2, result.returncode)
        self.assertIn(
            "waiting for another install-firefox/remove-firefox", result.stderr
        )
        self.assertEqual(before_sheet, self.sheet_path().read_bytes())
        self.assertEqual(before_js, self.user_js_path().read_bytes())

    def test_install_releases_the_lock_for_the_next_run(self):
        result = self.run_tool("--profile", str(self.profile))
        self.assertEqual(0, result.returncode, result.stderr)

        descriptor = os.open(
            self.profile, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
        )
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        finally:
            os.close(descriptor)

    def test_install_refuses_when_the_profile_lock_cannot_be_opened(self):
        def refuse_open(*args, **kwargs):
            raise PermissionError(errno.EACCES, "simulated refusal")

        with mock.patch.object(install_firefox.os, "open", side_effect=refuse_open):
            result = self.run_tool("--profile", str(self.profile))

        self.assertEqual(2, result.returncode)
        self.assertIn(f"cannot lock {self.profile}", result.stderr)
        self.assertIn("simulated refusal", result.stderr)
        self.assertFalse(self.sheet_path().exists())

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
        self.assertFalse(self.sheet_path().exists())


class TestRemove(FirefoxProfileTestCase):
    def test_remove_refuses_a_symlinked_chrome_directory(self):
        outside = self.root / "outside-chrome"
        outside.mkdir()
        sheet = outside / "userChrome.css"
        sheet.write_text(
            f"{install_firefox.CSS_MARKER}\nbody {{}}\n", encoding="utf-8"
        )
        self.create_symlink(self.profile / "chrome", outside, target_is_directory=True)
        js_text = (
            firefox_user_js.USER_JS_MARKER + "\n"
            + firefox_user_js.PREF_LINE + "\n"
        )
        _write(self.user_js_path(), js_text)

        result = self.run_tool("--remove", "--profile", str(self.profile))

        self.assertEqual(2, result.returncode)
        self.assertIn(f"cannot remove {self.profile / 'chrome'}", result.stderr)
        self.assertIn("symbolic link", result.stderr)
        self.assertTrue(sheet.is_file())
        self.assertEqual(js_text, _read(self.user_js_path()))

    def install(self):
        result = self.run_tool("--profile", str(self.profile))
        self.assertEqual(0, result.returncode, result.stderr)

    def test_remove_deletes_our_sheets_and_block_and_keeps_the_directory(self):
        self.install()
        result = self.run_tool("--remove", "--profile", str(self.profile))
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertFalse(self.sheet_path().exists())
        self.assertFalse(self.content_sheet_path().exists())
        self.assertTrue(self.sheet_path().parent.is_dir())
        self.assertEqual("", _read(self.user_js_path()))
        self.assertEqual(
            {self.sheet_path().parent, self.user_js_path()},
            set(self.profile.rglob("*")),
        )

    def test_remove_is_repeatable(self):
        self.install()
        self.assertEqual(
            0, self.run_tool("--remove", "--profile", str(self.profile)).returncode
        )
        self.assertEqual(
            0, self.run_tool("--remove", "--profile", str(self.profile)).returncode
        )

    def test_remove_after_install_at_the_1_mib_user_js_boundary(self):
        # A user.js whose marker block keeps it at exactly 1 MiB is accepted
        # by the reader; installing must leave it readable so removal can
        # reverse the block and restore the foreign line.
        cap = 1 << 20
        block = (
            firefox_user_js.USER_JS_MARKER
            + "\n"
            + firefox_user_js.PREF_LINE
            + "\n"
        )
        foreign = "x" * (cap - len(block.encode("utf-8")) - 1) + "\n"
        _write(self.user_js_path(), foreign + block)
        self.assertEqual(cap, self.user_js_path().stat().st_size)
        self.install()
        self.assertEqual(cap, self.user_js_path().stat().st_size)
        result = self.run_tool("--remove", "--profile", str(self.profile))
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(foreign, _read(self.user_js_path()))

    def test_remove_deletes_bom_prefixed_our_sheets(self):
        for relative, marker in (
            ("chrome/userChrome.css", install_firefox.CSS_MARKER),
            ("chrome/userContent.css", install_firefox.CONTENT_CSS_MARKER),
        ):
            with self.subTest(sheet=relative):
                profile = self.root / ("bom-remove-" + relative.replace("/", "-"))
                profile.mkdir()
                path = profile / relative
                _write(path, f"\ufeff{marker}\nbody {{}}\n")
                block = (
                    firefox_user_js.USER_JS_MARKER
                    + "\n"
                    + firefox_user_js.PREF_LINE
                    + "\n"
                )
                _write(profile / "user.js", block)

                result = self.run_tool("--remove", "--profile", str(profile))
                self.assertEqual(0, result.returncode, result.stderr)
                self.assertFalse(path.exists())
                self.assertEqual("", _read(profile / "user.js"))

    def test_remove_keeps_a_foreign_sheet_and_foreign_pref(self):
        foreign_sheet = "/* my own chrome */\n"
        foreign_js = 'user_pref("tabs", 0);\r\n' + firefox_user_js.PREF_LINE + "\r\n"
        _write(self.sheet_path(), foreign_sheet)
        _write(self.user_js_path(), foreign_js)
        result = self.run_tool("--remove", "--profile", str(self.profile))
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(foreign_sheet, _read(self.sheet_path()))
        self.assertEqual(foreign_js, _read(self.user_js_path()))

    def test_remove_keeps_a_foreign_user_content_and_removes_our_user_chrome(self):
        foreign_content = "/* my own content */\n"
        _write(self.content_sheet_path(), foreign_content)
        _write(self.sheet_path(), f"{install_firefox.CSS_MARKER}\n/* owned */\n")
        block = (
            firefox_user_js.USER_JS_MARKER
            + "\n"
            + firefox_user_js.PREF_LINE
            + "\n"
        )
        _write(self.user_js_path(), block)

        result = self.run_tool("--remove", "--profile", str(self.profile))
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertFalse(self.sheet_path().exists())
        self.assertEqual(foreign_content, _read(self.content_sheet_path()))
        self.assertEqual("", _read(self.user_js_path()))

    def test_remove_deletes_our_user_content_when_user_chrome_is_absent(self):
        _write(
            self.content_sheet_path(),
            f"{install_firefox.CONTENT_CSS_MARKER}\n/* owned */\n",
        )
        block = (
            firefox_user_js.USER_JS_MARKER
            + "\n"
            + firefox_user_js.PREF_LINE
            + "\n"
        )
        _write(self.user_js_path(), block)

        result = self.run_tool("--remove", "--profile", str(self.profile))
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertFalse(self.sheet_path().exists())
        self.assertFalse(self.content_sheet_path().exists())
        self.assertEqual("", _read(self.user_js_path()))

    def test_remove_preserves_dangling_links_and_cleans_the_owned_sibling(self):
        for relative in (
            "chrome/userChrome.css",
            "chrome/userContent.css",
            "user.js",
        ):
            with self.subTest(path=relative):
                profile = self.root / relative.replace("/", "-")
                profile.mkdir()
                sheet = profile / "chrome" / "userChrome.css"
                content = profile / "chrome" / "userContent.css"
                js = profile / "user.js"
                sheet.parent.mkdir()
                link = profile / relative
                foreign = b'user_pref("keep.me", true);\r\n'
                if link == sheet:
                    block = (
                        firefox_user_js.USER_JS_MARKER + "\r\n"
                        + firefox_user_js.PREF_LINE + "\r\n"
                    ).encode("utf-8")
                    js.write_bytes(foreign + block)
                else:
                    _write(sheet, install_firefox.CSS_MARKER + "\n/* owned */\n")
                target = self.root / (profile.name + "-missing")
                self.create_symlink(link, target)

                result = self.run_tool("--remove", "--profile", str(profile))

                self.assertEqual(0, result.returncode, result.stderr)
                self.assertEqual("", result.stderr)
                self.assertTrue(link.is_symlink())
                self.assertEqual(target, link.readlink())
                self.assertFalse(target.exists())
                if link == sheet:
                    self.assertEqual(foreign, js.read_bytes())
                    expected = {sheet.parent, sheet, js}
                else:
                    self.assertFalse(sheet.exists())
                    self.assertFalse(content.exists() and content != link)
                    expected = {sheet.parent, link}
                self.assertEqual(expected, set(profile.rglob("*")))

    def test_remove_refuses_a_symlinked_sheet_before_deleting_anything(self):
        target = self.root / "dotfiles" / "userChrome.css"
        target.parent.mkdir(parents=True)
        css_text = f"{install_firefox.CSS_MARKER}\nbody {{}}\n"
        target.write_text(css_text, encoding="utf-8")
        link = self.sheet_path()
        link.parent.mkdir(parents=True)
        self.create_symlink(link, target)
        js_text = firefox_user_js.USER_JS_MARKER + "\n" + firefox_user_js.PREF_LINE + "\n"
        _write(self.user_js_path(), js_text)

        result = self.run_tool("--remove", "--profile", str(self.profile))
        self.assertEqual(2, result.returncode)
        self.assertIn(f"cannot remove {link}", result.stderr)
        self.assertIn("symbolic link", result.stderr)
        # The link and its target survive, and the preference block was not
        # cleared before the sheet was refused.
        self.assertTrue(link.is_symlink())
        self.assertEqual(css_text, target.read_text(encoding="utf-8"))
        self.assertEqual(js_text, _read(self.user_js_path()))

    def test_remove_refuses_a_symlinked_user_js_before_clearing_the_sheet(self):
        sheet_text = f"{install_firefox.CSS_MARKER}\nbody {{}}\n"
        _write(self.sheet_path(), sheet_text)
        target = self.root / "dotfiles" / "user.js"
        target.parent.mkdir(parents=True)
        js_text = firefox_user_js.USER_JS_MARKER + "\n" + firefox_user_js.PREF_LINE + "\n"
        target.write_text(js_text, encoding="utf-8")
        link = self.user_js_path()
        self.create_symlink(link, target)

        result = self.run_tool("--remove", "--profile", str(self.profile))
        self.assertEqual(2, result.returncode)
        self.assertIn(f"cannot remove {link}", result.stderr)
        self.assertIn("symbolic link", result.stderr)
        # The sheet was not deleted before the preference path was refused,
        # and the link's target keeps its marker block.
        self.assertEqual(sheet_text, _read(self.sheet_path()))
        self.assertTrue(link.is_symlink())
        self.assertEqual(js_text, target.read_text(encoding="utf-8"))

    def test_install_and_remove_preserve_foreign_lines_and_crlf(self):
        foreign = (
            'user_pref("browser.tabs.inTitlebar", 0);\r\n'
            'user_pref("browser.startup.homepage", "about:blank");'
        )
        _write(self.user_js_path(), foreign)
        self.install()
        installed = _read(self.user_js_path())
        self.assertTrue(installed.startswith(foreign + "\r\n"))
        self.assertEqual(1, installed.count(firefox_user_js.USER_JS_MARKER))
        result = self.run_tool("--remove", "--profile", str(self.profile))
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(foreign + "\r\n", _read(self.user_js_path()))

    def test_unreadable_user_js_is_reported_without_writing_the_sheet(self):
        self.user_js_path().mkdir()
        result = self.run_tool("--profile", str(self.profile))
        self.assertEqual(2, result.returncode)
        self.assertIn(str(self.user_js_path()), result.stderr)
        self.assertFalse(self.sheet_path().exists())

    def test_non_utf8_user_js_is_reported_without_writing_the_sheet(self):
        # The reader decodes user.js as UTF-8 and promises a by-name error for
        # invalid bytes, while the directory case above pins a non-regular
        # path. A user.js with a stray latin-1 byte must exit 2 naming the
        # file, and the install must stop before writing the sheet.
        self.user_js_path().write_bytes(b'user_pref("x", "\xff");\n')
        result = self.run_tool("--profile", str(self.profile))
        self.assertEqual(2, result.returncode)
        self.assertIn("cannot read", result.stderr)
        self.assertIn(str(self.user_js_path()), result.stderr)
        self.assertFalse(self.sheet_path().exists())

    def test_an_unreadable_profile_file_is_reported_by_name(self):
        # read_profile_text opens every profile file through the shared
        # regular-file reader. A self-referential symlink makes that open fail
        # with ELOOP, an OSError, deterministically -- no dependence on file
        # permissions or on the test user. The directory and FIFO fixtures
        # reach the ValueError arm and the stray-byte fixture the decode arm,
        # so this pins the OSError arm that becomes a by-name ConfigError.
        for name in ("userChrome.css", "userContent.css", "user.js"):
            with self.subTest(profile_file=name):
                profile = self.root / f"unreadable-{name}"
                profile.mkdir()
                paths = {
                    "userChrome.css": profile / "chrome" / "userChrome.css",
                    "userContent.css": profile / "chrome" / "userContent.css",
                    "user.js": profile / "user.js",
                }
                unreadable = paths[name]
                untouched = [path for label, path in paths.items() if label != name]
                unreadable.parent.mkdir(parents=True, exist_ok=True)
                self.create_symlink(unreadable, unreadable)
                result = self.run_tool("--profile", str(profile))
                self.assertEqual(2, result.returncode)
                self.assertIn(f"cannot read {unreadable}", result.stderr)
                self.assertIn(os.strerror(errno.ELOOP), result.stderr)
                for path in untouched:
                    self.assertFalse(path.exists())

    def test_a_fifo_at_either_profile_file_is_refused_without_blocking(self):
        # A plain read_bytes on a FIFO waits forever for a writer, so it would
        # stall `make install-firefox` instead of reporting the profile file.
        # Run the install in a child so a regression is a bounded timeout, and
        # refuse the pipe by name before the other profile file is written.
        snippet = (
            "import sys; from tools.install_firefox import main; "
            "sys.exit(main(sys.argv[1:]))"
        )
        files = (
            ("userChrome.css", Path("chrome") / "userChrome.css"),
            ("userContent.css", Path("chrome") / "userContent.css"),
            ("user.js", Path("user.js")),
        )
        for name, fifo in files:
            with self.subTest(profile_file=name):
                profile = self.root / f"fifo-{name}"
                profile.mkdir()
                fifo_path = profile / fifo
                make_fifo(self, fifo_path)
                with mock.patch.dict(
                    os.environ, {"HOME": str(self.home)}, clear=True
                ):
                    child = snippet_child.run(
                        [snippet, "--profile", str(profile)],
                        cwd=repo_root.ROOT,
                        timeout=10,
                    )
                assert_fifo_refused(self, child, fifo_path)
                for other_name, other in files:
                    if other_name != name:
                        self.assertFalse((profile / other).exists())

    def test_a_failed_user_js_write_during_removal_is_reported_by_path(self):
        # Removal rewrites user.js before it deletes the sheet. A failure on
        # that first step must name user.js and leave both files unchanged
        # instead of deleting the sheet and leaving a stale preference.
        self.install()
        before_js = _read(self.user_js_path())
        before_sheet = _read(self.sheet_path())
        with mock.patch.object(
            firefox_user_files,
            "write_atomically",
            self.fail_write_to(self.user_js_path()),
        ):
            result = self.run_tool("--remove", "--profile", str(self.profile))
        self.assertEqual(2, result.returncode)
        self.assertIn(f"cannot write {self.user_js_path()}", result.stderr)
        self.assertEqual(before_js, _read(self.user_js_path()))
        self.assertEqual(before_sheet, _read(self.sheet_path()))

    def test_a_failed_sheet_unlink_is_reported_by_path(self):
        # _remove promises a by-name "cannot remove" error when our sheet
        # cannot be deleted, leaving the sheet in place rather than crashing.
        # The user.js rewrite that preceded it is put back, so the failure
        # does not leave the preference removed from a sheet that remains.
        self.install()
        sheet = _read(self.sheet_path())
        before_js = _read(self.user_js_path())
        with mock.patch.object(Path, "unlink", side_effect=OSError("simulated failure")):
            result = self.run_tool("--remove", "--profile", str(self.profile))
        self.assertEqual(2, result.returncode)
        self.assertIn(f"cannot remove {self.sheet_path()}", result.stderr)
        self.assertEqual(sheet, _read(self.sheet_path()))
        self.assertEqual(before_js, _read(self.user_js_path()))

    def test_a_failed_user_content_unlink_is_reported_by_path(self):
        # Both owned sheets are deleted in SHEETS order. A failure on the
        # second unlink must name that sheet, leave it in place, and restore
        # the user.js rewrite because the content sheet still remains.
        self.install()
        before_js = _read(self.user_js_path())
        before_content = _read(self.content_sheet_path())
        with mock.patch.object(
            Path, "unlink", self.fail_unlink_to(self.content_sheet_path())
        ):
            result = self.run_tool("--remove", "--profile", str(self.profile))
        self.assertEqual(2, result.returncode)
        self.assertIn(f"cannot remove {self.content_sheet_path()}", result.stderr)
        self.assertFalse(self.sheet_path().exists())
        self.assertEqual(before_content, _read(self.content_sheet_path()))
        self.assertEqual(before_js, _read(self.user_js_path()))

    def test_an_interrupt_after_only_the_first_sheet_unlink_restores_user_js(self):
        # An interrupt after the first sheet unlink leaves the second sheet
        # present, so the removal is half-applied and must put the previous
        # user.js back instead of keeping the rewritten one.
        self.install()
        before_js = _read(self.user_js_path())
        real_unlink = Path.unlink

        def interrupt_after_the_chrome_unlink(path, *args, **kwargs):
            if Path(path) == self.sheet_path():
                real_unlink(path, *args, **kwargs)
                raise KeyboardInterrupt
            return real_unlink(path, *args, **kwargs)

        with mock.patch.object(Path, "unlink", interrupt_after_the_chrome_unlink):
            with self.assertRaises(KeyboardInterrupt):
                self.run_tool("--remove", "--profile", str(self.profile))
        self.assertFalse(self.sheet_path().exists())
        self.assertTrue(self.content_sheet_path().exists())
        self.assertEqual(before_js, _read(self.user_js_path()))

    def test_a_failed_user_js_restore_during_removal_names_both_errors(self):
        # If the sheet cannot be deleted and the user.js rewrite cannot be put
        # back, the removal cannot restore the pair. The error must name both
        # failures, so the preference-less user.js beside the surviving sheet
        # is visible instead of the rollback failure being swallowed.
        self.install()
        before_js = _read(self.user_js_path())
        before_sheet = _read(self.sheet_path())
        real_write = firefox_user_files.write_atomically
        js_writes = []

        def flaky_write(path, writer):
            if Path(path) == self.user_js_path():
                js_writes.append(path)
                if len(js_writes) > 1:
                    raise OSError("simulated rollback failure")
            return real_write(path, writer)

        with mock.patch.object(
            firefox_user_files, "write_atomically", flaky_write
        ), mock.patch.object(
            Path, "unlink", side_effect=OSError("simulated failure")
        ):
            result = self.run_tool("--remove", "--profile", str(self.profile))
        self.assertEqual(2, result.returncode)
        self.assertIn(f"cannot remove {self.sheet_path()}", result.stderr)
        self.assertIn(f"cannot write {self.user_js_path()}", result.stderr)
        self.assertEqual(before_sheet, _read(self.sheet_path()))
        self.assertNotEqual(before_js, _read(self.user_js_path()))

    def test_an_interrupt_during_the_sheet_unlink_restores_user_js(self):
        # An interrupt after the user.js rewrite is not an OSError, but the
        # removal must still put the preference block back and then propagate
        # the interrupt instead of leaving a sheet with no preference.
        self.install()
        before_js = _read(self.user_js_path())
        before_sheet = _read(self.sheet_path())
        with mock.patch.object(Path, "unlink", side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):
                self.run_tool("--remove", "--profile", str(self.profile))
        self.assertEqual(before_sheet, _read(self.sheet_path()))
        self.assertEqual(before_js, _read(self.user_js_path()))

    def test_an_interrupt_after_the_user_js_rewrite_takes_effect_restores_it(self):
        # The rewrite can remove the preference block and then raise before
        # the caller records it. Without a pre-set intent flag that interrupt
        # skips the rollback and leaves the surviving sheet without its
        # preference; the previous user.js must be put back.
        self.install()
        before_js = _read(self.user_js_path())
        before_sheet = _read(self.sheet_path())
        real_write = firefox_user_files.write_atomically
        js_writes = []

        def interrupt_after_the_user_js_rewrite(path, writer):
            if Path(path) == self.user_js_path():
                js_writes.append(path)
                real_write(path, writer)
                if len(js_writes) == 1:
                    raise KeyboardInterrupt
                return
            return real_write(path, writer)

        with mock.patch.object(
            firefox_user_files, "write_atomically", interrupt_after_the_user_js_rewrite
        ):
            with self.assertRaises(KeyboardInterrupt):
                self.run_tool("--remove", "--profile", str(self.profile))
        self.assertEqual(before_js, _read(self.user_js_path()))
        self.assertEqual(before_sheet, _read(self.sheet_path()))

    def test_an_interrupt_after_the_sheet_unlink_takes_effect_keeps_the_removal(self):
        # An interrupt can arrive after the unlink removed the sheet but before
        # the removal records it. The sheet is gone, so the already rewritten
        # user.js matches a completed removal and must not be put back: a
        # rollback keyed on a late flag would leave a preference with no sheet.
        self.install()
        before_js = _read(self.user_js_path())
        real_unlink = Path.unlink

        def interrupt_after_the_last_sheet_unlink(path, *args, **kwargs):
            if Path(path) == self.content_sheet_path():
                real_unlink(path, *args, **kwargs)
                raise KeyboardInterrupt
            return real_unlink(path, *args, **kwargs)

        with mock.patch.object(Path, "unlink", interrupt_after_the_last_sheet_unlink):
            with self.assertRaises(KeyboardInterrupt):
                self.run_tool("--remove", "--profile", str(self.profile))
        self.assertFalse(self.sheet_path().exists())
        self.assertFalse(self.content_sheet_path().exists())
        self.assertEqual(
            firefox_user_js.remove_user_js(before_js), _read(self.user_js_path())
        )


if __name__ == "__main__":
    unittest.main()
