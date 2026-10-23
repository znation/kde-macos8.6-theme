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


if __name__ == "__main__":
    unittest.main()


class TestPublishFdopen(unittest.TestCase):
    def test_failed_fdopen_closes_descriptor(self):
        import tempfile
        directory = tempfile.mkdtemp(prefix="render-output-fdopen-")
        root = Path(directory)
        source = root / "src.png"
        source.write_bytes(b"source")
        output = root / "out.png"
        real_close = os.close
        closed = []
        def track_close(fd):
            closed.append(fd)
            return real_close(fd)
        def boom(*args, **kwargs):
            raise OSError("simulated fdopen failure")
        real_fdopen = os.fdopen
        os.close = track_close
        os.fdopen = boom
        try:
            with self.assertRaises(OSError):
                render_output.publish(source, output)
        finally:
            os.close = real_close
            os.fdopen = real_fdopen
        self.assertEqual(1, len(closed))
