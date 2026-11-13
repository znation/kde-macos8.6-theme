"""Run the repository's `make install` / `make uninstall` against a temp tree.

The installed artifacts land under `$(DESTDIR)$(XDG_DATA_HOME)`; the install
tests of each artifact family (color scheme, global theme, desktop theme,
Aurorae decoration, wallpaper, icon theme, Kvantum widget style, Lato font
package and GTK theme) pass a throwaway `DESTDIR` and inspect the result there, using
`support.installed_paths` where it names the layout.
Child processes go through `process_runner`, which applies the suite's timeout
and process-group cleanup. The repository root the commands run in, and the
boundary a contributor-supplied source file must stay within, come from
`support.repo_root`; the module also defines `run_captured` for tests that
need a captured child.
"""

import contextlib
import os
import shutil
import tempfile
import unittest

from support import containment
from support import process_runner
from support import repo_root
from support.installed_paths import XDG_DATA_HOME
from support.process_assertions import assert_failed, assert_succeeded


def run_captured(argv, **kwargs):
    """Run `argv` under `run`, capturing its output as decoded text.

    A caller that reads the child's `stdout`/`stderr` as `str` gets
    `capture_output` and `text` defaulted here; the rest (`cwd`, `env`,
    `timeout`) is forwarded to `process_runner.run`.
    """
    kwargs.setdefault("capture_output", True)
    kwargs.setdefault("text", True)
    return process_runner.run(argv, **kwargs)


def make_env(*names):
    """Return a copy of `os.environ` with *names* and `MAKEFLAGS` removed.

    A caller's `make VAR=...` reaches a child `make` both as a `VAR`
    environment variable and as a command-line variable definition inside
    `MAKEFLAGS`, and the child re-reads the latter; a test that pins a make
    variable must drop both so the ambient value does not win. *names* are the
    variables the test means to control (e.g. `CHECK_PATTERN`, `PYTHON`).
    """
    env = dict(os.environ)
    for name in (*names, "MAKEFLAGS"):
        env.pop(name, None)
    return env


def read_bytes(path):
    """Read *path* as bytes; the uninstall suites assert a file's exact contents."""
    with open(path, "rb") as handle:
        return handle.read()


