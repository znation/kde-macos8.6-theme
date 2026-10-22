"""Every test module must carry the ``unittest.main()`` entry-point guard.

``make check`` runs the suite through ``unittest discover``, which imports each
module under its own name, so the guard never fires there. It matters when a
contributor runs one module directly -- ``python3 tests/test_colorscheme.py``
-- which is the quickest way to reproduce a single failure. A module without
the guard exits 0 and prints nothing, so a failing test looks like a passing
one and the reader is sent looking for the bug elsewhere.

Fourteen modules had lost the guard: a file split into smaller modules, or an
extraction that moved a class into a module of its own, wrote the new file
without the guard the rest of the tree carries. Nothing tied the convention to
the tree, so the next split could drop it again unnoticed. These tests read
every ``tests/test_*.py`` module and require the guard, so a module that
loses it fails here instead of quietly doing nothing when it is run.
"""

from __future__ import annotations

import ast
import unittest

from support import containment
from support import repo_root

TESTS_DIR = repo_root.ROOT / "tests"


def test_modules():
    """Return the repository's test modules, in name order."""
    return sorted(TESTS_DIR.glob("test_*.py"))


def is_main_guard(node):
    """Return whether *node* is an ``if __name__ == "__main__":`` statement.

    Only a guard at module level counts: one nested in a class or a function
    never runs when the file is executed as a script, so a module carrying
    only a nested guard would still exit 0 silently.
    """
    test = node.test
    if not isinstance(test, ast.Compare) or len(test.ops) != 1:
        return False
    if not isinstance(test.ops[0], ast.Eq):
        return False
    if not isinstance(test.left, ast.Name) or test.left.id != "__name__":
        return False
    return any(
        isinstance(comparator, ast.Constant) and comparator.value == "__main__"
        for comparator in test.comparators
    )


def calls_unittest_main(node):
    """Return whether *node*'s guard body calls ``unittest.main()``."""
    return any(
        isinstance(statement, ast.Expr)
        and isinstance(statement.value, ast.Call)
        and isinstance(statement.value.func, ast.Attribute)
        and statement.value.func.attr == "main"
        for statement in node.body
    )


def module_guards(tree):
    """Return the module-level ``__main__`` guards in the parsed *tree*."""
    return [
        node
        for node in tree.body
        if isinstance(node, ast.If) and is_main_guard(node)
    ]


class TestEntryPointGuard(unittest.TestCase):
    """Each test module must run its own tests when executed directly."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.modules = test_modules()
        cls.trees = {
            path.name: ast.parse(
                containment.read_text(path, repo_root.ROOT)
            )
            for path in cls.modules
        }

    def test_the_tree_holds_test_modules_to_check(self):
        # An empty glob would make the assertions below vacuously true, so
        # name the cause instead of passing silently.
        self.assertTrue(self.modules, "no test modules found under tests/")

    def test_every_test_module_has_the_entry_point_guard(self):
        for name, tree in self.trees.items():
            with self.subTest(module=name):
                guards = module_guards(tree)
                self.assertEqual(
                    len(guards),
                    1,
                    f"{name} must hold exactly one module-level "
                    'if __name__ == "__main__": guard',
                )
                self.assertTrue(
                    calls_unittest_main(guards[0]),
                    f"{name}'s guard must call unittest.main()",
                )

    def test_every_test_module_ends_with_the_guard(self):
        for name, tree in self.trees.items():
            with self.subTest(module=name):
                guards = module_guards(tree)
                self.assertTrue(
                    guards,
                    f"{name} has no module-level __main__ guard",
                )
                self.assertIs(
                    tree.body[-1],
                    guards[0],
                    f"{name}'s __main__ guard must be its last statement",
                )


if __name__ == "__main__":
    unittest.main()
