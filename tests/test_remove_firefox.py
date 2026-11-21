"""Tests for the Firefox profile removal workflow (``install_firefox.py --remove``).

The tool runs in-process with ``HOME`` pointed at a temp root, so the removal of
the sheets and the ``user.js`` block is pinned without touching a real Firefox
profile. The install and profile-lock cases stay in
``tests/test_install_firefox.py``; the shared temp-home case is
``support.firefox_profile_case``.
"""

from __future__ import annotations

import errno
import os
import unittest
from pathlib import Path
from unittest import mock

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support import snippet_child
from support.fifo_fixtures import assert_fifo_refused, make_fifo
from support.theme_install import write_file as _write
from support.firefox_profile_case import FirefoxProfileTestCase, read_utf8 as _read
from tools import (
    firefox_user_files,
    firefox_user_js,
    install_firefox,
)


class TestRemove(FirefoxProfileTestCase):
    def test_remove_refuses_a_symlinked_chrome_directory(self):
        outside = self.root / "outside-chrome"
        outside.mkdir()
        sheet = outside / "userChrome.css"
        sheet.write_text(
            f"{install_firefox.CSS_MARKER}\nbody {{}}\n", encoding="utf-8"
        )
        self.create_symlink(self.profile / "chrome", outside, target_is_directory=True)
        js_text = self._owned_user_js_block()
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
        self.assert_profile_absent(self.sheet_path(), self.content_sheet_path())
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
        block = self._owned_user_js_block()
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
                block = self._owned_user_js_block()
                _write(profile / "user.js", block)

                result = self.run_tool("--remove", "--profile", str(profile))
                self.assertEqual(0, result.returncode, result.stderr)
                self.assertFalse(path.exists())
                self.assertEqual("", _read(profile / "user.js"))

    def test_remove_keeps_a_foreign_sheet_and_foreign_pref(self):
        foreign_sheet = "/* my own chrome */\n"
        foreign_js = (
            'user_pref("tabs", 0);\r\n'
            + firefox_user_js.STYLESHEETS_PREF
            + "\r\n"
        )
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
        block = self._owned_user_js_block()
        _write(self.user_js_path(), block)

        result = self.run_tool("--remove", "--profile", str(self.profile))
        self.assertEqual(0, result.returncode, result.stderr)
        self.assert_profile_absent(self.sheet_path())
        self.assertEqual(foreign_content, _read(self.content_sheet_path()))
        self.assertEqual("", _read(self.user_js_path()))

    def test_remove_deletes_our_user_content_when_user_chrome_is_absent(self):
        _write(
            self.content_sheet_path(),
            f"{install_firefox.CONTENT_CSS_MARKER}\n/* owned */\n",
        )
        block = self._owned_user_js_block()
        _write(self.user_js_path(), block)

        result = self.run_tool("--remove", "--profile", str(self.profile))
        self.assertEqual(0, result.returncode, result.stderr)
        self.assert_profile_absent(self.sheet_path(), self.content_sheet_path())
        self.assertEqual("", _read(self.user_js_path()))

    def test_remove_deletes_our_sheet_and_does_not_create_a_missing_user_js(self):
        _write(self.sheet_path(), f"{install_firefox.CSS_MARKER}\n/* owned */\n")
        self.assertFalse(self.user_js_path().exists())

        result = self.run_tool("--remove", "--profile", str(self.profile))
        self.assertEqual(0, result.returncode, result.stderr)
        self.assert_profile_absent(self.sheet_path(), self.user_js_path())

    def test_remove_clears_owned_user_js_without_creating_a_missing_chrome_dir(self):
        block = self._owned_user_js_block()
        _write(self.user_js_path(), block)
        self.assertFalse((self.profile / "chrome").exists())

        result = self.run_tool("--remove", "--profile", str(self.profile))

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual("", _read(self.user_js_path()))
        self.assertFalse((self.profile / "chrome").exists())

    def test_remove_deletes_our_sheet_and_leaves_a_user_js_without_our_block(self):
        foreign_js = 'user_pref("tabs", 0);\n'
        _write(self.sheet_path(), f"{install_firefox.CSS_MARKER}\n/* owned */\n")
        _write(self.user_js_path(), foreign_js)

        result = self.run_tool("--remove", "--profile", str(self.profile))
        self.assertEqual(0, result.returncode, result.stderr)
        self.assert_profile_absent(self.sheet_path())
        self.assertEqual(foreign_js, _read(self.user_js_path()))

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
                    block = self._owned_user_js_block("\r\n").encode("utf-8")
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
        js_text = self._owned_user_js_block()
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
        js_text = self._owned_user_js_block()
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
            'user_pref("browser.tabs.warnOnClose", false);\r\n'
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
        self.assert_profile_absent(self.sheet_path())

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
        self.assert_profile_absent(self.sheet_path())

    def test_non_utf8_user_chrome_is_reported_and_nothing_is_removed(self):
        # Removal decodes each sheet before deciding ownership, so a sheet
        # with invalid UTF-8 must exit 2 naming the file. The sheet and
        # user.js keep their bytes, because the refusal comes before any write.
        sheet_bytes = b"/* not decodable \xff */\n"
        js_bytes = b'user_pref("keep.me", true);\n'
        self.sheet_path().parent.mkdir(parents=True)
        self.sheet_path().write_bytes(sheet_bytes)
        self.user_js_path().write_bytes(js_bytes)
        result = self.run_tool("--profile", str(self.profile))
        self.assertEqual(2, result.returncode, result.stderr)
        self.assertIn("cannot read", result.stderr)
        self.assertIn(str(self.sheet_path()), result.stderr)
        self.assertEqual(sheet_bytes, self.sheet_path().read_bytes())
        self.assertEqual(js_bytes, self.user_js_path().read_bytes())

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
                self._assert_other_files_absent(profile, files, name)

    def _assert_other_files_absent(self, profile, files, name):
        """Assert no profile file but *name*'s was created."""
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
        self.run_with_failed_write(
            self.user_js_path(), "--remove", "--profile", str(self.profile)
        )
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

    def test_a_failed_user_content_unlink_restores_the_published_user_chrome(
        self,
    ):
        # Both owned sheets are deleted in SHEETS order. A failure on the
        # second unlink must name that sheet, leave it in place, and undo
        # both earlier steps: the user.js rewrite goes back and the user
        # chrome the first unlink took is written back byte-for-byte, so a
        # removal that fails partway leaves the profile exactly as it was.
        self.install()
        before_js = _read(self.user_js_path())
        before_sheet = _read(self.sheet_path())
        before_content = _read(self.content_sheet_path())
        with mock.patch.object(
            Path, "unlink", self.fail_unlink_to(self.content_sheet_path())
        ):
            result = self.run_tool("--remove", "--profile", str(self.profile))
        self.assertEqual(2, result.returncode)
        self.assertIn(f"cannot remove {self.content_sheet_path()}", result.stderr)
        self.assertEqual(before_sheet, _read(self.sheet_path()))
        self.assertEqual(before_content, _read(self.content_sheet_path()))
        self.assertEqual(before_js, _read(self.user_js_path()))

    def test_a_failed_deleted_sheet_restore_names_both_during_removal(self):
        # When the second unlink fails and the deleted user chrome cannot be
        # written back either, the removal cannot fully restore the pair. The
        # error must name both failures so the absent sheet is visible
        # instead of the rollback failure being swallowed.
        self.install()
        before_content = _read(self.content_sheet_path())
        real_write = firefox_user_files.write_atomically

        def failing_restore(path, writer):
            if Path(path) == self.sheet_path():
                raise OSError("simulated restore failure")
            return real_write(path, writer)

        with mock.patch.object(
            Path, "unlink", self.fail_unlink_to(self.content_sheet_path())
        ), mock.patch.object(
            firefox_user_files, "write_atomically", failing_restore
        ):
            result = self.run_tool("--remove", "--profile", str(self.profile))
        self.assertEqual(2, result.returncode)
        self.assertIn(f"cannot remove {self.content_sheet_path()}", result.stderr)
        self.assertIn(f"cannot write {self.sheet_path()}", result.stderr)
        self.assert_profile_absent(self.sheet_path())
        self.assertEqual(before_content, _read(self.content_sheet_path()))

    def test_a_failed_unlink_restores_an_outdated_sheet_reading_it_had(self):
        # A repeat install can adopt an outdated sheet that is still ours. A
        # removal of it that fails after the first unlink must restore the
        # sheet's own text, the one the removal read, not the shipped sheet
        # it shares a marker with.
        self.install()
        outdated = f"{install_firefox.CSS_MARKER}\n/* outdated sheet */\n"
        _write(self.sheet_path(), outdated)
        before_js = _read(self.user_js_path())
        with mock.patch.object(
            Path, "unlink", self.fail_unlink_to(self.content_sheet_path())
        ):
            result = self.run_tool("--remove", "--profile", str(self.profile))
        self.assertEqual(2, result.returncode)
        self.assertIn(f"cannot remove {self.content_sheet_path()}", result.stderr)
        self.assertEqual(outdated, _read(self.sheet_path()))
        self.assertEqual(before_js, _read(self.user_js_path()))

    def test_an_interrupt_after_only_the_first_sheet_unlink_restores_user_js(self):
        # An interrupt after the first sheet unlink leaves the second sheet
        # present, so the removal is half-applied and must undo it: the
        # previous user.js goes back and the deleted user chrome is restored,
        # leaving the profile exactly as it was instead of keeping the
        # rewritten one.
        self.install()
        before_js = _read(self.user_js_path())
        before_sheet = _read(self.sheet_path())
        with mock.patch.object(
            Path, "unlink", self.interrupt_unlink_to(self.sheet_path())
        ):
            with self.assertRaises(KeyboardInterrupt):
                self.run_tool("--remove", "--profile", str(self.profile))
        self.assertEqual(before_sheet, _read(self.sheet_path()))
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
        with mock.patch.object(
            Path, "unlink", self.interrupt_unlink_to(self.content_sheet_path())
        ):
            with self.assertRaises(KeyboardInterrupt):
                self.run_tool("--remove", "--profile", str(self.profile))
        self.assert_profile_absent(self.sheet_path(), self.content_sheet_path())
        self.assertEqual(
            firefox_user_js.remove_user_js(before_js), _read(self.user_js_path())
        )


if __name__ == "__main__":
    unittest.main()
