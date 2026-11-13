"""Shared scaffold for the `_uninstall` diagnostic suites' config-home cases.

Every diagnostic suite pins the same resolution of the config home the
recipes' scanners read from: with `XDG_CONFIG_HOME` unset -- or set to a
relative path, which the same fallback must beat -- they read
`$HOME/.config`, and with neither an absolute `XDG_CONFIG_HOME` nor an
absolute `HOME` nothing is checked. Ten suites pin that with the same
three-case shape; the file staged under the fallback home and the wording
asserted after the run vary per suite, so they arrive as callables from the
caller.

Callers: the ten `_uninstall` diagnostic suites (test_cursor,
test_kdedefaults, test_kdedefaults_mirror, test_kdeglobals,
test_kdeglobals_fonts, test_kwinrc, test_kwinrc_aurorae,
test_kwinrc_decoration, test_lnf and test_plasmarc), each its three
fallback shapes, plus test_kvantum_selection_make's unset fallback. Left in
their own modules on purpose: test_colorscheme_install's same three shapes
(additional assertion: runs rooted at a destdir the packaged scheme is
installed into), and test_theme_install's environment-level pin of
`make_env` itself. Within the callers, the share-one-run tests' richer
staging keeps its own shape.
"""

import os

from support import theme_install
from support.process_assertions import assert_succeeded
from support.tmp_dir import make_tmp_dir


def make_fallback_env(base, *, relative=False):
    """Return (config, env) where env resolves the config home to the fallback.

    The environment drops `XDG_CONFIG_HOME` and sets `HOME` to
    *base*`/home`, so the recipe reads *base*`/home/.config`; with *relative*
    it also sets `XDG_CONFIG_HOME` to a relative path, which must lose to the
    same fallback.
    """
    home = os.path.join(str(base), "home")
    env = theme_install.make_env("XDG_CONFIG_HOME")
    env["HOME"] = home
    if relative:
        env["XDG_CONFIG_HOME"] = "relative/config"
    return os.path.join(home, ".config"), env


def assert_home_fallback(case, stage, rule, *, relative=False):
    """Stage a still-selected file under the `$HOME/.config` fallback and pin
    the diagnostic naming it.

    `stage(config)` writes the suite's still-selected file into the fallback
    config directory under a fresh scratch `HOME` and returns its path;
    `rule(path)` builds the expected one-line diagnostic. The `make
    _uninstall` run -- rooted at its own fresh `DESTDIR` like every other
    fallback case -- must succeed, must leave the staged file's bytes
    untouched, and its stderr must carry the line. Returns (path, result) for
    the case's extra pins.
    """
    config, env = make_fallback_env(str(make_tmp_dir(case)), relative=relative)
    path = stage(config)
    staged = theme_install.read_bytes(path)
    result = theme_install.uninstall_recipe(
        str(make_tmp_dir(case)), extra=(), env=env
    )
    assert_succeeded(case, result)
    case.assertEqual(staged, theme_install.read_bytes(path))
    case.assertIn(rule(path), result.stderr)
    return path, result


def assert_no_config_home(case, *absent):
    """Run `make _uninstall` with neither config-home variable resolvable.

    With neither an absolute `XDG_CONFIG_HOME` nor an absolute `HOME` there
    is no config home to read, so the diagnostics must be skipped: the run
    succeeds and must not mention any of *absent*. Returns the result for the
    case's extra pins (a suite that must stay silent about a list it builds,
    such as the six font keys, loops over the returned result instead).
    """
    env = theme_install.make_env("XDG_CONFIG_HOME", "HOME")
    result = theme_install.uninstall_recipe(
        str(make_tmp_dir(case)), extra=(), env=env
    )
    assert_succeeded(case, result)
    for marker in absent:
        case.assertNotIn(marker, result.stderr)
    return result
