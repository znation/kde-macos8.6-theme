"""Tests for the Firefox profile removal workflow (``install_firefox.py --remove``).

The tool runs in-process with ``HOME`` pointed at a temp root, so the removal of
the sheets and the ``user.js`` block is pinned without touching a real Firefox
profile. The install and profile-lock cases stay in
``tests/test_install_firefox.py``; the rollback cases (a failed rewrite, unlink
or restore, and interrupts) live in ``tests/test_remove_firefox_rollback.py``.
The shared temp-home case is ``support.firefox_profile_case``.
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
from support.process_assertions import assert_succeeded
from support.theme_install import write_file as _write
from support.firefox_profile_case import FirefoxProfileTestCase, read_utf8 as _read
from tools import install_firefox
from tools.firefox import user_js as firefox_user_js


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

    def test_remove_deletes_our_sheets_and_block_and_keeps_the_directory(self):
        self.install()
        result = self.run_tool("--remove", "--profile", str(self.profile))
        assert_succeeded(self, result)
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
        assert_succeeded(self, result)
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
                assert_succeeded(self, result)
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
        assert_succeeded(self, result)
        self.assertEqual(foreign_sheet, _read(self.sheet_path()))
        self.assertEqual(foreign_js, _read(self.user_js_path()))

    def test_remove_keeps_a_foreign_user_content_and_removes_our_user_chrome(self):
        foreign_content = "/* my own content */\n"
        _write(self.content_sheet_path(), foreign_content)
        _write(self.sheet_path(), f"{install_firefox.CSS_MARKER}\n/* owned */\n")
        block = self._owned_user_js_block()
        _write(self.user_js_path(), block)

        result = self.run_tool("--remove", "--profile", str(self.profile))
        assert_succeeded(self, result)
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
        assert_succeeded(self, result)
        self.assert_profile_absent(self.sheet_path(), self.content_sheet_path())
        self.assertEqual("", _read(self.user_js_path()))

    def test_remove_deletes_our_sheet_and_does_not_create_a_missing_user_js(self):
        _write(self.sheet_path(), f"{install_firefox.CSS_MARKER}\n/* owned */\n")
        self.assertFalse(self.user_js_path().exists())

        result = self.run_tool("--remove", "--profile", str(self.profile))
        assert_succeeded(self, result)
        self.assert_profile_absent(self.sheet_path(), self.user_js_path())

    def test_remove_clears_owned_user_js_without_creating_a_missing_chrome_dir(self):
        block = self._owned_user_js_block()
        _write(self.user_js_path(), block)
        self.assertFalse((self.profile / "chrome").exists())

        result = self.run_tool("--remove", "--profile", str(self.profile))

        assert_succeeded(self, result)
        self.assertEqual("", _read(self.user_js_path()))
        self.assertFalse((self.profile / "chrome").exists())

    def test_remove_deletes_our_sheet_and_leaves_a_user_js_without_our_block(self):
        foreign_js = 'user_pref("tabs", 0);\n'
        _write(self.sheet_path(), f"{install_firefox.CSS_MARKER}\n/* owned */\n")
        _write(self.user_js_path(), foreign_js)

        result = self.run_tool("--remove", "--profile", str(self.profile))
        assert_succeeded(self, result)
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

                assert_succeeded(self, result)
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
        assert_succeeded(self, result)
        self.assertEqual(foreign + "\r\n", _read(self.user_js_path()))

    def test_unreadable_user_js_is_reported_without_writing_the_sheet(self):
        self.user_js_path().mkdir()
        result = self.run_tool("--profile", str(self.profile))
        self.assertEqual(2, result.returncode)
        self.assertIn(str(self.user_js_path()), result.stderr)
        self.assert_profile_absent(self.sheet_path())

    def test_a_directory_at_user_chrome_is_refused_and_user_js_is_kept(self):
        # Removal reads userChrome.css through the shared regular-file reader
        # before it decides ownership. A directory at that path must exit 2
        # naming the path, keep the directory, and leave our user.js block and
        # our userContent.css untouched, because the refusal comes before any
        # write or unlink.
        self.install()
        js_bytes = self.user_js_path().read_bytes()
        content_bytes = self.content_sheet_path().read_bytes()
        self.sheet_path().unlink()
        self.sheet_path().mkdir()
        result = self.run_tool("--remove", "--profile", str(self.profile))
        self.assertEqual(2, result.returncode, result.stderr)
        self.assertIn(f"cannot read {self.sheet_path()}", result.stderr)
        self.assertIn("not a regular file", result.stderr)
        self.assertTrue(self.sheet_path().is_dir())
        self.assertEqual(js_bytes, self.user_js_path().read_bytes())
        self.assertEqual(content_bytes, self.content_sheet_path().read_bytes())

    def test_a_directory_at_user_js_keeps_installed_sheets_byte_for_byte(self):
        # Removal reads both installed sheets and then user.js. A directory at
        # user.js must refuse by name before any sheet is unlinked, so the
        # installed userChrome.css and userContent.css keep their exact bytes.
        self.install()
        chrome_bytes = self.sheet_path().read_bytes()
        content_bytes = self.content_sheet_path().read_bytes()
        self.user_js_path().unlink()
        self.user_js_path().mkdir()
        result = self.run_tool("--remove", "--profile", str(self.profile))
        self.assertEqual(2, result.returncode, result.stderr)
        self.assertIn(str(self.user_js_path()), result.stderr)
        self.assertTrue(self.user_js_path().is_dir())
        self.assertEqual(chrome_bytes, self.sheet_path().read_bytes())
        self.assertEqual(content_bytes, self.content_sheet_path().read_bytes())

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


if __name__ == "__main__":
    unittest.main()
