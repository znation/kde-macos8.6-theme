"""Direct pins for the shared scratch-home helpers.

`support.tmp_dir.make_config_home` is the one helper the `_uninstall`
diagnostic suites stage their config homes through; these tests pin its
contract: the returned pair is (scratch root, `<tmp>/config`), nothing under
it is created eagerly (suites stage exactly what a case needs), and the
scratch root is removed when the case's cleanups run.

`make_session_home` is the same idea for the apply tool suites: its six-tuple
is (root, home, data, config, bin, env), home and bin exist and env maps the
four variables onto the paths, while data and config are created only when a
suite stages them.
"""

import os
import unittest

from support.tmp_dir import make_config_home, make_session_home, make_tmp_dir


class TestMakeConfigHome(unittest.TestCase):
    """The (tmp, config) pair contract."""

    def test_returns_the_scratch_root_and_its_config_path(self):
        tmp, config = make_config_home(self)
        # The scratch root exists; the config home is only a path (swapping
        # the pair's order would fail the isdir/is-not-exists pair).
        self.assertTrue(os.path.isdir(tmp))
        self.assertFalse(os.path.exists(config))
        self.assertEqual(config, os.path.join(tmp, "config"))

    def test_nothing_is_created_under_the_scratch_root(self):
        tmp, config = make_config_home(self)
        self.assertEqual(os.listdir(tmp), [])
        self.assertFalse(os.path.exists(config))

    def test_scratch_root_is_removed_at_cleanup(self):
        tmp, _config = make_config_home(self)
        self.assertTrue(os.path.isdir(tmp))
        self.doCleanups()
        self.assertFalse(os.path.exists(tmp))

    def test_make_tmp_dir_removes_its_scratch_dir_at_cleanup(self):
        # The config-home helper reuses make_tmp_dir, so the same case-cleanup
        # registration applies; pin the underlying helper's own contract too.
        tmp = make_tmp_dir(self)
        self.assertTrue(os.path.isdir(tmp))
        self.doCleanups()
        self.assertFalse(os.path.exists(tmp))


class TestMakeSessionHome(unittest.TestCase):
    """The (root, home, data, config, bin, env) tuple contract."""

    def test_returns_the_home_paths_and_env_that_maps_onto_them(self):
        root, home, data, config, bin_dir, env = make_session_home(self)
        # The env maps each variable onto its path; a swapped field or env
        # entry fails one of the four equality pins.
        self.assertEqual(env["HOME"], str(home))
        self.assertEqual(env["XDG_DATA_HOME"], str(data))
        self.assertEqual(env["XDG_CONFIG_HOME"], str(config))
        self.assertEqual(env["PATH"], str(bin_dir))
        for path in (home, bin_dir):
            self.assertTrue(os.path.isdir(path), str(path))
            self.assertTrue(str(path).startswith(str(root) + os.sep), str(path))

    def test_data_and_config_are_paths_only(self):
        root, _home, data, config, bin_dir, _env = make_session_home(self)
        self.assertEqual(sorted(os.listdir(root)), ["bin", "home"])
        self.assertFalse(os.path.exists(data))
        self.assertFalse(os.path.exists(config))
        self.assertEqual(os.listdir(bin_dir), [])

    def test_scratch_root_is_removed_at_cleanup(self):
        root, *_rest = make_session_home(self)
        self.assertTrue(os.path.isdir(root))
        self.doCleanups()
        self.assertFalse(os.path.exists(root))


if __name__ == "__main__":
    unittest.main()
