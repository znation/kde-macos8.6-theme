"""Run the repository's `make install` / `make uninstall` against a temp tree.

The installed artifacts land under `$(DESTDIR)$(XDG_DATA_HOME)`, so the install
tests in `test_colorscheme`, `test_lookandfeel` and `test_desktoptheme` pass a
throwaway `DESTDIR` and inspect the result there.
"""

import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The data home inside each test's throwaway DESTDIR.
XDG_DATA_HOME = "/share"

# Hard limit for every child process the test suite starts, so a `make`,
# `plasma-apply-*` or `kpackagetool6` that never exits fails the test instead of
# stalling `make check` forever.
SUBPROCESS_TIMEOUT = 60


def run(argv, **kwargs):
    """Run `argv` under the suite's subprocess timeout.

    Every subprocess the tests start goes through here, so a child that outlives
    `SUBPROCESS_TIMEOUT` raises `subprocess.TimeoutExpired` rather than hanging
    the suite. The constant is read at call time, so a test can patch it.
    """
    kwargs.setdefault("timeout", SUBPROCESS_TIMEOUT)
    return subprocess.run(argv, **kwargs)


def _run(target, destdir, extra=(), env=None):
    return run(
        [
            "make", target, f"DESTDIR={destdir}", f"XDG_DATA_HOME={XDG_DATA_HOME}",
            *extra,
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
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
