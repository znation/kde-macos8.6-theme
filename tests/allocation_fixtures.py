"""Measure the peak heap a callable allocates, for the memory-bound tests.

The PNG reader's oversize-file guard and the decoder's decompression-bomb
guard both prove they stopped early by running the call under ``tracemalloc``
and asserting the traced peak stayed under a bound. That start/read/stop
scaffold lives here once, so each test reads only the call and its bound.
"""

import tracemalloc


def peak_allocation(call):
    """Return ``(call(), peak)`` with the peak traced allocation in bytes.

    ``call`` runs under ``tracemalloc`` and its result is returned beside the
    peak traced memory, read before the tracer stops. The tracer is stopped in
    a ``finally`` so a raising *call* -- the oversize/bomb guards raise the
    ``PngError`` the caller then inspects -- does not leave it running.
    """
    tracemalloc.start()
    try:
        result = call()
        peak = tracemalloc.get_traced_memory()[1]
    finally:
        tracemalloc.stop()
    return result, peak
