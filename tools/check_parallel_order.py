"""Order check workers by each module's recorded wall duration.

175 modules share the worker budget, and one suite (the real render
surface) alone runs for seconds while most modules finish well under a
second. Starting the slowest recorded module first keeps the whole critical
path covered by the other workers: with plain discovery (alphabetical)
order the render module starts only after roughly a run's worth of shorter
modules, and nearly every other module is already finished when its run
begins.

The durations come from the previous run's completion times, saved to a
small JSON cache under ``$XDG_CACHE_HOME`` (default ``~/.cache``). The
cache is best-effort in both directions: any read or parse failure leaves
discovery order, any write failure only names itself on stderr, so a
read-only host runs the plain discovery order. Only the run's own modules
are kept in the cache, so removed modules leave no entries behind and the
file cannot grow without bound.
"""

from __future__ import annotations

import json
import math
import os
from pathlib import Path

if __package__:
    from tools.atomic_write import write_bytes_atomically
else:  # run directly: python3 tools/check_parallel_order.py
    from atomic_write import write_bytes_atomically

_CACHE_VERSION = 1
_CACHE_DIR = ("kde-macos8.6-theme",)
_CACHE_FILE = "check-durations.json"


def cache_path() -> str:
    """Return the durations cache path under the XDG cache home."""
    base = os.environ.get("XDG_CACHE_HOME")
    if not base or not os.path.isabs(base):
        base = os.path.join(os.path.expanduser("~"), ".cache")
    return os.path.join(base, *_CACHE_DIR, _CACHE_FILE)


def load_durations(path: str) -> dict[str, float]:
    """Read per-module durations, returning an empty dict on any bad state.

    A missing, unreadable or malformed file (a cache volume that disappeared,
    a partially written file from a killed run, a foreign JSON shape) must not
    cost the run anything: an empty result falls back to discovery order in
    :func:`order_modules`, the same order a host that never had a cache uses.
    """
    try:
        with open(path, "rb") as source:
            record = json.loads(source.read())
    except (OSError, ValueError):
        return {}
    if not isinstance(record, dict) or record.get("version") != _CACHE_VERSION:
        return {}
    entries = record.get("durations")
    if not isinstance(entries, dict):
        return {}
    durations: dict[str, float] = {}
    for module, seconds in entries.items():
        if not isinstance(module, str) or not isinstance(seconds, (int, float)):
            continue
        if not math.isfinite(seconds) or seconds < 0:
            continue
        durations[module] = float(seconds)
    return durations


def order_modules(modules: list[str],
                  durations: dict[str, float]) -> list[str]:
    """Sort the queue's slowest recorded module first; ties keep discovery order.

    ``sorted`` is stable, so modules with no recorded duration (no cache, or a
    module the previous run never reached) stay in discovery order relative to
    each other. A wrong placement merely reorders overlapping workers; the
    results still print in discovery order.
    """
    return sorted(modules, key=lambda module: -durations.get(module, 0.0))


def save_durations(path: str, durations: dict[str, float]) -> None:
    """Atomically write one run's durations; an OSError reaches the caller.

    Callers pass only the modules that ran this run, so the file holds no
    stale entries for removed modules and cannot grow without bound.
    Concurrent ``make check`` runs on one host race benignly: the last
    completion writes last, and each write is a whole file.
    """
    payload = {
        "version": _CACHE_VERSION,
        "durations": {module: round(seconds, 3)
                      for module, seconds in sorted(durations.items())},
    }
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    data = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    write_bytes_atomically(
        Path(path), (data + "\n").encode("utf-8"))
