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


if __name__ == "__main__":
    unittest.main()
