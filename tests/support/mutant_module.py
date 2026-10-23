"""Class shapes the invariant register's reference resolver must reject.

``tests/support/invariants_mutations.py`` points the register's first row at these
classes to drive ``tests/invariants.py``'s resolver over class shapes the
shipped tests never define. None subclasses ``unittest.TestCase``, so unittest
collects no tests from this file and ``test_suite_discovery``'s misnamed-module
guard leaves it alone; the resolver still reads it with :func:`ast.parse`.
"""


class Helper:
    """A class with no test-shaped method; a reference to it names no test."""

    def helper(self):
        """Do nothing; the resolver must see no test-shaped method here."""
        pass


class NotATestCase:
    """A class unittest never collects, whatever its method names."""

    def test_looks_like_a_test(self):
        pass


class FakeTestCase:
    """A base that only looks like ``unittest.TestCase`` by name."""


class TestNotCollected(FakeTestCase):
    """A class whose ``*TestCase`` base is local and does not reach unittest."""

    def test_ok(self):
        pass
