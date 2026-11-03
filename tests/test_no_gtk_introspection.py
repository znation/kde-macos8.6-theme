"""Pin that the suite's own Python process imports no GTK introspection.

The GTK pixel suites run their GTK work inside child interpreters
(``tests/test_gtk_theme_controls.py`` via its ``-c`` programs,
``tests/test_gtk4_theme.py`` via ``subprocess.run``): an in-process
``import gi`` leaves GLib's C worker threads in the suite process. Those
threads never appear in ``threading.active_count()``, but every later
``tests/support/snippet_child.py`` ``os.fork`` FIFO guard then runs from a
multi-threaded parent -- Python 3.12+ warns about that as a deadlock hazard
in the child, and a future Python may refuse it outright. A child program's
``import gi`` lives inside a string constant, which the AST never sees as an
import statement, so this scanner keeps a real import from sneaking back
into the process.
"""

from __future__ import annotations

import ast
import re
import unittest

from support.repo_root import ROOT

# One scan over the repo's Python packages keeps the invariant tree-wide:
# a tool or helper that imported ``gi`` in-process would poison the whole
# suite process the same way a test does.
_SCANNED_DIRS = ("tools", "tests")

# A cheap text gate before the per-file parse: any real Import or
# ImportFrom node whose root module is ``gi`` puts the keyword, the module
# name and whitespace between them into the file's source, so a source that
# lacks that text cannot hold such a node and needs no parse. The \-newline
# continuations are flattened first because ``import \\\n    gi`` splits the
# keyword from the name across lines; overmatching (a string mentioning
# ``import gi``, as the GTK suites' child programs do) only costs the parse
# the strict scan would have spent anyway.
_IMPORT_GI = re.compile(r"\b(?:from|import)\s+gi\b")


def _has_importable_gi(source: str) -> bool:
    """Return whether *source* can hold a real import statement naming ``gi``.

    Backslash-newline continuations are flattened before the search so an
    import whose ``import`` keyword and ``gi`` name sit on separate lines
    still matches.
    """
    return _IMPORT_GI.search(source.replace("\\\n", " ")) is not None


def _gi_import_messages(path: str, source: str) -> list[str]:
    """Return one message per ``gi`` import statement in real *source* code.

    A path is echoed into each message so a finding names its file and line;
    *path* is the reader-facing name (a real file path or a test label).
    """
    messages: list[str] = []
    tree = ast.parse(source, filename=path)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            names = [node.module or ""]
        else:
            continue
        for name in names:
            if name.split(".")[0] == "gi":
                messages.append(f"{path}:{node.lineno}: imports {name}")
    return messages


class TestNoGtkIntrospection(unittest.TestCase):
    """No module under tools/ or tests/ imports GTK introspection in-process."""

    def test_the_repository_imports_no_gtk_introspection_in_process(self):
        findings: list[str] = []
        for directory in _SCANNED_DIRS:
            for path in sorted((ROOT / directory).rglob("*.py")):
                if "__pycache__" in path.parts:
                    continue
                source = path.read_text(encoding="utf-8")
                if not _has_importable_gi(source):
                    continue
                findings.extend(
                    _gi_import_messages(
                        str(path.relative_to(ROOT)),
                        source,
                    )
                )
        self.assertEqual(
            findings,
            [],
            "an in-process import of gi leaves GLib's worker threads in the "
            "suite process, which poisons every later tests/support/"
            "snippet_child.py os.fork FIFO guard (Python 3.12+ deprecates "
            "forking a multi-threaded process): move the GTK work into a "
            "child interpreter, as tests/test_gtk_theme_controls.py and "
            "tests/test_gtk4_theme.py do",
        )

    def test_the_detector_names_an_in_process_gi_import(self):
        findings = _gi_import_messages(
            "synthetic", "from gi.repository import Gtk\n"
        )
        self.assertEqual(
            findings, ["synthetic:1: imports gi.repository"], findings
        )

    def test_the_detector_names_a_bare_gi_import(self):
        findings = _gi_import_messages("synthetic", "import gi\n")
        self.assertEqual(findings, ["synthetic:1: imports gi"], findings)

    def test_the_detector_ignores_a_child_program_string(self):
        # The child program's import is text in a string constant, exactly
        # how the two GTK suites hide theirs.
        findings = _gi_import_messages(
            "synthetic", "run_child('-c', 'import gi\\n')\n"
        )
        self.assertEqual(findings, [], findings)

    def test_the_text_gate_admits_every_form_a_real_import_can_take(self):
        # The text gate must never hide a parse: any Import or ImportFrom
        # node naming ``gi`` puts matching source text in the file. Comment
        # and string mentions are admitted too -- overmatching only costs
        # the parse the strict scan would have spent.
        for source in (
            "import gi\n",
            "import gi.repository\n",
            "import gi.repository as gi_rep\n",
            "from gi import Gtk\n",
            "from gi.repository import Gtk\n",
            "x = 1; import gi\n",
            "import gi \\n    as g\n",
            "import \\\n    gi\n",
            "from \\\n    gi import Api\n",
            "x = 1; # import git\nimport gi\n",
            "# from gi it never comes\nfrom gi import Api\n",
        ):
            with self.subTest(source=source):
                self.assertTrue(_has_importable_gi(source), source)

    def test_the_text_gate_rejects_text_only_gi_neighbours(self):
        # A word boundary after ``gi`` is what the gate matches: an import
        # of another module over the same prefix, or prose mentioning gi,
        # matches nothing and the file skips its parse.
        for source in (
            "import gigi\n",
            "import git\n",
            "from giraffe import neck\n",
            "run_child('-c', 'import git')\n",
            "# from giraffe import neck\n",
        ):
            with self.subTest(source=source):
                self.assertFalse(_has_importable_gi(source), source)

    def test_the_text_gate_admits_files_the_detector_later_clears_harmlessly(self):
        # Files the gate admits but the detector clears (string constants
        # mentioning ``import gi``, this module's own tests included) are
        # parsed and re-scanned: the gate may overmatch, but every repo file
        # it admits that holds no real Import node must yield no finding, so
        # the tree-scan assertion below stays a statement about real code.
        findings: list[str] = []
        for directory in _SCANNED_DIRS:
            for path in (ROOT / directory).rglob("*.py"):
                if "__pycache__" in path.parts:
                    continue
                source = path.read_text(encoding="utf-8")
                if not _has_importable_gi(source):
                    continue
                findings.extend(
                    _gi_import_messages(str(path.relative_to(ROOT)), source)
                )
        self.assertEqual(
            [],
            findings,
            "a file the text gate admits carries a real gi import: the "
            "repository is not clean",
        )


if __name__ == "__main__":
    unittest.main()
