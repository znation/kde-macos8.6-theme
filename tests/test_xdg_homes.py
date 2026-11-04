"""Tests for tools/xdg_homes.py's shared XDG home resolution.

Both the GTK and cursor apply tools read these resolvers, so an absolute XDG
value, the default below ``$HOME`` and the ``None`` result for an unusable
``HOME`` are pinned once here.
"""

from __future__ import annotations

import unittest
from pathlib import Path

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from tools import xdg_homes


class TestDefaultDataHome(unittest.TestCase):
    def test_absolute_home_names_the_fallback_child(self):
        # Unlike data_home, no XDG_DATA_HOME value is consulted: the default
        # is defined only by HOME, whatever the resolved data home is.
        for env in (
            {"HOME": "/home/u"},
            {"HOME": "/home/u", "XDG_DATA_HOME": "/data"},
            {"HOME": "/home/u", "XDG_DATA_HOME": "relative"},
            {"HOME": "/home/u", "XDG_DATA_HOME": ""},
        ):
            with self.subTest(env=env):
                self.assertEqual(
                    Path("/home/u/.local/share"),
                    xdg_homes.default_data_home(env),
                )

    def test_without_an_absolute_home_is_none(self):
        # No usable HOME means no default to name, even with an absolute
        # XDG_DATA_HOME that data_home would resolve from.
        for env in (
            {},
            {"HOME": "relative/home"},
            {"HOME": ""},
            {"XDG_DATA_HOME": "/data"},
        ):
            with self.subTest(env=env):
                self.assertIsNone(xdg_homes.default_data_home(env))


class TestDataHome(unittest.TestCase):
    def test_absolute_data_home_is_used_even_without_home(self):
        self.assertEqual(
            Path("/data"),
            xdg_homes.data_home(
                {"XDG_DATA_HOME": "/data", "XDG_CONFIG_HOME": "/config"}
            ),
        )

    def test_empty_data_home_falls_back_to_home(self):
        self.assertEqual(
            Path("/home/u/.local/share"),
            xdg_homes.data_home({"XDG_DATA_HOME": "", "HOME": "/home/u"}),
        )

    def test_relative_data_home_falls_back_to_home(self):
        self.assertEqual(
            Path("/home/u/.local/share"),
            xdg_homes.data_home(
                {"XDG_DATA_HOME": "relative", "HOME": "/home/u"}
            ),
        )

    def test_data_home_without_an_absolute_home_is_none(self):
        for env in ({}, {"HOME": "relative/home"}):
            with self.subTest(env=env):
                self.assertIsNone(xdg_homes.data_home(env))


class TestConfigHome(unittest.TestCase):
    def test_absolute_config_home_is_used_even_without_home(self):
        self.assertEqual(
            Path("/config"),
            xdg_homes.config_home({"XDG_CONFIG_HOME": "/config"}),
        )

    def test_empty_config_home_falls_back_to_home(self):
        self.assertEqual(
            Path("/home/u/.config"),
            xdg_homes.config_home({"XDG_CONFIG_HOME": "", "HOME": "/home/u"}),
        )

    def test_relative_config_home_falls_back_to_home(self):
        self.assertEqual(
            Path("/home/u/.config"),
            xdg_homes.config_home(
                {"XDG_CONFIG_HOME": "relative", "HOME": "/home/u"}
            ),
        )

    def test_config_home_without_an_absolute_home_is_none(self):
        for env in ({}, {"HOME": "relative/home"}):
            with self.subTest(env=env):
                self.assertIsNone(xdg_homes.config_home(env))


class TestRequireHome(unittest.TestCase):
    class _Refusal(Exception):
        pass

    def test_resolved_path_is_returned_unchanged(self):
        self.assertEqual(
            Path("/config"),
            xdg_homes.require_home(
                Path("/config"), {}, "XDG_CONFIG_HOME", "$HOME/.config", self._Refusal
            ),
        )

    def test_unresolvable_refusal_names_both_received_values(self):
        # The exact wording is the contract the apply-gtk and remove-kvantum
        # refusals share: each variable's state (unset, empty, or the
        # received value in shell quoting) and the fallback that could not
        # be used.
        cases = [
            (
                {},
                "XDG_CONFIG_HOME is unset and HOME is unset, so the "
                "$HOME/.config fallback cannot be used; set XDG_CONFIG_HOME "
                "to an absolute path or export an absolute HOME",
            ),
            (
                {"XDG_CONFIG_HOME": "", "HOME": ""},
                "XDG_CONFIG_HOME is empty and HOME is empty, so the "
                "$HOME/.config fallback cannot be used; set XDG_CONFIG_HOME "
                "to an absolute path or export an absolute HOME",
            ),
            (
                {"XDG_CONFIG_HOME": "relative", "HOME": "home/relative"},
                "XDG_CONFIG_HOME is not an absolute path ('relative') and "
                "HOME is not an absolute path ('home/relative'), so the "
                "$HOME/.config fallback cannot be used; set XDG_CONFIG_HOME "
                "to an absolute path or export an absolute HOME",
            ),
        ]
        for env, message in cases:
            with self.subTest(env=env):
                with self.assertRaises(self._Refusal) as caught:
                    xdg_homes.require_home(
                        None,
                        env,
                        "XDG_CONFIG_HOME",
                        "$HOME/.config",
                        self._Refusal,
                    )
                self.assertEqual(message, str(caught.exception))

    def test_unresolvable_data_home_refusal_names_the_data_home_fallback(self):
        with self.assertRaises(self._Refusal) as caught:
            xdg_homes.require_home(
                None,
                {},
                "XDG_DATA_HOME",
                "$HOME/.local/share",
                self._Refusal,
            )
        self.assertEqual(
            "XDG_DATA_HOME is unset and HOME is unset, so the "
            "$HOME/.local/share fallback cannot be used; set XDG_DATA_HOME "
            "to an absolute path or export an absolute HOME",
            str(caught.exception),
        )


if __name__ == "__main__":
    unittest.main()
