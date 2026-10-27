"""Tests for the unused-import scanner the suite runs over tools/ and tests/.

The scanner's own tree-clean assertion is the point: no import under ``tools/``
or ``tests/`` may name a value its module never reads unless a ``# noqa``
comment, an ``__all__`` entry or another module's import keeps it. The
behavioural tests below pin each allowance and the detection itself against
synthetic trees, so a scanner bug cannot silently pass or fail the tree.
"""

from __future__ import annotations

import unittest
from pathlib import Path

from support.repo_root import ROOT
from support.tmp_dir import make_tmp_dir
from support.unused_imports import unused_imports


class TestNoUnusedImports(unittest.TestCase):
    """`unused_imports` flags dead imports and honours its allowances."""

    def test_the_repository_tree_is_clean(self):
        findings = unused_imports(ROOT)
        self.assertEqual(
            findings,
            [],
            "imports no statement reads (remove them, mark a deliberate "
            "side-effect import with # noqa, or re-export it in __all__)",
        )

    def _write(self, root: Path, relative: str, text: str) -> None:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def _findings(self, case, files: dict[str, str]) -> list[str]:
        root = make_tmp_dir(case)
        for relative, text in files.items():
            self._write(root, relative, text)
        return unused_imports(root, ("pkg",))

    def test_an_import_no_statement_reads_is_flagged(self):
        findings = self._findings(
            self, {"pkg/mod.py": "import os\n"}
        )
        self.assertEqual(len(findings), 1, findings)
        self.assertIn("pkg/mod.py:1: unused import os", findings[0])

    def test_an_import_a_statement_reads_is_kept(self):
        findings = self._findings(
            self, {"pkg/mod.py": "import os\n\nvalue = os.sep\n"}
        )
        self.assertEqual(findings, [])

    def test_a_noqa_marked_import_is_kept(self):
        findings = self._findings(
            self, {"pkg/mod.py": "import os  # noqa: F401  (side effect)\n"}
        )
        self.assertEqual(findings, [])

    def test_a_multiline_noqa_marked_import_is_kept(self):
        findings = self._findings(
            self,
            {
                "pkg/mod.py": (
                    "from os import (\n"
                    "    sep,  # noqa: F401  (side effect)\n"
                    ")\n"
                )
            },
        )
        self.assertEqual(findings, [])

    def test_the_annotations_future_import_is_kept(self):
        findings = self._findings(
            self,
            {"pkg/mod.py": "from __future__ import annotations\n"},
        )
        self.assertEqual(findings, [])

    def test_a_star_import_is_kept(self):
        findings = self._findings(
            self, {"pkg/mod.py": "from os import *\n"}
        )
        self.assertEqual(findings, [])

    def test_an_all_entry_re_exports_the_import(self):
        findings = self._findings(
            self,
            {"pkg/mod.py": 'import os\n\n__all__ = ["os"]\n'},
        )
        self.assertEqual(findings, [])

    def test_an_annotated_all_entry_re_exports_the_import(self):
        # `__all__: list[str] = ["os"]` is an assignment too: the annotated
        # form must collect its strings like the plain one, or a typed
        # re-export hub flags its own dead imports.
        findings = self._findings(
            self,
            {"pkg/mod.py": 'import os\n\n__all__: list[str] = ["os"]\n'},
        )
        self.assertEqual(findings, [])

    def test_an_all_augassign_entry_re_exports_the_import(self):
        # `__all__ += ["os"]` is the extend form a re-export hub uses: the
        # augmented assignment must collect its strings like the plain one,
        # or a hub that grows __all__ flags its own dead imports.
        findings = self._findings(
            self,
            {
                "pkg/mod.py": (
                    'import os\n\n__all__ = []\n__all__ += ["os"]\n'
                )
            },
        )
        self.assertEqual(findings, [])

    def test_an_augassign_to_another_name_keeps_the_flag(self):
        # Only an augmented assignment whose target is `__all__` re-exports:
        # growing a plain list honours no import, so the flag stays.
        findings = self._findings(
            self,
            {
                "pkg/mod.py": (
                    'import os\n\nexports = []\nexports += ["os"]\n'
                )
            },
        )
        self.assertEqual(len(findings), 1, findings)
        self.assertIn("pkg/mod.py:1: unused import os", findings[0])

    def test_a_reassignment_of_the_imported_name_keeps_the_flag(self):
        # A Store context is not a read: `os = None` uses neither the
        # binding nor the value, so the import it shadows stays a finding.
        findings = self._findings(
            self, {"pkg/mod.py": "import os\n\nos = None\n"}
        )
        self.assertEqual(len(findings), 1, findings)
        self.assertIn("pkg/mod.py:1: unused import os", findings[0])

    def test_a_del_of_the_imported_name_keeps_the_flag(self):
        # `del os` detaches the binding without reading it, so the import
        # it clears stays a finding too.
        findings = self._findings(
            self, {"pkg/mod.py": "import os\n\ndel os\n"}
        )
        self.assertEqual(len(findings), 1, findings)
        self.assertIn("pkg/mod.py:1: unused import os", findings[0])

    def test_an_annotated_all_declaration_without_a_value_keeps_the_flag(self):
        # A bare `__all__: list[str]` names no strings, so it re-exports
        # nothing and the dead import stays a finding.
        findings = self._findings(
            self,
            {"pkg/mod.py": "import os\n\n__all__: list[str]\n"},
        )
        self.assertEqual(len(findings), 1, findings)
        self.assertIn("pkg/mod.py:1: unused import os", findings[0])

    def test_a_name_another_module_imports_from_here_is_kept(self):
        # `consts.X` feeds `mod.py`, whose re-export feeds `user.py`: the
        # shared-constant hub pattern (aurorae_fixtures' palette re-exports).
        findings = self._findings(
            self,
            {
                "pkg/consts.py": "X = 1\n",
                "pkg/mod.py": "from pkg.consts import X\n",
                "pkg/user.py": "from pkg.mod import X\n\nvalue = X\n",
            },
        )
        self.assertEqual(findings, [])

    def test_an_aliased_import_from_here_keeps_the_imported_name(self):
        # `from pkg.mod import os as platform` reads mod.py's `import os`;
        # the re-export allowance follows the name imported, not the alias.
        findings = self._findings(
            self,
            {
                "pkg/mod.py": "import os\n",
                "pkg/user.py": (
                    "from pkg.mod import os as platform\n\nvalue = platform\n"
                ),
            },
        )
        self.assertEqual(findings, [])

    def test_an_aliased_import_keeps_only_the_name_actually_imported(self):
        # The alias must not bless a different name: user.py imports `sys`
        # (as `os`), so mod.py's `import os` stays dead.
        findings = self._findings(
            self,
            {
                "pkg/mod.py": "import os\n",
                "pkg/user.py": "from pkg.mod import sys as os\n\nvalue = os\n",
            },
        )
        self.assertEqual(len(findings), 1, findings)
        self.assertIn("pkg/mod.py:1: unused import os", findings[0])

    def test_a_package_facade_re_export_keeps_the_submodule_import(self):
        # The facade ``__init__.py`` is skipped as a scan subject, but its
        # ``from .mod import thing`` is the import-from-elsewhere that keeps
        # mod.py's own import of ``thing`` alive: a consumer reads the name
        # through the package, so mod.py's re-export is not dead even though
        # no scanned module names mod.py directly and mod.py never reads it.
        findings = self._findings(
            self,
            {
                "pkg/__init__.py": "from .mod import thing\n",
                "pkg/mod.py": "from .thing import thing\n",
                "pkg/thing.py": "thing = 1\n",
                "pkg/user.py": "from pkg import thing\n\nvalue = thing\n",
            },
        )
        self.assertEqual(findings, [])

    def test_a_bare_relative_import_does_not_bless_the_submodules_import(self):
        # ``from . import thing`` imports the submodule pkg.thing, not a
        # name from it, so it must register only ("pkg", "thing") -- never
        # ("pkg.thing", "thing"), which would keep pkg/thing.py's own dead
        # import of the name ``thing`` alive under its dotted candidate.
        findings = self._findings(
            self,
            {
                "pkg/__init__.py": "",
                "pkg/other.py": "thing = 1\n",
                "pkg/thing.py": "from .other import thing\n",
                "pkg/mod.py": "from . import thing\n",
            },
        )
        self.assertEqual(
            findings,
            [
                "pkg/mod.py:1: unused import thing",
                "pkg/thing.py:1: unused import thing",
            ],
        )

    def test_findings_are_sorted_by_path_then_line(self):
        # The findings feed the tree-clean assertion's failure message, so
        # a module's offenders must list in line order: ast.walk visits
        # statements breadth-first, so a nested or block-nested import
        # would otherwise trail the module's later top-level imports.
        findings = self._findings(
            self,
            {
                "pkg/z.py": "import q\n",
                "pkg/mod.py": (
                    "def f():\n"
                    "    import b\n"
                    "if True:\n"
                    "    import a\n"
                    "import c\n"
                ),
            },
        )
        self.assertEqual(
            findings,
            [
                "pkg/mod.py:2: unused import b",
                "pkg/mod.py:4: unused import a",
                "pkg/mod.py:5: unused import c",
                "pkg/z.py:1: unused import q",
            ],
        )

    def test_a_package_facade_is_not_scanned(self):
        findings = self._findings(
            self,
            {
                "pkg/__init__.py": "from os import sep\n",
                "pkg/mod.py": "value = 1\n",
            },
        )
        self.assertEqual(findings, [])

    def test_a_dotted_import_binds_its_top_level_name(self):
        # `import os.path` binds `os`; the plain name is what a use must read.
        findings = self._findings(
            self, {"pkg/mod.py": "import os.path\n\nvalue = os.sep\n"}
        )
        self.assertEqual(findings, [])


if __name__ == "__main__":
    unittest.main()
