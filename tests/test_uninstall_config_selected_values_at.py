"""`read_selected_values_at` returns the wanted INI values, or nothing.

The uninstall diagnostics call this wrapper for every config surface they
inspect. Its contract (its docstring): read and select the INI values at a
path, returning an empty mapping when the file is unavailable. Watched here:
an absent path, a directory at the path, and an over-cap file all come back
empty; a readable file returns its wanted (section, key) values with the last
occurrence winning and unwanted keys dropped.
"""

import os
import unittest

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.tmp_dir import make_tmp_dir
from tools import uninstall_config

WANTED = {"General": ("theme",)}


class TestReadSelectedValuesAt(unittest.TestCase):
    def test_an_absent_file_returns_an_empty_mapping(self):
        tmp = str(make_tmp_dir(self))
        path = os.path.join(tmp, "missing", "kdeglobals")

        self.assertEqual({}, uninstall_config.read_selected_values_at(path, WANTED))

    def test_a_directory_at_the_path_returns_an_empty_mapping(self):
        tmp = str(make_tmp_dir(self))
        path = os.path.join(tmp, "kdeglobals")
        os.makedirs(path)

        self.assertEqual({}, uninstall_config.read_selected_values_at(path, WANTED))

    def test_a_readable_file_returns_the_last_wanted_value_only(self):
        tmp = str(make_tmp_dir(self))
        path = os.path.join(tmp, "kdeglobals")
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(
                "[General]\n"
                "theme=First\n"
                "theme=Second\n"
                "other=Ignored\n"
                "[Other]\n"
                "theme=AlsoIgnored\n"
            )

        self.assertEqual(
            {("General", "theme"): "Second"},
            uninstall_config.read_selected_values_at(path, WANTED),
        )

    def test_an_over_cap_file_returns_an_empty_mapping(self):
        tmp = str(make_tmp_dir(self))
        path = os.path.join(tmp, "kdeglobals")
        head = b"[General]\ntheme=Ours\n"
        with open(path, "wb") as handle:
            handle.write(head)
            handle.write(b"#" * (uninstall_config._MAX_CONFIG_BYTES + 1 - len(head)))

        self.assertEqual({}, uninstall_config.read_selected_values_at(path, WANTED))


if __name__ == "__main__":
    unittest.main()
