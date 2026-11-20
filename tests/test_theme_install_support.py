"""Pins the shared install test helpers in ``support/theme_install.py``.

``assert_uninstall_diagnostics``, ``assert_files_identical`` and
``copy_shipped_file`` are the helpers the install suites route through. The
``make``-level behaviour they serve (what ``make install`` and ``uninstall`` do)
stays in ``test_theme_install.py``.
"""

import os
import tempfile
import unittest
import unittest.mock
from pathlib import Path

from support import repo_root, theme_install
from support.symlink_fixtures import symlinked_repo


class _FakeResult:
    """The slice of a CompletedProcess the diagnostics pin helper reads."""

    def __init__(self, returncode=0, stderr=""):
        self.returncode = returncode
        self.stdout = ""
        self.stderr = stderr


class TestAssertUninstallDiagnostics(unittest.TestCase):
    """The shared recipe pin runs once and pins printed, absent, unchanged.

    The per-surface `_uninstall` diagnostic suites route their one-line
    stderr rule assertions through `assert_uninstall_diagnostics`; the pin
    must read an *unchanged* path before the recipe runs, so a run that
    edits the scanned file fails instead of comparing the edited bytes with
    themselves.
    """

    RULE = "uninstall: the selection still names ours after removal"
    FOREIGN = "uninstall: the other diagnostic's line"

    def _bind_recipe(self, result, edit=None):
        """Point this case's `uninstall_with_config` at *result*; return the calls."""
        calls = []

        def uninstall_with_config(tmp, config):
            calls.append((tmp, config))
            if edit is not None:
                edit()
            return result

        self.uninstall_with_config = uninstall_with_config
        return calls

    def test_runs_the_recipe_once_and_pins_printed_and_absent_rules(self):
        result = _FakeResult(stderr=self.RULE + "\n")
        calls = self._bind_recipe(result)
        returned = theme_install.assert_uninstall_diagnostics(
            self, "tmp", "config", self.RULE, absent=self.FOREIGN
        )
        self.assertEqual(calls, [("tmp", "config")])
        self.assertIs(returned, result)

    def test_an_editing_recipe_run_fails_the_unchanged_pin(self):
        # The pre-run read is what makes this fail: a helper that read the
        # file only after the run would compare the edited bytes with
        # themselves and let an editing diagnostic through.
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "plasmarc")
            with open(path, "wb") as handle:
                handle.write(b"before")

            def edit():
                with open(path, "wb") as handle:
                    handle.write(b"after")

            self._bind_recipe(_FakeResult(stderr=self.RULE), edit)
            with self.assertRaises(AssertionError):
                theme_install.assert_uninstall_diagnostics(
                    self, tmp, tmp, self.RULE, unchanged=path
                )
            with open(path, "rb") as handle:
                self.assertEqual(handle.read(), b"after")

    def test_an_untouched_recipe_run_passes_the_unchanged_pin(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "plasmarc")
            with open(path, "wb") as handle:
                handle.write(b"same")
            self._bind_recipe(_FakeResult(stderr=self.RULE))
            theme_install.assert_uninstall_diagnostics(
                self, tmp, tmp, self.RULE, unchanged=path
            )


class TestAssertFilesIdentical(unittest.TestCase):
    """The install byte-comparison must refuse a source symlink that escapes.

    ``assert_files_identical`` reads a contributor-supplied package file and
    compares it with the installed copy; ``assertEqual`` echoes both byte
    strings on a mismatch, so a checked-in symlink at the source that resolves
    outside the repository must be refused before it is opened. The copy in the
    throwaway DESTDIR is not contributor-supplied and is read as before.
    """

    def test_rejects_a_source_symlink_that_escapes_the_repository(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            root, source = symlinked_repo(
                tmp, "theme/icons/icon.svg", b"PRIVATE-SECRET-BYTES"
            )
            target = tmp / "installed.svg"
            target.write_bytes(b"a different installed copy")
            with unittest.mock.patch.object(repo_root, "ROOT", root):
                with self.assertRaises(ValueError) as caught:
                    theme_install.assert_files_identical(self, source, target)
        self.assertIn(str(source), str(caught.exception))
        self.assertNotIn("PRIVATE-SECRET-BYTES", str(caught.exception))

    def test_reads_a_source_symlink_that_stays_within_the_repository(self):
        # The guard must refuse only escapes, not a legitimate package file
        # reached through a symlink inside the repository.
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            root, source = symlinked_repo(
                tmp,
                "theme/icons/alias.svg",
                b"same bytes",
                target="theme/icons/icon.svg",
            )
            target = tmp / "installed.svg"
            target.write_bytes(b"same bytes")
            with unittest.mock.patch.object(repo_root, "ROOT", root):
                theme_install.assert_files_identical(self, source, target)


class TestCopyShippedFile(unittest.TestCase):
    """A copy of a package file must not follow a symlink out of the repository.

    The install tests copy a checked-in file such as the color scheme to a
    throwaway directory before installing it. ``shutil.copy`` follows a
    checked-in symlink at the source, so it would copy a private file's bytes
    into the test tree or stream a device without bound; the helper reads
    through the shared containment guard instead and writes nothing on a
    refusal.
    """

    def test_rejects_a_source_symlink_that_escapes_the_repository(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            root, source = symlinked_repo(
                tmp, "theme/color-schemes/MacOS8.colors", b"PRIVATE-SECRET-BYTES"
            )
            dest = tmp / "copied.colors"
            with unittest.mock.patch.object(repo_root, "ROOT", root):
                with self.assertRaises(ValueError) as caught:
                    theme_install.copy_shipped_file(source, dest)
            self.assertIn(str(source), str(caught.exception))
            self.assertNotIn("PRIVATE-SECRET-BYTES", str(caught.exception))
            self.assertFalse(dest.exists())

    def test_copies_a_source_symlink_that_stays_within_the_repository(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            root, source = symlinked_repo(
                tmp,
                "alias.colors",
                b"same bytes",
                target="theme/color-schemes/MacOS8.colors",
            )
            dest = tmp / "copied.colors"
            with unittest.mock.patch.object(repo_root, "ROOT", root):
                theme_install.copy_shipped_file(source, dest)
            self.assertEqual(dest.read_bytes(), b"same bytes")


if __name__ == "__main__":
    unittest.main()
