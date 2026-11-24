"""Drive the pin-registry key guard over manufactured registries.

``tests/test_kvantum_bevel_pixels.py`` and ``tests/test_kvantum_svg_arrows.py``
apply the guard to their shipped registries, which never repeat a key, so the
rejection boundary is invisible to them: a guard whose duplicate comparison
were a no-op would leave every shipped test green. These tests manufacture the
module shapes the shipped files never hold -- a flat duplicate, a nested
duplicate, a non-literal key, a missing registry and a clean registry -- and
observe the guard's answer, plus the module-level contract: a same-named dict
inside a function body must not shadow the module-level registry.

Run with the project's check harness (stdlib unittest)::

    python3 -m unittest discover -s tests -v
"""

from __future__ import annotations

import os
import tempfile
import unittest

from support.pin_registries import assert_registries_name_each_key_once


class TestPinRegistriesGuard(unittest.TestCase):
    """Assert the guard's answer for each manufactured registry shape."""

    def _guard_against(self, source, registry_names):
        """Run the guard over *source* in a scratch root; return its message.

        The scratch root bounds the read the way the caller's root does, so
        the guard needs no repository write and the assertion, if any, carries
        the manufactured module's path.
        """
        with tempfile.TemporaryDirectory() as root:
            module_path = os.path.join(root, "registry_module.py")
            with open(module_path, "w", encoding="utf-8") as module:
                module.write(source)
            with self.assertRaises(AssertionError) as caught:
                assert_registries_name_each_key_once(
                    self, module_path, registry_names, root
                )
        return str(caught.exception)

    def test_a_flat_duplicate_is_rejected_by_key_name(self):
        message = self._guard_against('R = {"a": 1, "b": 2, "a": 3}\n', ("R",))
        self.assertIn("R repeats the key(s) ['a']", message)

    def test_a_nested_duplicate_is_rejected_under_its_registry(self):
        message = self._guard_against(
            'R = {"x": {"p": 1, "p": 2}, "y": {"q": 1}}\n', ("R",)
        )
        self.assertIn("R.x repeats the key(s) ['p']", message)

    def test_a_non_literal_key_is_rejected(self):
        message = self._guard_against('R = {"a": 1, ("b",): 2}\n', ("R",))
        self.assertIn("R has a non-literal key", message)

    def test_a_computed_key_is_rejected(self):
        message = self._guard_against('K = "k"\nR = {K: 1, "b": 2}\n', ("R",))
        self.assertIn("R has a non-literal key", message)

    def test_a_missing_registry_is_rejected_by_name(self):
        message = self._guard_against('R = {"a": 1}\n', ("S",))
        self.assertIn("S is not a module-level assignment", message)

    def test_a_clean_registry_is_accepted(self):
        with tempfile.TemporaryDirectory() as root:
            module_path = os.path.join(root, "registry_module.py")
            with open(module_path, "w", encoding="utf-8") as module:
                module.write('R = {"x": {"p": 1}, "y": {"q": 1}}\n')
            assert_registries_name_each_key_once(self, module_path, ("R",), root)

    def test_a_function_local_dict_does_not_shadow_the_registry(self):
        # A same-named duplicate inside a function body is not the registry:
        # the guard must inspect the module-level dict and keep accepting it.
        source = (
            "def helper():\n"
            '    R = {"a": 1, "a": 2}\n'
            'R = {"a": 1, "b": 2}\n'
        )
        with tempfile.TemporaryDirectory() as root:
            module_path = os.path.join(root, "registry_module.py")
            with open(module_path, "w", encoding="utf-8") as module:
                module.write(source)
            assert_registries_name_each_key_once(self, module_path, ("R",), root)


if __name__ == "__main__":
    unittest.main()
