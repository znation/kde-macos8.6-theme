"""Guard a test file's pin registries against a repeated dictionary key.

A pin registry is a module-level ``UPPER_CASE`` dict a test file iterates
``.items()`` over or indexes by key to pin one entry per state, direction,
shape or slice. A merge that adds a row twice -- the same key literal pasted
with a changed value -- is legal Python: the second entry silently replaces
the first, and every pin the discarded row carried stops being asserted
while the suite stays green. :func:`assert_registries_name_each_key_once`
parses the test file's own AST and fails when any named registry repeats a
literal string key, its nested dict values included.

Plain string keys need no evaluation, so the guard reads them without
executing the module; a registry that grows a computed key must extend the
guard first.
"""

from __future__ import annotations

import ast

from support.invariants import parsed_module
from support.repo_root import ROOT


def assert_registries_name_each_key_once(case, module_path, registry_names):
    """Assert each named registry dict in *module_path* repeats no key.

    *case* is the calling ``unittest.TestCase``; a missing registry name, a
    non-dict literal or a non-literal key fails there with the registry's
    name, so the extension the failure asks for is the guard itself.
    """
    tree = parsed_module(module_path, ROOT)
    literals = {}
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
        ):
            literals[node.targets[0].id] = node.value
    for name in registry_names:
        literal = literals.get(name)
        case.assertIsNotNone(
            literal, f"{name} is not a module-level assignment in {module_path}"
        )
        case.assertIsInstance(
            literal, ast.Dict, f"{name} in {module_path} is not a dict literal"
        )
        _assert_keys_distinct(case, literal, name)


def _assert_keys_distinct(case, node, label):
    """Assert the dict literal *node*, and its dict values, repeat no key."""
    names = []
    for key in node.keys:
        if key is None or not isinstance(key, ast.Constant) or not isinstance(
            key.value, str
        ):
            case.fail(f"{label} has a non-literal key; extend the registry guard")
            return
        names.append(key.value)
    repeats = sorted(name for name in set(names) if names.count(name) > 1)
    case.assertEqual(repeats, [], f"{label} repeats the key(s) {repeats}")
    for key, value in zip(node.keys, node.values):
        if isinstance(value, ast.Dict):
            _assert_keys_distinct(case, value, f"{label}.{key.value}")