def write_file(path, body):
    """Write *body* at *path*, creating its parent directory as needed.

    *body* may be ``str`` (encoded here as UTF-8) or ``bytes`` (written as
    is). This is the shared copy of the read-dirs-then-create-parent staging
    write: the recipe suites stage config-file contents under the test's
    config home with :func:`write_config_file`, the Firefox suites stage
    profile files through their local ``_write``/``write`` bindings, and the
    GTK user-CSS/uninstall suites stage user-file fixtures through it inline.

    Callers outside this module keep local names:
    test_install_firefox.py and test_firefox_profile.py bind ``_write`` as an
    import alias, ApplyGtkTestCase.write and test_gtk_install._write delegate
    their bodies here, and test_gtk_user_files.py's two ``css()`` helpers call
    it directly, test_invariants.py's ``_write``/``_register``,
    test_no_unused_imports.py's ``_write``, test_remove_kvantum.py's
    ``write`` and ApplyGtkTestCase.install_sheet delegate to it,
    support/kde_config.py's ``write`` (the ``kdeglobals`` seeder) fixes only
    its file name over it, and test_gtk_selection.py and
    test_placeholders.py stage their fixtures with direct ``write_file``
    calls. Deliberately left: ApplyGtkTestCase.write_bytes and the
    containment-refusal fixtures write raw bytes, not UTF-8 text,
    support/checker_scratch.py's ``_write`` adds containment and recording
    around its write, the kdedefaults suites' one-line direct ``write_file``
    call sites are already shared, not duplicated, test_invariants.py's
    ``test_cross_check_rejects_a_non_utf8_register`` writes and reads bytes
    that must not survive a UTF-8 decode, and
    tools/check_references_selftest.py stages inline in ``tools`` rather
    than importing test support. The mkdir-only fixtures that prepare a
    symlink or unreadable path (which write nothing) stay direct too.
    Still unconverted next-run material includes the further
    mkdir-then-write_text staging family in tests/test_gtk_staging.py,
    tests/test_apply_cursor.py, tests/test_apply_gtk_errors.py,
    tests/test_install_firefox.py (the ``user.js`` fixture),
    tests/test_firefox_profile.py, tests/test_local_hook.py
    (``write_fake_make``), tests/test_make_cursors.py, tests/test_svg_case.py,
    and support/symlink_fixtures.py's content staging; the same pair pattern
    also survives in, for example, tests/test_apply_theme.py,
    tests/test_sample_cli.py, tests/test_shipped_files.py,
    tests/test_suite_discovery.py, tests/test_checker_mutations.py,
    tests/test_render_surface_units.py,
    tests/test_check_references_validation.py, tests/test_apply_cursor_locks.py,
    and this module's own test_theme_install.py.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as handle:
        handle.write(body.encode("utf-8") if isinstance(body, str) else body)
    return path


def write_config_file(config, name, body):
    """Write *body* as `<config>`/name; return its path.

    The recipe suites stage one config file (`plasmarc`, `kdeglobals`,
    `kcminputrc`, `kwinrc`, `Kvantum/kvantum.kvconfig`, `settings.ini`, ...)
    under the test's config home before running a recipe; a *name* carrying
    further path segments is allowed. This is the one copy of that staging
    write, so the suites' local wrappers stay one-line bindings.
    """
    return write_file(os.path.join(config, name), body)


def run_make(args, env=None):
    """Run `make *args*` at the repository root under the suite's timeout runner.

    *args* is the target plus any variable assignments (`run_make(["install",
    "DESTDIR=..."])`); *env* replaces the environment for a test that drives
    `make -n` with a controlled one. The return is `process_runner.run`'s
    CompletedProcess, so a caller reads `returncode`, `stdout` and `stderr`.
    """
    return run_captured(
        ["make", *args],
        cwd=repo_root.ROOT,
        env=env,
    )


def assert_both_targets_refused(case, env, args, expected):
    """Run `install` and `uninstall` with *env*; both must refuse.

    *args* carries the make variable assignments for each target, and *expected*
    names each substring the diagnostic must carry. `install` and `uninstall`
    share their guards, so a test that drove only one target would miss a guard
    wired to the other.
    """
    for target in ("install", "uninstall"):
        with case.subTest(target=target):
            result = run_make([target, *args], env=env)
            assert_failed(case, result)
            for substring in expected:
                case.assertIn(substring, result.stderr)


def assert_metacharacter_refused(case, variable, make_value, shown_value, args=()):
    """Run `install`/`uninstall` with `variable=make_value`; both must refuse.

    The make-level shell-metacharacter guard refuses the value before any
    recipe of either target runs; its diagnostic names the variable and echoes
    the value back, so *shown_value* is the post-expansion text the diagnostic
    must carry verbatim (a `$$` arrives as `$`). *args* appends further make
    assignments beside the guarded one.
    """
    assert_both_targets_refused(
        case,
        None,
        (*args, f"{variable}={make_value}"),
        (f"{variable} contains a shell metacharacter", shown_value),
    )


def _run(target, destdir, extra=(), env=None):
    """Run *target* with DESTDIR=*destdir*, the shared XDG_DATA_HOME, *extra* and *env*."""
    return run_make(
        [target, f"DESTDIR={destdir}", f"XDG_DATA_HOME={XDG_DATA_HOME}", *extra],
        env=env,
    )


def install(destdir, extra=(), env=None, packages=None):
    """Run `make install` rooted at `destdir`; returns the CompletedProcess.

    `extra` appends make variable assignments (e.g. `COLOR_SCHEME=...`); `env`
    replaces the environment, for tests that shadow a tool on PATH. `packages`
    narrows the install to one `INSTALL_PACKAGES` family (`look-and-feel`), so
    a test of one artifact does not copy the other families; the default
    installs every family, GTK included.
    """
    if packages is not None:
        extra = (*extra, f"INSTALL_PACKAGES={packages}")
    return _run("install", destdir, extra, env)


def uninstall(destdir, extra=(), env=None):
    """Run `make uninstall` rooted at `destdir`; returns the CompletedProcess.

    `extra` and `env` are as for `install`.
    """
    return _run("uninstall", destdir, extra, env)


def uninstall_recipe(destdir, extra=(), env=None):
    """Run the internal `make _uninstall` recipe rooted at *destdir*.

    The public `uninstall` target only wraps the recipe in the data-home and
    flock guards, `install -d`, and a nested `make`; those are covered by
    ``test_theme_install``. Calling the recipe directly keeps each case from
    spawning that second make and taking the lock. *extra* appends make
    variable assignments (e.g. `COLOR_SCHEME=...`); *env* replaces the
    environment, for a test that supplies its own `XDG_CONFIG_HOME`.
    """
    return _run("_uninstall", destdir, extra, env)


def assert_make_n_uninstall_parses(case, *pins):
    """Dry `make -n _uninstall` and pin the parse and the recipe's own pins.

    The public `uninstall` target only prints the guards and its nested locked
    `make _uninstall` under -n, so the scanner's recipe is pinned by drying
    the internal recipe directly: the run must succeed and its dried output
    must name `tools/uninstall_diagnostics.py`. Every `_uninstall` diagnostic
    suite ends with this parse pin; *pins* are the suite's recipe fragments
    (its diagnostic's `--<mode>-id` argument) the dried output must still
    carry.
    """
    result = run_make(["-n", "_uninstall"], env=make_env())
    assert_succeeded(case, result)
    case.assertIn("tools/uninstall_diagnostics.py", result.stdout)
    for pin in pins:
        case.assertIn(pin, result.stdout)


class UninstallRecipeTestCase(unittest.TestCase):
    """Base for the `make _uninstall` diagnostic suites.

    Their shared step is `uninstall_with_config`: run the recipe rooted at
    *tmp* with *XDG_CONFIG_HOME* pointing at *config*, unless the case passes
    its own *env*, for the fallback-path suites that must leave the variable
    unset (or relative). The suites otherwise differ in the file they read
    and in the diagnostic wording each one is the contract for.
    """

    def uninstall_with_config(self, tmp, config, env=None):
        return uninstall_recipe(
            tmp,
            extra=(),
            env=env if env is not None else dict(os.environ, XDG_CONFIG_HOME=config),
        )


def assert_uninstall_diagnostics(case, tmp, config, *printed, absent=(), unchanged=None):
    """Run the suite's `make _uninstall` recipe once and pin its stderr.

    The per-surface `_uninstall` diagnostic suites share one run shape: a
    single recipe run rooted at *tmp* with *XDG_CONFIG_HOME* at *config*,
    success, and the stderr assertions. *printed* names the diagnostic lines
    that must appear and *absent* those that must not; either may be one
    diagnostic line or a tuple of them. *unchanged*, when given, is a path
    whose bytes the run must not touch: the helper reads it
    before the run and again after, as the warn cases pin a diagnostic that
    edits nothing. Returns the recipe's CompletedProcess for the sites that
    pin more than stderr.

    Every one-line stderr rule assertion around a recipe run in the
    `_uninstall` diagnostic suites routes through here; the read-cap suite's
    cap-contract sites keep their own with-open read idiom, and the suites'
    multi-line rule arguments, loop bodies, and the mirror suite's direct
    config reads keep their explicit form.
    """
    original = read_bytes(unchanged) if unchanged is not None else None
    result = case.uninstall_with_config(tmp, config)
    assert_succeeded(case, result)
    for rule in printed:
        case.assertIn(rule, result.stderr)
    # A lone string passed for *absent* must be one rule, not a sequence of
    # characters each asserted on its own.
    for rule in (absent,) if isinstance(absent, str) else absent:
        case.assertNotIn(rule, result.stderr)
    if unchanged is not None:
        case.assertEqual(original, read_bytes(unchanged))
    return result


def assert_diagnostics_in_order(case, result, lines):
    """Assert each of *lines* is in result.stderr, strictly in print order.

    The `_uninstall` suites' recipe-order pins stage several diagnostics in
    one run and pin that stderr lists them in the recipe's published order:
    each fragment must be present, and each fragment's first occurrence must
    sit strictly before the next one's. A diagnostic prints once per run, so
    the first occurrence is the occurrence; as with assert_uninstall_diagnostics,
    a fragment may be a full rule or the distinctive head of one.
    """
    positions = []
    for line in lines:
        case.assertIn(line, result.stderr)
        positions.append(result.stderr.index(line))
    for earlier, later in zip(positions, positions[1:]):
        case.assertLess(earlier, later)


def installed_template(case, packages):
    """Return this test class's installed tree for *packages*, installing once.

    A test class whose methods each need the same installed package would
    otherwise run `make install` once per method. The first call installs into
    a class-owned temporary directory; later calls copy that tree, so every
    caller still gets its own mutable DESTDIR. The template is removed when
    the class's tests finish. A failed install raises through
    ``assert_succeeded`` and is not remembered, so the next caller retries it.
    """
    templates = getattr(type(case), "_installed_templates", None)
    if templates is None:
        templates = {}
        type(case)._installed_templates = templates
    template = templates.get(packages)
    if template is None:
        template = tempfile.mkdtemp(prefix="installed-template-")
        case.addClassCleanup(shutil.rmtree, template, ignore_errors=True)
        assert_succeeded(case, install(template, packages=packages))
        templates[packages] = template
    return template


def _require_no_escaping_symlinks(root):
    """Refuse a symlink under *root* that resolves outside it.

    An installed package can contain a checked-in symlink: ``make install``'s
    ``cp -r`` preserves it in the template. Copying that template with
    ``copytree``'s default ``symlinks=False`` dereferences the link, so a
    private file or an arbitrary directory named by it lands in the test's
    DESTDIR (and a FIFO or device would block or stream forever). Each link
    is therefore resolved before the copy starts, and an escape is refused by
    name.
    """
    root = os.path.abspath(root)
    for directory, dirnames, filenames in os.walk(root):
        for name in (*dirnames, *filenames):
            path = os.path.join(directory, name)
            if os.path.islink(path) and not containment.resolves_within(
                root, path
            ):
                raise ValueError(
                    f"{path} resolves outside {root} (a symlink escape); "
                    "refusing to copy it"
                )


def copy_installed_tree(source, dest):
    """Copy an installed template into *dest*, refusing an escaping symlink.

    *source* is a tree ``make install`` produced, so it can contain a symlink
    copied from the package. The copy preserves symlinks as links instead of
    dereferencing them, and a link that resolves outside *source* is refused
    before anything is written, so a private file's bytes never enter the
    test's DESTDIR. An inner link that stays inside *source* is copied as a
    link.
    """
    _require_no_escaping_symlinks(source)
    shutil.copytree(source, dest, dirs_exist_ok=True, symlinks=True)


@contextlib.contextmanager
def installed_destdir(case, **kwargs):
    """Yield a fresh temporary DESTDIR with `make install` already succeeded.

    Creates a `tempfile.TemporaryDirectory`, runs `install` into it (forwarding
    *kwargs*), asserts the child exited 0 via `assert_succeeded`, and yields the
    directory. The directory is removed when the context exits, so a test that
    only needs the installed tree alive while it inspects it writes
    ``with installed_destdir(self) as tmp:`` instead of repeating the
    tempdir/install/assert scaffold.

    A call naming only `packages` shares one install per test class and copies
    it into the yielded directory; those are the calls whose installed tree the
    tests treat as read-only input. A call with any other make variable or a
    replaced environment installs into the yielded directory each time, since
    its result can differ from another call's.
    """
    with tempfile.TemporaryDirectory() as destdir:
        if set(kwargs) == {"packages"}:
            template = installed_template(case, kwargs["packages"])
            copy_installed_tree(template, destdir)
        else:
            assert_succeeded(case, install(destdir, **kwargs))
        yield destdir


def copy_shipped_file(source, dest):
    """Copy a contributor-supplied repository file to *dest* through the guard.

    *source* is a checked-in theme file, so a symlink at it can resolve outside
    the repository: ``shutil.copy`` would follow the link, pulling a private
    file's bytes into the test tree or streaming a device such as ``/dev/zero``
    without bound. The shared containment reader refuses an escaping symlink, a
    non-regular file and an oversize file before anything is written, and its
    size bound keeps a hostile source from exhausting memory. *dest* is the
    test's throwaway path and is written as a plain file.
    """
    data = containment.read_bytes(source, repo_root.ROOT)
    with open(dest, "wb") as handle:
        handle.write(data)


def assert_files_identical(case, source, target, msg=None):
    """Assert *target* exists and is byte-identical to *source*.

    *case* is the calling ``unittest.TestCase``; its assertions report the
    mismatch. *msg* labels the comparison, defaulting to *target*. The install
    tests use this to pin that a copy is byte-for-byte, not merely present.
    *source* is a contributor-supplied package file, and ``assertEqual`` echoes
    both byte strings when they differ, so a checked-in symlink at *source*
    that resolves outside the repository is refused before it is opened; the
    installed *target* lies in a throwaway DESTDIR and is read as before.
    """
    case.assertTrue(os.path.isfile(target), target)
    original = containment.read_bytes(source, repo_root.ROOT)
    with open(target, "rb") as copy:
        case.assertEqual(original, copy.read(), msg or target)


def shadow_command_env(destdir, name, script):
    """Write `script` as an executable `name` in `<destdir>/fakebin`.

    Returns an environment whose PATH finds the fake before the real command,
    so a test can make a system tool fail partway through `make install`.
    """
    bindir = os.path.join(destdir, "fakebin")
    os.makedirs(bindir, exist_ok=True)
    command = os.path.join(bindir, name)
    with open(command, "w", encoding="utf-8") as handle:
        handle.write(script)
    os.chmod(command, 0o755)
    env = dict(os.environ)
    env["PATH"] = bindir + os.pathsep + os.environ.get("PATH", "")
    return env
