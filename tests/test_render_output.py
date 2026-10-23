"""Tests for tools/render_output.py's atomic output publication.

``publish`` must not write through a symlink planted at a guessable temporary
name, and must leave the output with the mode a plain copy would.
"""

from __future__ import annotations

import os
import stat
import tempfile
import unittest
from pathlib import Path

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.close_tracking import failing_fdopen  # noqa: E402
from tools import render_output  # noqa: E402


class TestPublish(unittest.TestCase):
    """`publish` must not write through a symlink planted at a guessable name."""

    def test_a_planted_symlink_does_not_redirect_the_copy(self):
        with tempfile.TemporaryDirectory(prefix="render-publish-") as directory:
            root = Path(directory)
            source = root / "source.png"
            source.write_bytes(b"the new render")
            victim = root / "victim.txt"
            victim.write_bytes(b"do not overwrite")
            output = root / "render.png"
            # The fixed temporary name the tool used to build; a local user who
            # can write the output directory can create it before the copy.
            planted = output.with_name(f".render-{os.getpid()}.tmp")
            planted.symlink_to(victim)

            render_output.publish(source, output)

            self.assertEqual(b"do not overwrite", victim.read_bytes())
            self.assertEqual(b"the new render", output.read_bytes())


class TestPublishMode(unittest.TestCase):
    """`publish` gives the output the mode a plain copy would.

    ``mkstemp`` opens the temporary file 0600, while a plain
    ``open(..., "wb")`` creates the output with the process umask applied; the
    copy must restore that mode before the rename or the published render is
    left owner-only.
    """

    def test_output_mode_matches_the_process_umask(self):
        with tempfile.TemporaryDirectory(prefix="render-publish-") as directory:
            root = Path(directory)
            source = root / "source.png"
            source.write_bytes(b"the new render")
            output = root / "render.png"
            previous = os.umask(0o027)
            self.addCleanup(os.umask, previous)

            render_output.publish(source, output)

            self.assertEqual(b"the new render", output.read_bytes())
            self.assertEqual(0o640, stat.S_IMODE(output.stat().st_mode))


class TestPublishFdopen(unittest.TestCase):
    def test_failed_fdopen_closes_descriptor(self):
        import tempfile
        directory = tempfile.mkdtemp(prefix="render-output-fdopen-")
        root = Path(directory)
        source = root / "src.png"
        source.write_bytes(b"source")
        output = root / "out.png"
        with failing_fdopen() as closed:
            with self.assertRaises(OSError):
                render_output.publish(source, output)
        self.assertEqual(1, len(closed))


class TestOutputProblem(unittest.TestCase):
    """`output_problem` names each reason the output path is unusable.

    The CLI test in ``tests/test_render_surface.py`` only asserts the generic
    ``cannot write`` prefix for the directory and missing-parent cases, so a
    refusal that lost its specific reason would still pass there.
    """

    def test_a_directory_output_is_named(self):
        with tempfile.TemporaryDirectory(prefix="render-problem-") as directory:
            self.assertEqual(
                "is a directory", render_output.output_problem(Path(directory))
            )

    def test_a_missing_parent_directory_is_named(self):
        with tempfile.TemporaryDirectory(prefix="render-problem-") as directory:
            output = Path(directory) / "missing" / "render.png"
            self.assertEqual(
                "its directory does not exist", render_output.output_problem(output)
            )

    def test_an_unwritable_parent_directory_is_named(self):
        with tempfile.TemporaryDirectory(prefix="render-problem-") as directory:
            locked = Path(directory) / "locked"
            locked.mkdir()
            locked.chmod(0o500)
            try:
                if os.access(locked, os.W_OK):
                    self.skipTest("directory permissions are not enforced for this user")
                self.assertEqual(
                    "its directory is not writable",
                    render_output.output_problem(locked / "render.png"),
                )
            finally:
                locked.chmod(0o700)

    def test_a_writable_output_has_no_problem(self):
        with tempfile.TemporaryDirectory(prefix="render-problem-") as directory:
            self.assertIsNone(
                render_output.output_problem(Path(directory) / "render.png")
            )


class TestOutputProblemTypeGuard(unittest.TestCase):
    def test_non_path_output_raises_naming_type(self):
        with self.assertRaisesRegex(
            ValueError,
            r"^output_problem\(\) requires a pathlib\.Path: output must be Path, "
            r"not int$",
        ):
            render_output.output_problem(42)


class TestPublishTypeGuards(unittest.TestCase):
    def test_non_path_source_raises_naming_type(self):
        with self.assertRaisesRegex(
            ValueError,
            r"^publish\(\) requires pathlib\.Path: source must be Path, not str$",
        ):
            render_output.publish("not-a-path", Path("/tmp/x"))

    def test_non_path_output_raises_naming_type(self):
        with self.assertRaisesRegex(
            ValueError,
            r"^publish\(\) requires pathlib\.Path: output must be Path, not int$",
        ):
            render_output.publish(Path("/tmp/x"), 42)


if __name__ == "__main__":
    unittest.main()
