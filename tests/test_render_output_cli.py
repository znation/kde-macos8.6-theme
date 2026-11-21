"""The render CLI's output-path contract, against shell stubs of the external tools.

``tools/render_surface.py`` publishes its output path: it refuses an unusable
output before installing anything, copies a capture over the output, keeps the
previous output whole when a copy fails or a capture source is refused, leaves
no hidden leftovers, and passes a dash-leading ``RENDER_OUTPUT`` through
``make render`` as a path. These cases run against the same stub executables as
``tests/test_render_failure_paths.py``, which keeps the session failure paths;
the publication unit tests live in ``tests/test_render_output.py``.
"""

from __future__ import annotations

import errno
import os
import shutil
import subprocess
import unittest
from pathlib import Path
from unittest import mock

from support import repo_root
from support.cli_fixtures import call_main
from tools import render_surface, render_workflow
from support.render.stub_tools import StubTools


class TestRenderOutputCli(StubTools, unittest.TestCase):

    def test_unwritable_output_is_refused_before_installing(self):
        marker = self.root / "make-ran"
        self.stub("make", f"touch {marker}")
        for label, output in (
            ("a directory", self.root),
            ("an empty path", Path("")),
            ("a missing directory", self.root / "missing" / "out.png"),
        ):
            with self.subTest(label):
                status, stderr = call_main(render_surface.main, str(output))
                self.assertEqual(2, status)
                self.assertIn("render_surface: error: cannot write", stderr)
                self.assertFalse(marker.exists())
                self.assert_scratch_removed()

    def test_a_read_only_output_directory_is_refused_before_installing(self):
        # The last branch of `tools/render_output.py`'s `output_problem`: the
        # directory exists but this
        # user may not write it. `os.access` is the only check that sees that,
        # and a refusal here keeps the failure a named diagnostic instead of
        # letting the copy fail later with an errno the operator has to read
        # out of a traceback.
        marker = self.root / "make-ran"
        self.stub("make", f"touch {marker}")
        locked = self.root / "locked"
        locked.mkdir()
        locked.chmod(0o500)
        self.addCleanup(locked.chmod, 0o700)
        if os.access(locked, os.W_OK):
            self.skipTest("directory permissions are not enforced for this user")
        status, stderr = call_main(render_surface.main, str(locked / "out.png"))
        self.assertEqual(2, status)
        self.assertIn("render_surface: error: cannot write", stderr)
        self.assertIn("its directory is not writable", stderr)
        self.assertFalse(marker.exists())
        self.assert_scratch_removed()

    def test_a_capture_is_copied_to_the_output(self):
        fixture = self.stub_capture()
        status, stderr, output = self.run_main()
        self.assertEqual((0, ""), (status, stderr))
        self.assertEqual(fixture.read_bytes(), output.read_bytes())
        self.assertEqual([], self.hidden_files())

    def test_a_failed_copy_keeps_the_previous_output_and_leaves_no_partial_file(self):
        self.stub_capture()
        output = self.root / "out.png"
        output.write_bytes(b"previous good render")

        def die_midway(src, dst):
            dst.write(b"half a PNG")
            raise OSError(errno.ENOSPC, "No space left on device")

        with mock.patch.object(shutil, "copyfileobj", die_midway):
            status, stderr = call_main(render_surface.main, str(output))
        self.assertEqual(1, status)
        self.assertIn("cannot write", stderr)
        self.assertNotIn("Traceback", stderr)
        self.assertEqual(b"previous good render", output.read_bytes())
        self.assertEqual([], self.hidden_files())
        self.assert_scratch_removed()

    def test_a_fifo_refusal_is_reported_as_a_failed_render(self):
        # The open guard refuses a non-regular capture source with ValueError,
        # not OSError; the CLI must still report it as a failed render with
        # its own diagnostic instead of tracebacking out of the exit contract.
        self.stub_capture()
        output = self.root / "out.png"
        output.write_bytes(b"previous good render")

        with mock.patch.object(
            render_workflow,
            "publish",
            side_effect=ValueError(
                f"{self.root / 'surface.png'} cannot be read: "
                "not a regular file; refusing to open it"
            ),
        ):
            status, stderr = call_main(render_surface.main, str(output))
        self.assertEqual(1, status)
        self.assertIn("cannot write", stderr)
        self.assertIn("not a regular file", stderr)
        self.assertNotIn("Traceback", stderr)
        self.assertEqual(b"previous good render", output.read_bytes())
        self.assertEqual([], self.hidden_files())
        self.assert_scratch_removed()

    def test_make_render_passes_a_dash_leading_output_as_a_path(self):
        real_path = os.pathsep.join(
            entry
            for entry in os.environ["PATH"].split(os.pathsep)
            if entry != str(self.bin)
        )
        result = subprocess.run(
            ["make", "-n", "render", "RENDER_OUTPUT=-x.png"],
            cwd=repo_root.ROOT,
            env={**os.environ, "PATH": real_path},
            capture_output=True,
            text=True,
            timeout=60,
        )
        self.assertIn('render_surface.py "$@" -- "-x.png"', result.stdout)


if __name__ == "__main__":
    unittest.main()
