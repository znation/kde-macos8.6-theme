"""Guard that no ``tests/**/*.py`` file defines a name twice in one scope.

A later ``def`` of the same name in the same scope (module body or
one class body) replaces the earlier definition when the module is imported,
so a copy-pasted test method silently shadows the test it was filed under and
the suite stays green while that test never executes. The check parses every
``*.py`` file below ``tests/`` (support packages included, since a mixin's
shadowed ``setUp`` hides just as silently) and fails naming each duplicated
definition with both line numbers.
"""

from __future__ import annotations

import ast
import os
import unittest

from support.tmp_dir import make_tmp_dir


TESTS_DIR = os.path.dirname(os.path.abspath(__file__))


def python_files(directory):
    """Return every ``*.py`` path under *directory*, ``__pycache__`` skipped.

    The shadowing check is static: it parses files instead of importing them,
    so it also sees modules discovery would refuse to import, and it needs
    paths rather than dotted names.
    """
    paths = []
    for entry in sorted(os.listdir(directory)):
        full = os.path.join(directory, entry)
        if entry.endswith(".py"):
            paths.append(full)
        elif os.path.isdir(full) and entry != "__pycache__":
            paths.extend(python_files(full))
    return paths


def shadowed_definitions(path):
    """Return the same-scope duplicated ``def`` names in the file at *path*.

    Each finding is a ``(name, first_line, shadow_line)`` tuple: only the
    direct ``def`` children of the module body and of each class body are
    compared, because a later def of the same name in the same scope replaces
    the earlier one at import time and the earlier test silently never runs.
    Defs nested inside functions are local to each call and cannot shadow a
    sibling test, so they stay out of scope; the same method name in two
    different classes is ordinary overriding-shaped suite structure, not
    shadowing, and is not reported either.
    """
    with open(path, encoding="utf-8") as handle:
        tree = ast.parse(handle.read(), filename=path)
    scopes = [tree.body]
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            scopes.append(node.body)
    findings = []
    for body in scopes:
        seen = {}
        for child in body:
            if not isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if child.name in seen:
                findings.append((child.name, seen[child.name], child.lineno))
            else:
                seen[child.name] = child.lineno
    return findings


def shadowed_def_files(directory):
    """Return ``(relative_path, findings)`` for files under *directory* with one.

    *findings* is what :func:`shadowed_definitions` returns for the file, and
    each path is relative to *directory*, so the diagnostic names the file to
    fix and both line numbers to look between.
    """
    found = []
    for path in sorted(python_files(directory)):
        findings = shadowed_definitions(path)
        if findings:
            found.append((os.path.relpath(path, directory), findings))
    return found


class TestShadowedDefinitions(unittest.TestCase):
    def test_no_test_module_defines_a_name_twice_in_the_same_scope(self):
        # A later def of the same name in the same scope replaces the earlier
        # one at import time, so a copy-pasted test method silently shadows
        # the test it was filed under while the suite stays green. Two such
        # shadowings merged to main and were found only by hand (the
        # missing-kdialog slider test and the escaped-whitespace GTK test,
        # both fixed 2026-11-10); this guard parses every tests/*.py file so
        # the next one cannot land unreported.
        paths = python_files(TESTS_DIR)
        # Without this, a broken directory listing would make the assertion
        # below pass vacuously (no files checked, no shadows found).
        self.assertIn(os.path.join(TESTS_DIR, "test_suite_shadowed_defs.py"), paths)
        shadowed = shadowed_def_files(TESTS_DIR)
        self.assertEqual(
            shadowed,
            [],
            "these files define a def name twice in one scope, so the later "
            "definition replaces the earlier one at import time and the "
            "earlier test silently never runs; delete the shadowed "
            "definition or rename the survivor (each entry lists the name "
            "and both line numbers): " + repr(shadowed),
        )

    def test_a_shadowed_test_method_is_reported(self):
        # Prove the guard bites: a copy-pasted second def of the same test
        # name in one class is exactly what
        # test_no_test_module_defines_a_name_twice_in_the_same_scope must
        # catch, naming the method and both of its line numbers.
        source = (
            "import unittest\n"
            "\n"
            "class TestProbe(unittest.TestCase):\n"
            "    def test_first(self):\n"
            "        self.assertTrue(True)\n"
            "\n"
            "    def test_first(self):\n"
            "        self.assertTrue(True)\n"
        )
        tmp = make_tmp_dir(self)
        (tmp / "test_probe.py").write_text(source, encoding="utf-8")
        self.assertEqual(
            shadowed_def_files(str(tmp)),
            [("test_probe.py", [("test_first", 4, 7)])],
        )

    def test_a_shadowed_async_test_method_is_reported(self):
        # Async defs replace earlier same-named defs in a class body just as
        # ordinary defs do, so the static guard must catch them too.
        source = (
            "class TestProbe:\n"
            "    async def test_first(self):\n"
            "        return 1\n"
            "\n"
            "    async def test_first(self):\n"
            "        return 2\n"
        )
        tmp = make_tmp_dir(self)
        (tmp / "test_probe.py").write_text(source, encoding="utf-8")
        self.assertEqual(
            shadowed_def_files(str(tmp)),
            [("test_probe.py", [("test_first", 2, 5)])],
        )

    def test_a_shadowed_module_level_helper_is_reported(self):
        # The same shadowing in a support module hides a helper just as
        # silently: a mixin whose setUp is redefined below its use site is
        # the same import-time replacement, so module scopes are checked too.
        source = (
            "def helper():\n"
            "    return 1\n"
            "\n"
            "def helper():\n"
            "    return 2\n"
        )
        tmp = make_tmp_dir(self)
        (tmp / "support_probe.py").write_text(source, encoding="utf-8")
        self.assertEqual(
            shadowed_def_files(str(tmp)),
            [("support_probe.py", [("helper", 1, 4)])],
        )

    def test_the_same_method_name_in_two_classes_is_not_reported(self):
        # The negative control: two classes may each define a method of the
        # same name -- that is ordinary suite structure, not shadowing -- so
        # the check compares only within one scope.
        source = (
            "import unittest\n"
            "\n"
            "class TestA(unittest.TestCase):\n"
            "    def test_ok(self):\n"
            "        self.assertTrue(True)\n"
            "\n"
            "class TestB(unittest.TestCase):\n"
            "    def test_ok(self):\n"
            "        self.assertTrue(True)\n"
        )
        tmp = make_tmp_dir(self)
        (tmp / "test_probe.py").write_text(source, encoding="utf-8")
        self.assertEqual(shadowed_def_files(str(tmp)), [])


if __name__ == "__main__":
    unittest.main()
