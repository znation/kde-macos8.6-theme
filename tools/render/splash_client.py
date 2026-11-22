"""Build the argv for the splash render client."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tools.render.session import Session


def splash_client(session: Session) -> tuple[str, ...]:
    """Return the splash argv the splash mode renders.

    ``ksplashqml --test --nofork`` opens the look-and-feel package's own
    ``contents/splash/Splash.qml`` painted from the session's installed tree,
    never the caller's data home: the fullscreen layer-shell surface whose
    ``#63639C`` field the queued splash gate will compare. ``--test`` is the
    shape the bare nested session can capture: upstream 6.3.6
    ``ksplash/ksplashqml/splashapp.cpp`` advances one stage every 2 s in test
    mode and exits 0 at stage 7 (about 10 s in), so the client is alive at
    the existing 8 s settle but keeps its lifetime deterministic instead of
    drifting, while a plain ``--nofork`` client died on its own between the
    25 s and 45 s marks in the 2026-11-11 probe, taking the mapped splash
    with it -- a 30 s settle captured an already-vanished splash. The
    argument is the installed package *directory*
    (``.../plasma/look-and-feel/org.macos8.desktop``): a bare theme id would
    resolve outside the scratch data home.
    """
    return (
        "ksplashqml",
        "--test",
        "--nofork",
        str(session.data / "plasma" / "look-and-feel" / "org.macos8.desktop"),
    )
