"""`make install`/`uninstall` data-home resolution and the `FLOCK_TIMEOUT` guard.

An empty or relative `XDG_DATA_HOME` falls back to the XDG default
(`$HOME/.local/share`), and an unset or relative `HOME` with no absolute data
home is refused. A `FLOCK_TIMEOUT` that is not a valid timeout is refused
before the data home is created. Install paths, symlink guards and
`INSTALL_PACKAGES` stay in ``test_theme_install.py``.
"""

import os
import unittest

from support import installed_paths, theme_install
from support.process_assertions import assert_failed, assert_succeeded
from support.tmp_dir import make_tmp_dir



class TestXdgDataHomeDefault(unittest.TestCase):
    """An empty or relative $XDG_DATA_HOME must fall back to the XDG default.

    The XDG Base Directory spec resolves $XDG_DATA_HOME to $HOME/.local/share
    when it is unset or empty, and treats a relative value as invalid and
    ignores it; README's Installing section documents the same default. `?=`
    alone kept an empty environment value, so `make install` targeted
    $(DESTDIR) itself (or, with no DESTDIR, ran `install -d ""`). Drive
    `make -n` with a controlled environment and read the data-home path the
    recipe would use.
    """

    HOME = "/tmp/tumwater-test-home"

    def _install_dry_run(self, xdg):
        """Return the `make -n install` output for *xdg* in the environment."""
        env = dict(os.environ, HOME=self.HOME, XDG_DATA_HOME=xdg)
        result = theme_install.run_make(["-n", "install"], env=env)
        assert_succeeded(self, result)
        return result.stdout

    def test_empty_falls_back_to_the_xdg_default(self):
        out = self._install_dry_run("")
        self.assertIn(f'install -d "{self.HOME}/.local/share"', out)

    def test_relative_falls_back_to_the_xdg_default(self):
        out = self._install_dry_run("relative/share")
        self.assertIn(f'install -d "{self.HOME}/.local/share"', out)
        self.assertNotIn("relative/share", out)

    def test_absolute_is_kept(self):
        out = self._install_dry_run("/custom/share")
        self.assertIn('install -d "/custom/share"', out)

    def test_unset_home_without_an_absolute_data_home_is_refused(self):
        # The fallback is $HOME/.local/share, so with HOME unset it becomes
        # /.local/share at the filesystem root. Both targets must refuse
        # rather than write there or delete from it. XDG_DATA_HOME is dropped
        # from the environment (not passed on the command line), so the
        # fallback -- and the guard -- actually run.
        env = dict(os.environ)
        env.pop("HOME", None)
        env.pop("XDG_DATA_HOME", None)
        theme_install.assert_both_targets_refused(self, env, (), ("HOME is unset",))

    def test_relative_home_without_an_absolute_data_home_is_refused(self):
        # A relative HOME makes the fallback a relative path, so `install -d`
        # would create a tree under the current directory (and `uninstall`
        # delete from it). DESTDIR is rooted at a temp dir so a guard that
        # wrongly let the run through cannot write into the checkout; the
        # guard reads HOME, not DESTDIR, so the refusal still exercises the
        # relative-HOME branch.
        env = dict(os.environ, HOME="relative")
        env.pop("XDG_DATA_HOME", None)
        tmp = make_tmp_dir(self)
        theme_install.assert_both_targets_refused(
            self,
            env,
            (f"DESTDIR={tmp}",),
            (
                "HOME is not an absolute path",
                # The guard names the offending HOME so a contributor can
                # see which value it read, not just that one was bad.
                "('relative')",
            ),
        )

    def test_guard_names_the_relative_data_home_it_refused(self):
        # XDG_DATA_HOME_ENV is exported so the guard can name the raw value
        # the caller gave; without the export the recipe shell sees no such
        # variable and the diagnostic shows an empty ('') value instead.
        env = dict(os.environ, HOME="relative", XDG_DATA_HOME="relative/share")
        env.pop("XDG_DATA_HOME_ENV", None)
        tmp = make_tmp_dir(self)
        result = theme_install.run_make(["install", f"DESTDIR={tmp}"], env=env)
        assert_failed(self, result)
        self.assertIn(
            "XDG_DATA_HOME is not an absolute path ('relative/share')",
            result.stderr,
        )


