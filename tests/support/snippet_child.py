"""Run a ``python -c`` snippet in a child process without a fresh interpreter.

The suite's FIFO guards prove that a reader refuses a pipe instead of blocking
on it. Each guard runs the reader in a child process, so a reader that blocks
cannot stall ``make check``, and the parent bounds the child with a timeout.

A child started with ``subprocess.run([sys.executable, "-c", ...])`` pays for a
fresh interpreter and re-imports the module under test: the suite's guards
spent about 1.8 seconds on that, nearly all of it import time in the child.

:func:`run` forks instead. The child inherits this interpreter with its
modules already imported, so the snippet runs at once; it is still a separate
process with its own stdout and stderr, and the parent still kills it when
the timeout expires, so the guarantee the guards rely on does not change. A
platform without ``os.fork`` falls back to ``subprocess.run``.

Forking has three hazards, each pinned by ``tests/test_snippet_child.py``:
the parent's own pending output must be written once and not by the child, a
child that has already been reaped must never be signalled (its pid may
belong to another process by then), and the reap that follows a kill must be
bounded, so a child the kernel does not release cannot stall the suite from
the cleanup path.
"""

from __future__ import annotations

import locale
import os
import select
import signal
import subprocess
import sys
import time
import traceback

from support import process_runner


def run(snippet_argv, cwd=None, timeout=10):
    """Run the snippet *snippet_argv* in a child process.

    *snippet_argv* is the argument list a ``python -c`` command takes: its
    first element is the snippet's source and the rest are the arguments the
    snippet reads from ``sys.argv``. The snippet runs as ``__main__`` with
    ``sys.argv == ["-c", *args]`` and the working directory first on
    ``sys.path``, exactly as ``python -c code *args`` would see it.

    The return is a `subprocess.CompletedProcess` with the child's exit
    status and its captured stdout and stderr, decoded as text. A child that
    outlives *timeout* is killed and `subprocess.TimeoutExpired` is raised, as
    `subprocess.run` does. A child that has already exited is reported with
    its own status instead: it is never signalled, because its pid has been
    reaped and may belong to another process by then.
    """
    if not hasattr(os, "fork"):
        code, *args = snippet_argv
        return subprocess.run(
            [sys.executable, "-c", code, *args],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd,
        )
    return _run_forked(snippet_argv, cwd, timeout)


def _run_forked(snippet_argv, cwd, timeout):
    """Run *snippet_argv* in a forked child; return its `CompletedProcess`."""
    # The parent's pending output belongs to the parent. It is flushed here,
    # before the fork, so the child inherits empty buffers: a flush in the
    # child would write the parent's bytes to the real stdout, and the parent
    # would write the same bytes again when it flushed its own copy of them.
    _flush_parent_streams()
    out_read, out_write = os.pipe()
    err_read, err_write = os.pipe()
    pid = os.fork()
    if pid == 0:
        try:
            os.close(out_read)
            os.close(err_read)
        except BaseException:
            os._exit(1)
        _run_snippet(snippet_argv, cwd, out_write, err_write)
    os.close(out_write)
    os.close(err_write)
    return _collect(pid, out_read, err_read, snippet_argv, timeout)


def _flush_parent_streams():
    """Flush the parent's own buffered stdout and stderr.

    The child's copy of the parent's buffers must not be flushed: the bytes
    are in the parent's copy as well, so the child would write them to the
    real stdout and the parent would write them a second time. Flushing here
    writes them once and leaves the child with empty buffers.
    """
    for stream in (sys.stdout, sys.stderr):
        if stream is not None:
            stream.flush()


def _run_snippet(snippet_argv, cwd, out_write, err_write):
    """Run the snippet in the forked child; never returns.

    The child writes to its own stdout and stderr, so the parent sees the
    snippet's output and not the rest of the suite's. It leaves through
    `os._exit`, which skips the interpreter's shutdown: the child must not
    flush the parent's streams, run its exit handlers or report the parent's
    coverage of its own death.
    """
    code, *args = snippet_argv
    status = 0
    try:
        os.dup2(out_write, 1)
        os.dup2(err_write, 2)
        os.close(out_write)
        os.close(err_write)
        if cwd is not None:
            os.chdir(cwd)
        # `python -c code args` sees sys.argv == ["-c", *args] and puts the
        # working directory first on sys.path.
        sys.argv = ["-c", *args]
        sys.path.insert(0, "")
        try:
            exec(compile(code, "<string>", "exec"), {"__name__": "__main__"})
        except SystemExit as exc:
            status = exc.code
        except BaseException:
            traceback.print_exc()
            status = 1
        try:
            sys.stdout.flush()
            sys.stderr.flush()
        except BaseException:
            pass
    except BaseException:
        status = 1
    if status is None:
        status = 0
    elif not isinstance(status, int):
        print(status, file=sys.stderr)
        status = 1
    os._exit(status)


