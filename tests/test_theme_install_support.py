"""Pins the shared install test helpers.

``assert_uninstall_diagnostics``, ``assert_files_identical`` and
``copy_shipped_file`` are the helpers in ``support/theme_install.py`` that the
install suites route through. ``installed_destdir`` in the same module and
``FailedInstallPreservesPackage._install_ok`` in
``support/install_failure_cases.py`` are the shared template copies. The pins
for those two check that each helper installs once per class and copies the
template per test, and that a symlink in the template is refused or kept as a
link. The ``make``-level behaviour they serve (what ``make install`` and
``uninstall`` do) stays in ``test_theme_install.py``.
"""

import contextlib
import os
import tempfile
import unittest
import unittest.mock
from pathlib import Path

from support import install_failure_cases, repo_root, theme_install
from support.install_failure_cases import FailedInstallPreservesPackage
from support.symlink_fixtures import symlinked_repo
from support.tmp_dir import make_tmp_dir


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


class TestInstalledDestdirSharing(unittest.TestCase):
    """`installed_destdir` installs once per class and copies that tree."""

    def setUp(self):
        # The helper caches on the test class; each test here starts a new
        # class-level cache so one test's install cannot satisfy another.
        self.addCleanup(self._forget_templates)
        self._forget_templates()

    def _forget_templates(self):
        if "_installed_templates" in type(self).__dict__:
            delattr(type(self), "_installed_templates")

    @staticmethod
    def _fake_install(calls, results):
        def install(destdir, **kwargs):
            calls.append(kwargs)
            if not results:
                raise AssertionError("install called more often than expected")
            result = results.pop(0)
            if result.returncode == 0:
                (Path(destdir) / "marker").write_text(
                    "installed", encoding="utf-8"
                )
            return result

        return install

    def _succeeded(self):
        return unittest.mock.Mock(returncode=0, stdout="", stderr="")

    def test_repeated_calls_install_once_and_copy_the_tree(self):
        calls = []
        with unittest.mock.patch.object(
            theme_install, "install", self._fake_install(calls, [self._succeeded()])
        ):
            with theme_install.installed_destdir(
                self, packages="color-scheme"
            ) as first:
                self.assertEqual(
                    "installed",
                    (Path(first) / "marker").read_text(encoding="utf-8"),
                )
            with theme_install.installed_destdir(
                self, packages="color-scheme"
            ) as second:
                self.assertEqual(
                    "installed",
                    (Path(second) / "marker").read_text(encoding="utf-8"),
                )
        self.assertEqual([{"packages": "color-scheme"}], calls)
        self.assertNotEqual(first, second)

    def test_each_package_family_gets_its_own_template(self):
        calls = []
        results = [self._succeeded(), self._succeeded()]
        with unittest.mock.patch.object(
            theme_install, "install", self._fake_install(calls, results)
        ):
            with theme_install.installed_destdir(
                self, packages="color-scheme"
            ):
                pass
            with theme_install.installed_destdir(self, packages="kvantum"):
                pass
        self.assertEqual(
            [{"packages": "color-scheme"}, {"packages": "kvantum"}], calls
        )

    def test_a_failed_install_is_not_reused(self):
        calls = []
        failed = unittest.mock.Mock(
            returncode=1, stdout="", stderr="template install failed"
        )
        results = [failed, self._succeeded()]
        with unittest.mock.patch.object(
            theme_install, "install", self._fake_install(calls, results)
        ):
            with self.assertRaises(AssertionError):
                with theme_install.installed_destdir(
                    self, packages="color-scheme"
                ):
                    pass
            with theme_install.installed_destdir(
                self, packages="color-scheme"
            ) as destdir:
                self.assertTrue((Path(destdir) / "marker").is_file())
        self.assertEqual(2, len(calls))

    def test_an_escaping_template_symlink_is_refused(self):
        # The template comes from `make install`, whose `cp -r` preserves a
        # package symlink. Copying it with `copytree`'s default dereferences
        # the link into the test's DESTDIR, so a private file's bytes enter
        # the test tree; the copy must refuse the escape before it starts.
        private = make_tmp_dir(self) / "private"
        private.write_text("private secret line\n", encoding="utf-8")
        dest = make_tmp_dir(self) / "dest"
        dest.mkdir()

        def fake_install(destdir, **kwargs):
            (Path(destdir) / "leak").symlink_to(private)
            return self._succeeded()

        with (
            unittest.mock.patch.object(theme_install, "install", fake_install),
            unittest.mock.patch.object(
                theme_install.tempfile,
                "TemporaryDirectory",
                lambda *args, **kwargs: contextlib.nullcontext(str(dest)),
            ),
        ):
            with self.assertRaises(ValueError) as caught:
                with theme_install.installed_destdir(
                    self, packages="color-scheme"
                ):
                    pass
        self.assertIn("resolves outside", str(caught.exception))
        self.assertNotIn("private secret line", str(caught.exception))
        self.assertEqual(
            "private secret line\n", private.read_text(encoding="utf-8")
        )
        self.assertEqual([], list(dest.iterdir()))

    def test_a_contained_template_symlink_is_copied_as_a_link(self):
        # `make install`'s `cp -r` also preserves a link whose target stays
        # inside the package; the copy must keep it a link rather than
        # dereferencing it into a second copy.
        def fake_install(destdir, **kwargs):
            target = Path(destdir) / "target"
            target.write_text("kept\n", encoding="utf-8")
            (Path(destdir) / "inside-link").symlink_to("target")
            return self._succeeded()

        with unittest.mock.patch.object(
            theme_install, "install", fake_install
        ):
            with theme_install.installed_destdir(
                self, packages="color-scheme"
            ) as destdir:
                link = Path(destdir) / "inside-link"
                self.assertTrue(link.is_symlink())
                self.assertEqual("target", os.readlink(link))


