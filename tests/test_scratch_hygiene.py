"""Pin the tracked tree free of run-scratch bookkeeping files.

The run tooling once wrote its scratch bookkeeping file (``.scratchpath``) into
the worktree instead of ``$TMPDIR`` and an accidental ``git add`` tracked it
(entry found by the readme role 2026-10-31). A tracked file whose content is a
single path into that run's temporary scratch directory carries nothing another
clone can resolve, and no repository file or recipe reads it. These tests fail
when such a file is tracked again, so stray bookkeeping at the repository root
cannot hide in the tracked tree while every check stays green.

Run with the project's check harness (stdlib unittest) via ``make check``.
"""

from __future__ import annotations

import os
import subprocess
import unittest

from support import repo_root


def tracked_files(root):
    """Return the tracked paths under *root*, from ``git ls-files``."""
    out = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z"],
        check=True,
        capture_output=True,
    )
    return out.stdout.decode("utf-8", "surrogateescape").split("\0")


class _TrackFailure(AssertionError):
    """A failure that names the one offending path, not the whole tree."""


class TestNoTrackedScratchFiles(unittest.TestCase):
    def test_scratchpath_is_not_tracked(self):
        if ".scratchpath" in tracked_files(repo_root.ROOT):
            raise _TrackFailure("'.scratchpath' is tracked; remove it (git rm)")

    def test_no_tracked_top_level_file_names_a_run_scratch_dir(self):
        # A top-level tracked file whose first line is a path into a per-run
        # scratch directory (tumwater's run scratch layout:
        # /tmp/tumwater-run-*/tmp.*) is bookkeeping that leaked into the tree.
        for name in tracked_files(repo_root.ROOT):
            if "/" in name:
                continue
            path = os.path.join(repo_root.ROOT, name)
            if not os.path.isfile(path):
                continue
            with open(path, "rb") as fh:
                first_line = fh.readline()
            if first_line.startswith(b"/tmp/tumwater-run-"):
                raise _TrackFailure(
                    f"tracked top-level file {name!r} names a run scratch "
                    f"dir: {first_line!r}"
                )


if __name__ == "__main__":
    unittest.main()
