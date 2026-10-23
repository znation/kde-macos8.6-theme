"""Commands and paths README tells a reader to use must exist.

README names `make` targets, `tools/*.py` scripts and a few package paths. A
renamed target or script leaves the instruction pointing at nothing; these
tests derive the names from README and fail when one has no counterpart.
"""

from __future__ import annotations

import os
import re
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from support import containment
from support.repo_root import ROOT
from support.symlink_fixtures import symlinked_repo
from tools import render_surface

_MAKE_TARGET = re.compile(r"\bmake\s+([a-z][a-z-]*)\b")
_TOOL_SCRIPT = re.compile(r"\btools/[A-Za-z0-9_]+\.py\b")
_PACKAGE_PATH = re.compile(r"`((?:theme|contents)/[A-Za-z0-9_./-]+)`")
_MAKEFILE_TARGET = re.compile(r"^([A-Za-z][A-Za-z0-9_-]*)\s*:(?!=)", re.MULTILINE)
LOOK_AND_FEEL = os.path.join(ROOT, "theme", "look-and-feel", "org.macos8.desktop")


def read(name):
    """Return the UTF-8 text of the repository file at *name*.

    ``README.md`` and ``Makefile`` are contributor-supplied, and a checked-in
    symlink at either path can point at a private file. The make targets,
    ``tools/*.py`` scripts and backticked package paths this reader extracts
    are echoed by the ``assertEqual`` diagnostics below, so a path that
    resolves outside the repository is refused before it is opened.
    """
    return containment.read_text(os.path.join(ROOT, name), ROOT, encoding="utf-8")


class TestReadmeCommands(unittest.TestCase):
    def test_every_make_target_in_readme_is_defined(self):
        named = set(_MAKE_TARGET.findall(read("README.md")))
        defined = set(_MAKEFILE_TARGET.findall(read("Makefile")))
        self.assertTrue(named, "README names no make targets")
        self.assertEqual(
            set(), named - defined, "README names make targets the Makefile lacks"
        )

    def test_every_tool_script_in_readme_exists(self):
        named = set(_TOOL_SCRIPT.findall(read("README.md")))
        self.assertTrue(named, "README names no tools/ scripts")
        missing = {n for n in named if not os.path.isfile(os.path.join(ROOT, n))}
        self.assertEqual(set(), missing, "README names tools/ scripts not on disk")

    def test_every_package_path_in_readme_exists(self):
        named = set(_PACKAGE_PATH.findall(read("README.md")))
        self.assertTrue(named, "README names no theme/ or contents/ paths")
        missing = set()
        for path in named:
            base = ROOT if path.startswith("theme/") else LOOK_AND_FEEL
            if not os.path.isfile(os.path.join(base, path)):
                missing.add(path)
        self.assertEqual(set(), missing, "README names package files not on disk")

    def test_readme_names_every_tool_make_render_requires(self):
        readme = read("README.md")
        start = readme.index("`make render` renders")
        paragraph = readme[start : readme.index("\n\n", start)]
        # `make` is the command the paragraph documents, so it is always named.
        wanted = [t for t in render_surface.REQUIRED_TOOLS if t != "make"]
        unnamed = [t for t in wanted if f"`{t}`" not in paragraph]
        self.assertEqual([], unnamed, "make render needs tools README does not name")


class TestReadCommandContainment(unittest.TestCase):
    """The README/Makefile read refuses a symlink that escapes the repository.

    A checked-in symlink at ``README.md`` or ``Makefile`` can point at a
    private file, and the token sets parsed from it reach ``assertEqual``
    diagnostics that echo them; the read must refuse such a path before it is
    opened rather than leak the private file's matching tokens.
    """

    def test_rejects_a_symlink_that_escapes_the_repository(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, link = symlinked_repo(
                tmp, "README.md", "make private-target\n"
            )
            with mock.patch.object(sys.modules[__name__], "ROOT", root):
                with self.assertRaises(ValueError) as caught:
                    read("README.md")
        self.assertIn(str(link), str(caught.exception))

    def test_allows_a_symlink_that_stays_within_the_repository(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, _ = symlinked_repo(
                tmp, "README.md", "make check\n", target="actual-readme.md"
            )
            with mock.patch.object(sys.modules[__name__], "ROOT", root):
                self.assertEqual(read("README.md"), "make check\n")


class TestReadmeCommandParsing(unittest.TestCase):
    """Pin the token rules on synthetic text."""

    def test_make_target_spans_a_line_break(self):
        self.assertEqual(["uninstall"], _MAKE_TARGET.findall("`make\nuninstall`"))

    def test_make_target_ignores_variables_and_capitalised_words(self):
        self.assertEqual([], _MAKE_TARGET.findall("make CHECK_TESTS=x; Make Check"))

    def test_tool_script_needs_the_tools_directory(self):
        text = "python3 tools/sample.py x; other/sample.py"
        self.assertEqual(["tools/sample.py"], _TOOL_SCRIPT.findall(text))

    def test_makefile_target_skips_variable_assignments(self):
        text = "CC := x\ncheck:\n\tx\n_priv:\nhelp: check\n"
        self.assertEqual(["check", "help"], _MAKEFILE_TARGET.findall(text))


if __name__ == "__main__":
    unittest.main()