class TestFlockTimeout(unittest.TestCase):
    """An invalid FLOCK_TIMEOUT must be refused before the lock is taken.

    FLOCK_TIMEOUT is a make variable a caller can set, but `flock -w` accepts
    only a non-negative integer number of seconds that fits its 64-bit signed
    timer. An empty, non-numeric, or too-large value otherwise reaches flock,
    which fails with its own "invalid timeout value" or "cannot set up timer"
    message that does not name the variable -- after `install` has already
    created the data home. The guard must name FLOCK_TIMEOUT and leave the
    tree untouched. `install` and `uninstall` share the guard.

    The guard must also accept every value flock accepts: leading zeros are
    characters, not magnitude, so a small value written with them must not be
    refused as too large.
    """

    def _assert_refused(self, value, extra=None):
        expected = [
            "FLOCK_TIMEOUT must be a non-negative integer number of seconds",
            f"'{value}'",
        ]
        if extra is not None:
            expected.append(extra)
        tmp = make_tmp_dir(self)
        theme_install.assert_both_targets_refused(
            self,
            None,
            (
                f"DESTDIR={tmp}",
                f"XDG_DATA_HOME={installed_paths.XDG_DATA_HOME}",
                f"FLOCK_TIMEOUT={value}",
            ),
            expected,
        )
        data_home = os.path.join(tmp, installed_paths.XDG_DATA_HOME.lstrip("/"))
        self.assertFalse(os.path.exists(data_home), data_home)

    def test_empty_is_refused_before_creating_the_data_home(self):
        self._assert_refused("")

    def test_non_numeric_is_refused_before_creating_the_data_home(self):
        self._assert_refused("60s")

    def test_above_the_timer_limit_is_refused_before_creating_the_data_home(self):
        # `flock -w` stores the timeout in a signed 64-bit timer field, so a
        # value above 2**63 - 1 reaches it and fails with its own "cannot set
        # up timer: Invalid argument" after the data home exists. The guard
        # must reject it and name the limit.
        self._assert_refused(
            "9223372036854775808",
            "at most 9223372036854775807",
        )

    def test_a_value_longer_than_the_timer_limit_is_refused_by_length(self):
        # After leading zeros are stripped, a value of more than 19 digits
        # cannot fit flock's signed 64-bit timer whatever its digits, so the
        # guard refuses it by length before comparing the digits. Without that
        # length clause a 20-digit value slips past the 19-digit comparison,
        # reaches flock, and fails with flock's own message after the data
        # home exists.
        self._assert_refused(
            "99999999999999999999",
            "at most 9223372036854775807",
        )

    def test_leading_zeros_do_not_make_a_small_value_look_too_large(self):
        # A valid value written with leading zeros ("000...0001") has more
        # than 19 characters but a value of 1. The length check must strip the
        # zeros before calling it too large; flock parses the value as 1
        # second, so the install must proceed and install the scheme.
        tmp = str(make_tmp_dir(self))
        result = theme_install.install(
            tmp,
            extra=["FLOCK_TIMEOUT=00000000000000000001"],
            packages="color-scheme",
        )
        assert_succeeded(self, result)
        scheme = installed_paths.installed_color_scheme(tmp)
        self.assertTrue(os.path.isfile(scheme), result.stderr)

    def test_install_d_failure_is_not_blamed_on_the_lock(self):
        # The guards, `install -d` and the locked sub-make share one recipe
        # shell in both `install` and `uninstall`. An `install -d` failure with
        # flock's conflict status (75) must not print the lock-wait diagnostic:
        # only flock's own failure means the data-home lock was busy. Both
        # targets are driven because a missing or misplaced brace on either
        # recipe line would reintroduce the misleading message.
        for target in ("install", "uninstall"):
            with self.subTest(target=target):
                tmp = make_tmp_dir(self)
                env = theme_install.shadow_command_env(
                    tmp, "install", "#!/bin/sh\nexit 75\n"
                )
                result = theme_install.run_make(
                    [
                        target,
                        f"DESTDIR={tmp}",
                        f"XDG_DATA_HOME={installed_paths.XDG_DATA_HOME}",
                    ],
                    env=env,
                )
                assert_failed(self, result)
                self.assertNotIn("gave up after", result.stderr)
                self.assertNotIn(
                    "another install or uninstall holds it", result.stderr
                )


if __name__ == "__main__":
    unittest.main()