class TestFailedInstallSharing(unittest.TestCase):
    """`FailedInstallPreservesPackage` installs once per class and copies."""

    def test_install_ok_installs_once_and_copies_per_test(self):
        calls = []

        def fake_install(destdir, **kwargs):
            calls.append(kwargs)
            (Path(destdir) / "marker").write_text(
                "installed", encoding="utf-8"
            )
            return unittest.mock.Mock(returncode=0, stdout="", stderr="")

        class Case(FailedInstallPreservesPackage, unittest.TestCase):
            MAKE_PACKAGES = "color-scheme"

            def runTest(self):
                pass

            def _snapshot(self, tmp):
                return (str(tmp), "metadata", "good")

        case = Case()
        self.addCleanup(case.doCleanups)
        self.addCleanup(Case.doClassCleanups)
        with unittest.mock.patch.object(
            theme_install, "install", fake_install
        ):
            first = case._install_ok()
            second = case._install_ok()

        self.assertEqual([{"packages": "color-scheme"}], calls)
        self.assertNotEqual(first[0], second[0])
        for result in (first, second):
            self.assertTrue((Path(result[0]) / "marker").is_file())

    def test_install_ok_refuses_an_escaping_template_symlink(self):
        private = make_tmp_dir(self) / "private"
        private.write_text("private secret line\n", encoding="utf-8")
        copy_dir = make_tmp_dir(self) / "copy"
        copy_dir.mkdir()

        def fake_install(destdir, **kwargs):
            (Path(destdir) / "leak").symlink_to(private)
            return unittest.mock.Mock(returncode=0, stdout="", stderr="")

        class Case(FailedInstallPreservesPackage, unittest.TestCase):
            MAKE_PACKAGES = "color-scheme"

            def runTest(self):
                pass

        case = Case()
        self.addCleanup(case.doCleanups)
        self.addCleanup(Case.doClassCleanups)
        with unittest.mock.patch.object(
            install_failure_cases, "make_tmp_dir", lambda case: copy_dir
        ):
            with unittest.mock.patch.object(
                theme_install, "install", fake_install
            ):
                with self.assertRaises(ValueError) as caught:
                    case._install_ok()
        self.assertIn("resolves outside", str(caught.exception))
        self.assertNotIn("private secret line", str(caught.exception))
        self.assertEqual(
            "private secret line\n", private.read_text(encoding="utf-8")
        )
        self.assertEqual([], list(copy_dir.iterdir()))


if __name__ == "__main__":
    unittest.main()
