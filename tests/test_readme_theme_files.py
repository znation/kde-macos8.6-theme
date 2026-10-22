"""README's list of shipped theme SVGs must match the files on disk.

README names every SVG the desktop theme and the window decoration ship, in
backticks, so a contributor can find the artwork for a surface. Adding a widget
SVG without naming it, or deleting one and leaving its name behind, makes that
list lie; these tests derive both sides and fail when they disagree.
"""

from __future__ import annotations

import glob
import os
import re
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from support import containment
from support import snippet_child
from support.desktoptheme_paths import PACKAGE
from support.repo_root import ROOT
from tools import containment as tools_containment

_DESKTOP_TOKEN = re.compile(r"`((?:widgets|dialogs)/[^`/]+\.svg)`")
_AURORAE_TOKEN = re.compile(r"`([^`/]+\.svg)`")
AURORAE_DIR = os.path.join(ROOT, "theme", "aurorae", "themes", "org.macos8.desktop")


def readme_text():
    """Return the UTF-8 text of the repository's ``README.md``.

    ``README.md`` is contributor-supplied, and a checked-in symlink at its
    path can point at a private file. The backticked SVG names this reader
    extracts are echoed by the ``assertEqual`` diagnostics below, so a path
    that resolves outside the repository is refused before it is opened.
    Reading through the shared guard also bounds the read (an arbitrarily
    large README is refused by name instead of being loaded whole) and refuses
    a FIFO or device by name instead of blocking `make check` forever.
    """
    path = os.path.join(ROOT, "README.md")
    return containment.read_text(path, ROOT)


def shipped(package, pattern):
    """Paths of *package*'s SVGs matching *pattern*, relative to *package*."""
    return {
        os.path.relpath(path, package)
        for path in glob.glob(os.path.join(package, pattern), recursive=True)
    }


class TestReadmeThemeFiles(unittest.TestCase):
    def _assert_every_svg_is_named(self, token, package, pattern, label):
        """Fail when a shipped *label* SVG is absent from README's backticks."""
        named = set(token.findall(readme_text()))
        on_disk = shipped(package, pattern)
        self.assertTrue(on_disk, "no %s SVGs found under %s" % (label, package))
        self.assertEqual(
            set(),
            on_disk - named,
            "%s SVGs README does not name in backticks" % label,
        )

    def test_every_desktop_theme_svg_is_named_in_readme(self):
        self._assert_every_svg_is_named(
            _DESKTOP_TOKEN, PACKAGE, "*/*.svg", "desktop theme"
        )

    def test_readme_names_no_missing_desktop_theme_svg(self):
        named = set(_DESKTOP_TOKEN.findall(readme_text()))
        self.assertEqual(
            set(),
            named - shipped(PACKAGE, "*/*.svg"),
            "README names desktop theme SVGs that are not shipped",
        )

    def test_every_aurorae_svg_is_named_in_readme(self):
        self._assert_every_svg_is_named(
            _AURORAE_TOKEN, AURORAE_DIR, "*.svg", "Aurorae"
        )


class TestReadmeTextContainment(unittest.TestCase):
    """The README read refuses a symlink that escapes the repository.

    A checked-in symlink at ``README.md`` can point at a private file, and the
    SVG names parsed from it reach ``assertEqual`` diagnostics that echo the
    sets; the read must refuse such a path before it is opened rather than
    leak the private file's backticked tokens.
    """

    def test_rejects_a_symlink_that_escapes_the_repository(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            root = tmp / "repo"
            root.mkdir()
            secret = tmp / "secret.md"
            secret.write_text(
                "`widgets/private.svg`\n", encoding="utf-8"
            )
            link = root / "README.md"
            link.symlink_to(secret)
            with mock.patch.object(sys.modules[__name__], "ROOT", root):
                with self.assertRaises(ValueError) as caught:
                    readme_text()
        self.assertIn(str(link), str(caught.exception))

    def test_allows_a_symlink_that_stays_within_the_repository(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            root = tmp / "repo"
            root.mkdir()
            target = root / "actual-readme.md"
            target.write_text("`widgets/a.svg`\n", encoding="utf-8")
            link = root / "README.md"
            link.symlink_to(target)
            with mock.patch.object(sys.modules[__name__], "ROOT", root):
                self.assertEqual(readme_text(), "`widgets/a.svg`\n")

    def test_refuses_an_oversize_readme_instead_of_loading_it_whole(self):
        # README is contributor-supplied, so a stray multi-gigabyte file must
        # not be loaded whole: a plain ``read()`` would allocate it and raise
        # MemoryError, which names neither the file nor the guard. The shared
        # reader refuses one past its cap by name instead.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            root.mkdir()
            path = root / "README.md"
            path.write_bytes(b"x" * (tools_containment._MAX_READ_BYTES + 1))
            with mock.patch.object(sys.modules[__name__], "ROOT", root):
                with self.assertRaises(ValueError) as caught:
                    readme_text()
        self.assertIn(str(path), str(caught.exception))
        self.assertIn("larger than", str(caught.exception))

    def test_refuses_a_fifo_instead_of_blocking(self):
        # open() on a FIFO blocks until a writer appears, and readme_text has
        # no timeout, so one stray pipe at README.md would stall `make check`
        # with no diagnostic. Run it in a child so the pre-fix hang is a
        # bounded timeout rather than a stalled run.
        if not hasattr(os, "mkfifo"):
            self.skipTest("os.mkfifo is not available on this platform")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            root.mkdir()
            fifo = root / "README.md"
            os.mkfifo(fifo)
            code = (
                "import sys\n"
                "from unittest import mock\n"
                "import test_readme_theme_files as reader\n"
                "with mock.patch.object(reader, 'ROOT', sys.argv[1]):\n"
                "    reader.readme_text()\n"
            )
            child = snippet_child.run(
                [code, str(root)],
                cwd=os.path.dirname(__file__),
                timeout=10,
            )
        self.assertNotEqual(0, child.returncode, child.stdout + child.stderr)
        self.assertIn("not a regular file", child.stderr)
        self.assertIn(str(fifo), child.stderr)


class TestReadmeTokenParsing(unittest.TestCase):
    """Pin the token rules on synthetic text."""

    def test_desktop_token_requires_a_widgets_or_dialogs_directory(self):
        text = "`widgets/a.svg` `dialogs/b.svg` `c.svg` `other/d.svg` `widgets/e/f.svg`"
        self.assertEqual(
            ["widgets/a.svg", "dialogs/b.svg"], _DESKTOP_TOKEN.findall(text)
        )

    def test_aurorae_token_is_a_bare_file_name(self):
        text = "`a.svg` `widgets/b.svg` `c.png`"
        self.assertEqual(["a.svg"], _AURORAE_TOKEN.findall(text))


if __name__ == "__main__":
    unittest.main()
