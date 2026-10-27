"""Pin that the suite's own Python process imports no GTK introspection.

The GTK pixel suites run their GTK work inside child interpreters
(``tests/test_gtk_theme.py`` via its ``-c`` programs,
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
import unittest

from support.repo_root import ROOT

# One scan over the repo's Python packages keeps the invariant tree-wide:
# a tool or helper that imported ``gi`` in-process would poison the whole
# suite process the same way a test does.
_SCANNED_DIRS = ("tools", "tests")


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
                findings.extend(
                    _gi_import_messages(
                        str(path.relative_to(ROOT)),
                        path.read_text(encoding="utf-8"),
                    )
                )
        self.assertEqual(
            findings,
            [],
            "an in-process import of gi leaves GLib's worker threads in the "
            "suite process, which poisons every later tests/support/"
            "snippet_child.py os.fork FIFO guard (Python 3.12+ deprecates "
            "forking a multi-threaded process): move the GTK work into a "
            "child interpreter, as tests/test_gtk_theme.py and "
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


if __name__ == "__main__":
    unittest.main()
