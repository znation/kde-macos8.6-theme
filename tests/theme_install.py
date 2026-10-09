"""Run the repository's `make install` / `make uninstall` against a temp tree.

The installed artifacts land under `$(DESTDIR)$(XDG_DATA_HOME)`, so the install
tests in `test_colorscheme_install`, `test_lookandfeel` and `test_desktoptheme` pass a
throwaway `DESTDIR` and inspect the result there.
"""

import contextlib
import os
import signal
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The data home inside each test's throwaway DESTDIR.
XDG_DATA_HOME = "/share"

# Hard limit for every child process the test suite starts, so a `make`,
# `plasma-apply-*` or `kpackagetool6` that never exits fails the test instead of
# stalling `make check` forever.
SUBPROCESS_TIMEOUT = 60


def _kill_process_group(process):
    """SIGKILL *process* and every process in its group, tolerating races.

    The child is started in its own session, so its pid is its process-group
    id; killing the group reaps the descendants a shell left behind. A
    `ProcessLookupError` means the child already exited and there is nothing
    left to signal, which is not an error here.
    """
    try:
        os.killpg(os.getpgid(process.pid), signal.SIGKILL)
    except OSError:
        process.kill()


def start(argv, **kwargs):
    """Start `argv` in its own session, for a caller that polls it, then `finish`.

    A test that must observe a child while it runs starts it here instead of
    with `subprocess.Popen` directly, so `finish` can kill the child's whole
    process group when it outlives its timeout. `start_new_session` is forced,
    not defaulted, so that group is never the suite's own.
    """
    kwargs["start_new_session"] = True
    return subprocess.Popen(argv, **kwargs)


def finish(process, timeout=None):
    """Wait for a process from `start`, killing its group if it times out.

    Returns ``(stdout, stderr)``. A child that outlives *timeout* is SIGKILLed
    with every process in its group, so a hung `make install` cannot leave its
    `flock`/inner-`make` descendants running after the test has failed. A
    descendant that escaped the group and still holds the pipes is not waited
    on: the timeout is reported instead of blocking the suite. The constant is
    read at call time, so a test can patch it.
    """
    if timeout is None:
        timeout = SUBPROCESS_TIMEOUT
    try:
        return process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        _kill_process_group(process)
        try:
            stdout, stderr = process.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            # A descendant left the process group (for example by calling
            # setsid) and still holds the pipes. The direct child is dead;
            # report the timeout rather than block on the escaped descendant.
            raise subprocess.TimeoutExpired(process.args, timeout) from None
        raise subprocess.TimeoutExpired(
            process.args, timeout, output=stdout, stderr=stderr
        ) from None


@contextlib.contextmanager
def running(argv, **kwargs):
    """Start `argv` and guarantee its process group is killed when the block exits.

    `start`/`finish` is enough when the two calls are adjacent, but the lock
    test starts `make install`, polls it, and only then finishes it. Anything
    that raises between the start and the finish -- a poll that fails, or the
    operator interrupting `make check` -- would skip `finish` and leave the
    child, its descendants, and the data-home lock they hold alive after the
    test has failed. This context manager kills a still-running child with its
    whole process group on the way out whatever happens; a caller that reached
    `finish` first leaves nothing to kill, so the normal path is unaffected.
    It closes the child's pipes on the way out too, so a caller that did not
    reach `finish` -- including one whose child exited before the block ended
    -- does not leak them.

    Yields the `Popen`; `kwargs` are as for `start`.
    """
    process = start(argv, **kwargs)
    try:
        yield process
    finally:
        if process.poll() is None:
            _kill_process_group(process)
            process.wait()
        # `finish` drains and closes the pipes; a caller that never reached it
        # -- because the block raised, or because the child exited on its own
        # before the block ended -- leaves the read ends open until the
        # `Popen` is collected, so close them here. `close()` is idempotent,
        # so a caller that did reach `finish` is unaffected.
        for stream in (process.stdin, process.stdout, process.stderr):
            if stream is not None:
                stream.close()


def run(argv, **kwargs):
    """Run `argv` under the suite's subprocess timeout.

    This is the suite's timeout runner: a child that outlives
    `SUBPROCESS_TIMEOUT` raises `subprocess.TimeoutExpired` rather than hanging
    the suite. The constant is read at call time, so a test can patch it.

    The child starts a new session, so a timeout kills its whole process
    group rather than only the direct child. `make install` runs
    `flock ... make _install`: `subprocess.run`'s timeout SIGKILLs only the
    outer `make`, so the inner make and flock survive as orphans -- still
    running against the throwaway DESTDIR and still holding the data-home
    lock. `capture_output` is expanded here because `Popen` does not take it
    directly.
    """
    timeout = kwargs.pop("timeout", SUBPROCESS_TIMEOUT)
    if kwargs.pop("capture_output", False):
        kwargs.setdefault("stdout", subprocess.PIPE)
        kwargs.setdefault("stderr", subprocess.PIPE)
    process = start(argv, **kwargs)
    stdout, stderr = finish(process, timeout)
    return subprocess.CompletedProcess(
        process.args, process.returncode, stdout, stderr
    )