def _drain(open_streams, data):
    """Read every available chunk into *data*, dropping a stream at EOF.

    *open_streams* is updated in place: a descriptor the child has closed
    returns an empty chunk and is removed, so the caller can stop once every
    stream is drained. A non-blocking descriptor with nothing to read is left
    for the next pass.
    """
    for fd in tuple(open_streams):
        try:
            chunk = os.read(fd, 65536)
        except BlockingIOError:
            continue
        if chunk:
            data[fd] += chunk
        else:
            open_streams.discard(fd)


def _collect(pid, out_read, err_read, snippet_argv, timeout):
    """Wait for the child, capture its output and return its `CompletedProcess`.

    The child's output is drained while it runs, so a child that writes more
    than a pipe buffer holds does not block on the write and time out with
    its output lost. A child that outlives *timeout* is killed, reaped and
    reported as `subprocess.TimeoutExpired`. The wait between drains is a
    bounded ``select`` on the still-open pipes, so a chunk or the EOF a
    child's exit closes its pipes with wakes it at once; the 5ms bound keeps
    the ready-wait short and a pipe-less child keeps the old 5ms sleep.

    A child that has already exited is never signalled: its status has been
    reaped, so the pid may belong to another process by the time the wait
    ends. The reap that follows the kill is bounded, so a child the kernel
    does not release cannot stall the suite from the cleanup path.
    """
    os.set_blocking(out_read, False)
    os.set_blocking(err_read, False)
    data = {out_read: bytearray(), err_read: bytearray()}
    open_streams = {out_read, err_read}
    deadline = time.monotonic() + timeout
    status = None
    while True:
        _drain(open_streams, data)
        if status is None:
            reaped, raw = os.waitpid(pid, os.WNOHANG)
            if reaped == pid:
                status = raw
        if status is not None and not open_streams:
            break
        if time.monotonic() < deadline:
            if open_streams:
                # Wait for a stream to become readable instead of sleeping the
                # slice out: the slice bound keeps the reap poll interval, but
                # a chunk that arrives mid-slice (or the EOF a child's exit
                # closes its pipes with) wakes the select at once, so a fast
                # child does not pay the full slice before its next drain.
                select.select(tuple(open_streams), (), (), 0.005)
            else:
                time.sleep(0.005)
            continue
        if status is not None:
            # The child has exited and been reaped; only a writer that
            # outlived it keeps the pipe open. There is nothing to kill --
            # its pid is gone -- so the wait ends here and the child's own
            # result is reported.
            break
        # The child is still running: kill it, then wait for the kernel to
        # release it, with a bound.
        _kill(pid)
        _reap(pid)
        for fd in (out_read, err_read):
            os.close(fd)
        raise subprocess.TimeoutExpired(snippet_argv, timeout)
    for fd in (out_read, err_read):
        os.close(fd)
    encoding = locale.getpreferredencoding(False)
    return subprocess.CompletedProcess(
        [sys.executable, "-c", *snippet_argv],
        os.waitstatus_to_exitcode(status),
        data[out_read].decode(encoding, "replace"),
        data[err_read].decode(encoding, "replace"),
    )


def _kill(pid):
    """SIGKILL *pid*, tolerating a child that has already gone.

    A `ProcessLookupError` means the pid names no process, which is not an
    error here: there is nothing left to signal.
    """
    try:
        os.kill(pid, signal.SIGKILL)
    except ProcessLookupError:
        pass


def _reap(pid, timeout=None):
    """Wait for a killed *pid* to be released, with a bound.

    A child that was just SIGKILLed normally dies at once and the wait
    returns immediately. A child stuck in uninterruptible I/O is not released
    until the kernel lets go, which may be never, so the wait is bounded: an
    unbounded one would stall `make check` with no diagnostic, on the cleanup
    path of a test that was already failing. A reap that still times out is
    not re-raised -- the kill is already sent and nothing more can be done
    for the child -- and is reported on stderr instead, so the stuck child is
    visible rather than silent. The bound is
    `process_runner.REAP_TIMEOUT`, the one the suite's other child cleanup
    uses, and it is read at call time so a test can shorten it.
    """
    if timeout is None:
        timeout = process_runner.REAP_TIMEOUT
    deadline = time.monotonic() + timeout
    while True:
        try:
            reaped, _ = os.waitpid(pid, os.WNOHANG)
        except ChildProcessError:
            # Nothing waits for this pid any more: it is already gone.
            return
        if reaped == pid:
            return
        if time.monotonic() >= deadline:
            print(
                f"snippet_child: child {pid} was not released within "
                f"{timeout:g}s after it was killed; it is stuck in "
                "uninterruptible I/O and cannot be reaped",
                file=sys.stderr,
            )
            return
        time.sleep(0.005)
