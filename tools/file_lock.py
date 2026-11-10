"""The bounded-wait exclusive directory flock the apply tools share.

``apply-gtk``/``remove-gtk`` serialize on a lock over the directory
containing the config home (plus the data-home lock ``make install``
holds), and ``install-firefox``/``remove-firefox`` on a lock over the
profile directory. All of them contend on one directory inode with an
exclusive ``flock``: the lock adds no lock file to the user's tree and
the kernel releases it when the process dies, SIGKILL included.

The wait for a holder is bounded, so a run stopped with SIGSTOP cannot
block every later run forever. The semantics are easy to get subtly
wrong -- an interrupted wait must be retried, only ``EACCES``/``EAGAIN``
count as contention, and closing the descriptor, not an explicit unlock,
releases the lock -- so the one copy lives here and each tool passes its
own diagnostic wording and refusal exception class.
"""

from __future__ import annotations

import contextlib
import errno
import fcntl
import os
import time
from collections.abc import Iterator
from pathlib import Path

POLL_SECONDS = 0.05


def _wait_for_flock_error(
    exc: OSError,
    directory: Path,
    artifact: str,
    holder: str,
    timeout: float,
    deadline: float,
    error: type[Exception],
) -> None:
    """Handle one ``flock`` errno: raise anything else unpreserved, give up
    past the deadline, and otherwise sleep before the retry (an EINTR attempt
    retries without waiting)."""
    if exc.errno not in (errno.EINTR, errno.EACCES, errno.EAGAIN):
        raise error(f"cannot lock {directory} {artifact}: {exc}") from exc
    if time.monotonic() >= deadline:
        raise error(
            f"gave up after {timeout:g}s waiting for "
            f"{holder}; nothing was changed"
        )
    if exc.errno != errno.EINTR:
        time.sleep(POLL_SECONDS)


def _acquire_flock(
    descriptor: int,
    directory: Path,
    artifact: str,
    holder: str,
    timeout: float,
    error: type[Exception],
) -> None:
    """Take an exclusive non-blocking ``flock``, retrying until *timeout* runs out."""
    deadline = time.monotonic() + timeout
    while True:
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return
        except OSError as exc:
            _wait_for_flock_error(
                exc, directory, artifact, holder, timeout, deadline, error
            )


@contextlib.contextmanager
def exclusive_flock(
    directory: Path,
    artifact: str,
    holder: str,
    timeout: float,
    *,
    error: type[Exception],
) -> Iterator[None]:
    """Hold an exclusive flock on *directory* for the body's duration.

    *artifact* phrases what the lock protects ("for the GTK selection")
    and appears in the diagnostic of an open failure or a non-contention
    flock error; *holder* names the run being waited for in the timeout
    diagnostic. The directory must already exist (and be openable);
    otherwise a :class:`ConfigError`-class *error* naming it is raised.
    When another run keeps the lock past *timeout* seconds, *error* is
    raised naming *holder*, rather than blocking every later run forever.
    A non-contention flock error (the caller may not open the directory,
    for example) is an *error* too -- the yield loop classifies the
    ``errno`` -- and closing the descriptor releases the lock even when
    the body raised.
    """
    try:
        descriptor = os.open(
            directory, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
        )
    except OSError as exc:
        raise error(f"cannot lock {directory} {artifact}: {exc}") from exc
    try:
        _acquire_flock(descriptor, directory, artifact, holder, timeout, error)
        yield
    finally:
        # Closing the descriptor releases the lock even when the body raised.
        os.close(descriptor)


@contextlib.contextmanager
def parent_dir_lock(
    child: Path,
    artifact: str,
    holder: str,
    timeout: float,
    *,
    error: type[Exception],
) -> Iterator[None]:
    """Hold an exclusive lock on *child*'s parent directory.

    Apply and removal runs over a config home that may not exist yet lock
    this way: the containing directory is created if needed so both a run
    about to create *child* and a run not creating it contend on one inode,
    while *child* itself is left for its own run to create. Otherwise the
    semantics, diagnostic wording and bounded wait are those of
    :func:`exclusive_flock`. Exactly two call sites use this helper:
    ``apply-gtk``'s and ``remove-kvantum``'s ``_config_lock`` wrappers.
    """
    lock_dir = child.parent
    try:
        lock_dir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise error(f"cannot create {lock_dir}: {exc}") from exc
    with exclusive_flock(
        lock_dir, artifact, holder, timeout=timeout, error=error
    ):
        yield


@contextlib.contextmanager
def installed_data_lock(
    data_home: Path,
    artifact: str,
    timeout: float,
    *,
    error: type[Exception],
) -> Iterator[None]:
    """Serialize an installed-artifact check and selection with install runs.

    The Makefile install and uninstall targets hold this same data-home inode
    for their full run. Callers check their installed files again while this
    lock is held, so an uninstall cannot invalidate a selection mid-run.
    """
    with exclusive_flock(
        data_home,
        artifact,
        f"another install or uninstall to finish with {data_home}",
        timeout,
        error=error,
    ):
        yield
