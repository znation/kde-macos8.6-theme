"""Direct pins for the shared scratch-home helpers.

`support.tmp_dir.make_config_home` is the one helper the `_uninstall`
diagnostic suites stage their config homes through; these tests pin its
contract: the returned pair is (scratch root, `<tmp>/config`), nothing under
it is created eagerly (suites stage exactly what a case needs), and the
scratch root is removed when the case's cleanups run.
"""

import os
import unittest

from support.tmp_dir import make_config_home, make_tmp_dir


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

    def test_make_tmp_dir_cleanup_carries_to_config_home(self):
        # The config-home helper reuses make_tmp_dir, so the same case-cleanup
        # registration applies; pin the underlying helper's own contract too.
        tmp = make_tmp_dir(self)
        self.assertTrue(os.path.isdir(tmp))
        self.doCleanups()
        self.assertFalse(os.path.exists(tmp))


if __name__ == "__main__":
    unittest.main()
