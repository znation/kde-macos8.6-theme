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


def tracked_run_scratch_files(root):
    """Return tracked top-level files whose first line names run scratch."""
    offenders = []
    for name in tracked_files(root):
        if "/" in name:
            continue
        path = os.path.join(root, name)
        if os.path.islink(path) or not os.path.isfile(path):
            continue
        with open(path, "rb") as fh:
            first_line = fh.readline()
        if first_line.startswith(b"/tmp/tumwater-run-") and b"/tmp." in first_line:
            offenders.append((name, first_line))
    return offenders


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
        for name, first_line in tracked_run_scratch_files(repo_root.ROOT):
            raise _TrackFailure(
                f"tracked top-level file {name!r} names a run scratch "
                f"dir: {first_line!r}"
            )

    def test_scan_finds_matching_top_level_file_and_ignores_nested_file(self):
        import tempfile

        with tempfile.TemporaryDirectory() as directory:
            subprocess.run(["git", "init", "-q", directory], check=True)
            os.makedirs(os.path.join(directory, "nested"))
            # Git's NUL-delimited path listing must preserve legal filenames
            # containing newlines; line-based parsing would split this name.
            leak_name = "leak\nname"
            with open(os.path.join(directory, leak_name), "wb") as fh:
                fh.write(b"/tmp/tumwater-run-example/tmp.work\nmore data\n")
            with open(os.path.join(directory, "nested", "note"), "wb") as fh:
                fh.write(b"/tmp/tumwater-run-example/tmp.nested\n")
            # A matching file in the worktree is not a tracked-tree leak
            # until Git lists it; the production guard intentionally scans
            # the index rather than arbitrary untracked scratch state.
            with open(os.path.join(directory, "untracked"), "wb") as fh:
                fh.write(b"/tmp/tumwater-run-example/tmp.untracked\n")
            subprocess.run(
                ["git", "-C", directory, "add", leak_name, "nested/note"],
                check=True,
            )

            self.assertEqual(
                tracked_run_scratch_files(directory),
                [(leak_name, b"/tmp/tumwater-run-example/tmp.work\n")],
            )

    def test_scan_finds_scratch_path_without_a_trailing_newline(self):
        import tempfile

        with tempfile.TemporaryDirectory() as directory:
            subprocess.run(["git", "init", "-q", directory], check=True)
            leak_name = "leak"
            with open(os.path.join(directory, leak_name), "wb") as fh:
                fh.write(b"/tmp/tumwater-run-example/tmp.work")
            subprocess.run(["git", "-C", directory, "add", leak_name], check=True)

            self.assertEqual(
                tracked_run_scratch_files(directory),
                [(leak_name, b"/tmp/tumwater-run-example/tmp.work")],
            )

    def test_scan_ignores_run_path_without_scratch_directory(self):
        import tempfile

        with tempfile.TemporaryDirectory() as directory:
            subprocess.run(["git", "init", "-q", directory], check=True)
            with open(os.path.join(directory, "note"), "wb") as fh:
                fh.write(b"/tmp/tumwater-run-example/log.txt\n")
            subprocess.run(["git", "-C", directory, "add", "note"], check=True)

            self.assertEqual(tracked_run_scratch_files(directory), [])

    def test_scan_does_not_follow_a_tracked_symlink(self):
        import tempfile

        with tempfile.TemporaryDirectory() as directory:
            subprocess.run(["git", "init", "-q", directory], check=True)
            target = os.path.join(directory, "target")
            with open(target, "wb") as fh:
                fh.write(b"/tmp/tumwater-run-example/tmp.work\n")
            link = os.path.join(directory, "link")
            os.symlink("target", link)
            subprocess.run(["git", "-C", directory, "add", "link"], check=True)

            # Git records a symlink's target text, not the target file's
            # contents, so the scanner must not treat it as leaked bookkeeping.
            self.assertEqual(tracked_run_scratch_files(directory), [])


if __name__ == "__main__":
    unittest.main()
