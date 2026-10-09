"""Run child processes under the suite's timeout with process-group cleanup.

A test that spawns `make`, `plasma-apply-*`, `kpackagetool6` or a tool script
must not let a hung child stall `make check`, and a timeout must kill the whole
process group so a shell's descendants (an inner `make`, a `flock`) do not
survive as orphans. `run` is the common path; `start`/`finish`/`running` expose
the lifecycle to a test that has to poll a child while it runs.
"""

import contextlib
import os
import signal
import subprocess

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
