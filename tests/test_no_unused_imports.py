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
