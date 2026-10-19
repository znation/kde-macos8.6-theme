"""Run the repository's `make install` / `make uninstall` against a temp tree.

The installed artifacts land under `$(DESTDIR)$(XDG_DATA_HOME)`; the install
tests of each artifact (color scheme, global theme, desktop theme, Aurorae
decoration, wallpaper, icon theme) pass a throwaway `DESTDIR` and inspect the
result there via `support.installed_paths`, which names the layout.
Child processes go through `process_runner`, which applies the suite's timeout
and process-group cleanup. The module also re-exports `ROOT` (from
`repo_root`) and defines `run_captured` for tests that need a captured child.
"""

import contextlib
import os
import tempfile

from support import containment
from support import process_runner
from support.installed_paths import XDG_DATA_HOME
from support.process_assertions import assert_succeeded
from support.repo_root import ROOT


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
        cwd=ROOT,
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
    a test of one artifact does not copy the other six; the default installs
    every family.
    """
    if packages is not None:
        extra = (*extra, f"INSTALL_PACKAGES={packages}")
    return _run("install", destdir, extra, env)


def uninstall(destdir, extra=(), env=None):
    """Run `make uninstall` rooted at `destdir`; returns the CompletedProcess.

    `extra` and `env` are as for `install`.
    """
    return _run("uninstall", destdir, extra, env)


@contextlib.contextmanager
def installed_destdir(case, **kwargs):
    """Yield a fresh temporary DESTDIR with `make install` already succeeded.

    Creates a `tempfile.TemporaryDirectory`, runs `install` into it (forwarding
    *kwargs*), asserts the child exited 0 via `assert_succeeded`, and yields the
    directory. The directory is removed when the context exits, so a test that
    only needs the installed tree alive while it inspects it writes
    ``with installed_destdir(self) as tmp:`` instead of repeating the
    tempdir/install/assert scaffold.
    """
    with tempfile.TemporaryDirectory() as destdir:
        assert_succeeded(case, install(destdir, **kwargs))
        yield destdir


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
    original = containment.read_bytes(source, ROOT)
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