def run_captured(argv, **kwargs):
    """Run `argv` under `run`, capturing its output as decoded text.

    A caller that reads the child's `stdout`/`stderr` as `str` gets
    `capture_output` and `text` defaulted here; the rest (`cwd`, `env`,
    `timeout`) is forwarded to `run`.
    """
    kwargs.setdefault("capture_output", True)
    kwargs.setdefault("text", True)
    return run(argv, **kwargs)


def run_make(args, env=None):
    """Run `make *args*` at the repository root under the suite's timeout runner.

    *args* is the target plus any variable assignments (`run_make(["install",
    "DESTDIR=..."])`); *env* replaces the environment for a test that drives
    `make -n` with a controlled one. The return is `run`'s CompletedProcess,
    so a caller reads `returncode`, `stdout` and `stderr`.
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


def install(destdir, extra=(), env=None):
    """Run `make install` rooted at `destdir`; returns the CompletedProcess.

    `extra` appends make variable assignments (e.g. `COLOR_SCHEME=...`); `env`
    replaces the environment, for tests that shadow a tool on PATH.
    """
    return _run("install", destdir, extra, env)


def uninstall(destdir, extra=(), env=None):
    """Run `make uninstall` rooted at `destdir`; returns the CompletedProcess.

    `extra` and `env` are as for `install`.
    """
    return _run("uninstall", destdir, extra, env)


def installed_plasma_dir(destdir, kind):
    """Directory `make install` writes a Plasma package family into.

    The Makefile installs under `$(DESTDIR)$(XDG_DATA_HOME)/plasma/<kind>`;
    `kind` is `look-and-feel` or `desktoptheme`. `installed_package` joins a
    package's own directory onto the result; `staging_sibling`/`old_sibling`
    build a hidden sibling of that directory.
    """
    return os.path.join(destdir, XDG_DATA_HOME.lstrip("/"), "plasma", kind)


def installed_package(destdir, kind, package_id):
    """Directory `make install` writes one Plasma package into.

    The package family comes from `installed_plasma_dir`; the package's own
    directory is that family joined with its id (`org.macos8.desktop`).
    """
    return os.path.join(installed_plasma_dir(destdir, kind), package_id)


def installed_color_scheme_dir(destdir):
    """Directory `make install` writes the color scheme into.

    The Makefile installs the scheme under
    `$(DESTDIR)$(XDG_DATA_HOME)/color-schemes`, the non-Plasma sibling of
    `installed_plasma_dir`'s families. `installed_color_scheme` joins a
    scheme's filename onto the result; `staging_sibling` builds its hidden
    sibling.
    """
    return os.path.join(destdir, XDG_DATA_HOME.lstrip("/"), "color-schemes")


def installed_color_scheme(destdir, name="MacOS8.colors"):
    """Path `make install` writes a color scheme file to.

    The directory comes from `installed_color_scheme_dir`; the file is that
    directory joined with the scheme's source basename (`MacOS8.colors` by
    default, or a renamed source passed as `COLOR_SCHEME`).
    """
    return os.path.join(installed_color_scheme_dir(destdir), name)


def staging_sibling(parent, name):
    """Hidden path `make install` copies `name` into before swapping it in.

    The Makefile stages the artifact as `parent/.<name>.staging` and renames it
    into place, so a test that simulates a killed install builds the same path.
    """
    return os.path.join(parent, "." + name + ".staging")


def old_sibling(parent, name):
    """Hidden path `make install` moves the working `name` aside to.

    The Makefile moves the artifact to `parent/.<name>.old` during the swap and
    removes it after the rename, so a killed install can leave it behind.
    """
    return os.path.join(parent, "." + name + ".old")


def assert_files_identical(case, source, target, msg=None):
    """Assert *target* exists and is byte-identical to *source*.

    *case* is the calling ``unittest.TestCase``; its assertions report the
    mismatch. *msg* labels the comparison, defaulting to *target*. The install
    tests use this to pin that a copy is byte-for-byte, not merely present.
    """
    case.assertTrue(os.path.isfile(target), target)
    with open(source, "rb") as original, open(target, "rb") as copy:
        case.assertEqual(original.read(), copy.read(), msg or target)


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
