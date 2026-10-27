"""Tests for tests/support/file_identity.py -- the shared stat fingerprint.

Both test-side unchanged-file caches key their entries on this one fingerprint:
the SVG tree cache in ``support.svg_case`` and the Xcursor parse cache in
``support.xcursor``. Their suites pin the cache behaviour with the helper
mocked away (``test_svg_case``) or through a read that fails before the
fingerprint matters (``test_xcursor``), so no test pins the fingerprint's own
contract; these do, so a change to the identity rule is caught here rather
than in both caches at once.

Run with the project's check harness (stdlib unittest)::

    python3 -m unittest discover -s tests -v
"""

from __future__ import annotations

import os
import unittest

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support import tmp_dir
from support.file_identity import fingerprint_or_none


class TestFingerprintOrNone(unittest.TestCase):
    def setUp(self):
        self.directory = tmp_dir.make_tmp_dir(self)

    def test_the_fingerprint_is_the_documented_stat_identity(self):
        path = self.directory / "viewitem.svg"
        path.write_text("<svg id='one'/>", encoding="utf-8")
        stat = os.stat(path)
        self.assertEqual(
            fingerprint_or_none(path),
            (stat.st_ino, stat.st_size, stat.st_mtime_ns, stat.st_ctime_ns),
        )

    def test_two_different_files_have_different_fingerprints(self):
        first = self.directory / "first.svg"
        second = self.directory / "second.svg"
        first.write_text("<svg id='one'/>", encoding="utf-8")
        second.write_text("<svg id='two'/>", encoding="utf-8")
        self.assertNotEqual(fingerprint_or_none(first), fingerprint_or_none(second))

    def test_an_untouched_file_keeps_its_fingerprint(self):
        # The property both caches rely on to serve a cached parse: calling
        # again on a file nobody touched yields the same identity.
        path = self.directory / "viewitem.svg"
        path.write_text("<svg id='one'/>", encoding="utf-8")
        self.assertEqual(fingerprint_or_none(path), fingerprint_or_none(path))

    def test_a_rewritten_file_gets_a_new_fingerprint(self):
        # The property both caches rely on to invalidate: the write changes
        # the size, so no stat field the fingerprint carries can hide it.
        path = self.directory / "viewitem.svg"
        path.write_text("<svg id='one'/>", encoding="utf-8")
        first = fingerprint_or_none(path)
        path.write_text("<svg id='one-two'/>", encoding="utf-8")
        self.assertNotEqual(first, fingerprint_or_none(path))

    def test_a_file_that_cannot_be_statted_yields_none(self):
        # A missing path and a dangling symlink both fail the stat, and the
        # contract says either yields None so the caller's read reports the
        # missing or unreadable path instead of a bogus identity.
        missing = self.directory / "missing.svg"
        dangling = self.directory / "dangling.svg"
        dangling.symlink_to(self.directory / "gone.svg")
        self.assertIsNone(fingerprint_or_none(missing))
        self.assertIsNone(fingerprint_or_none(dangling))


if __name__ == "__main__":
    unittest.main()
