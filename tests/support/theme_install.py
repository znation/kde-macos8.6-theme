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

from support import containment
from support import process_runner
from support import repo_root
from support.installed_paths import XDG_DATA_HOME
from support.process_assertions import assert_succeeded


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


def _run(target, destdir, extra=(), env=None):
    return run_make(
        [target, f"DESTDIR={destdir}", f"XDG_DATA_HOME={XDG_DATA_HOME}", *extra],
        env=env,
    )


def install(destdir, extra=(), env=None, packages=None):
    """Run `make install` rooted at `destdir`; returns the CompletedProcess.

    `extra` appends make variable assignments (e.g. `COLOR_SCHEME=...`); `env`
    replaces the environment, for tests that shadow a tool on PATH. `packages`
    narrows the install to one `INSTALL_PACKAGES` family (`look-and-feel`), so
    a test of one artifact does not copy the other seven; the default installs
    every default family (`gtk` is opt-in).
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
