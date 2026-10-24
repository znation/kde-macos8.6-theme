"""Shared Makefile checks for an opt-in apply/remove target pair.

The GTK and cursor suites each drive a public `make` target that installs a
package and then runs a tool, plus its `--remove` counterpart. Both targets
share one Makefile shape: the dry run installs the package before the tool
runs, a non-empty `DESTDIR` is refused, an unusable `PYTHON` is refused, the
remove target passes `--remove`, and `make help` lists both targets. The
checks live here once; a suite subclasses the mixin and names its target.

It is a plain mixin, not a `TestCase`, so importing it does not collect an
unconfigured base.
"""

from __future__ import annotations

import os
import shutil
import tempfile

from support.process_assertions import assert_failed, assert_succeeded
from support.theme_install import make_env, run_make
from support.tmp_dir import make_tmp_dir


class ApplyTargetMakeCases:
    """Mixin: the Makefile target checks shared by an apply/remove pair.

    Subclasses set `TARGET` (`apply-gtk`), `REMOVE_TARGET` (`remove-gtk`),
    `INSTALL_PACKAGES` (the `INSTALL_PACKAGES=` value the apply target passes
    to install) and `SCRIPT` (the tool path the target runs).
    """

    TARGET = None
    REMOVE_TARGET = None
    INSTALL_PACKAGES = None
    SCRIPT = None

    def test_dry_run_shows_install_before_the_script(self):
        result = run_make(
            ["-n", self.TARGET], env=make_env("XDG_DATA_HOME")
        )
        assert_succeeded(self, result)
        install = f"INSTALL_PACKAGES={self.INSTALL_PACKAGES}"
        self.assertIn(install, result.stdout)
        self.assertIn(self.SCRIPT, result.stdout)
        self.assertLess(
            result.stdout.index(install), result.stdout.index(self.SCRIPT)
        )

    def test_non_empty_destdir_is_refused(self):
        destdir = tempfile.mkdtemp(prefix=f"{self.TARGET}-destdir-")
        self.addCleanup(shutil.rmtree, destdir, ignore_errors=True)
        result = run_make(
            [self.TARGET, f"DESTDIR={destdir}"], env=make_env()
        )
        assert_failed(self, result)
        self.assertIn("DESTDIR must be empty", result.stderr)
        self.assertNotIn(
            os.path.basename(self.SCRIPT), result.stdout + result.stderr
        )

    def test_python_version_is_refused(self):
        tmp = make_tmp_dir(self)
        fake = tmp / "python"
        fake.write_text("#!/bin/sh\nexit 3\n", encoding="utf-8")
        fake.chmod(0o755)
        result = run_make(
            [self.TARGET, f"PYTHON={fake}"], env=make_env("PYTHON")
        )
        assert_failed(self, result)
        self.assertIn("Python 3.10 or newer", result.stderr)
        self.assertIn(str(fake), result.stderr)

    def test_dry_run_shows_remove_script(self):
        result = run_make(["-n", self.REMOVE_TARGET], env=make_env())
        assert_succeeded(self, result)
        self.assertIn(f"{self.SCRIPT} --remove", result.stdout)

    def test_help_lists_both_targets(self):
        result = run_make(["help"], env=make_env())
        assert_succeeded(self, result)
        lines = result.stdout.splitlines()
        for target in (self.TARGET, self.REMOVE_TARGET):
            with self.subTest(target=target):
                self.assertTrue(
                    any(line.startswith(f"  {target} ") for line in lines),
                    result.stdout,
                )
