"""Skip guards the render capture gates share.

The Plasma tool lists (the applet render's five tools plus each mode's own
client), the software-renderer skip condition and the guard decorators that
write a gate's ``__unittest_skip__`` flag live here, so the dialog, desktop
and splash gates skip under the same condition their render CLI refuses on.
The pixel-reading mixin, the render session batch, the capture diagnostics
and the dialog-gate scaffolding live in the sibling modules
(``pixel_pins.py``, ``renders.py``, ``capture_diagnostics.py`` and
``gates.py``).
"""

from __future__ import annotations

import os
import shutil
import sys
from unittest import mock

REAL_TOOLS = ("kwin_wayland", "dbus-run-session", "plasmawindowed", "spectacle",
              "plasma-apply-colorscheme")
# The dialog clients the dialog modes open, beside the applet render tools.
# One literal feeds the gates' skip guard and the guard pins below, so an
# edit to either the CLI's requirement list or this list cannot drift the
# skip condition away from the condition the render CLI refuses on: each
# dialog flag requires its own client by name (kdialog for the thirteen kdialog
# modes, zenity for the GTK mode), and the gates skip when either client
# or any Plasma tool is absent.
DIALOG_REAL_TOOLS = REAL_TOOLS + ("kdialog", "zenity")
# The desktop mode's client, beside the applet render tools: the same set the
# CLI's desktop preflight requires (render_surface.py joins "plasmashell"
# onto its requirements for --desktop). One literal feeds the desktop gate's
# skip guard, as DIALOG_REAL_TOOLS feeds the dialog gates'.
DESKTOP_REAL_TOOLS = REAL_TOOLS + ("plasmashell",)
# The splash mode's client, beside the applet render tools: the same set the
# CLI's splash preflight requires (render_surface.py joins "ksplashqml"
# onto its requirements for --splash). One literal feeds the splash gate's
# skip guard, as DESKTOP_REAL_TOOLS feeds the desktop gate's.
SPLASH_REAL_TOOLS = REAL_TOOLS + ("ksplashqml",)
# Mesa drivers that render on the CPU. KWin's ScreenShot2 offscreen effect
# allocates a non-software EGL buffer for its render target; on a software
# renderer the allocation has no render engine behind it, and llvmpipe faults
# while the DBus reply waits on the resulting fence. KWin fixed this in 6.8
# (offscreeneffect: allocate a software buffer on software renderers,
# add43708), which the hosted 26.04 image does not carry, so the capture
# gates skip rather than time out there.
SOFTWARE_RENDERER_DRIVERS = frozenset({"llvmpipe", "softpipe", "swrast", "zink"})

SOFTWARE_RENDER_SKIP_REASON = (
    "KWin's ScreenShot2 offscreen effect hangs on a software Mesa renderer "
    "(fixed in KWin 6.8); run on a GPU-backed host to exercise the capture gates"
)


def software_renderer_skip_reason():
    """Return the capture gates' skip reason when Mesa is forced to software."""
    if os.environ.get("LIBGL_ALWAYS_SOFTWARE") == "1":
        return SOFTWARE_RENDER_SKIP_REASON
    for variable in ("MESA_LOADER_DRIVER_OVERRIDE", "GALLIUM_DRIVER"):
        if os.environ.get(variable, "").lower() in SOFTWARE_RENDERER_DRIVERS:
            return SOFTWARE_RENDER_SKIP_REASON
    return None


def dialog_gate_guard():
    """Return the skip guard the fifteen dialog render gates share.

    The dialog render CLI needs the same five Plasma tools as the applet
    render plus the client its requested mode opens (it exits 2 with a
    missing-tool diagnostic when one is absent: kdialog for the thirteen
    kdialog modes, zenity for the GTK mode), so the fifteen dialog gates skip
    under the condition the applet gate's ``skipUnless`` guard uses
    (``tests/test_render_surface.py``),
    extended with both clients. A gate that failed rather than skipped
    where its tools are missing would turn `make check` red on a machine
    that merely lacks Plasma, where the sibling applet gate already skips.
    """
    tools = DIALOG_REAL_TOOLS
    reason = software_renderer_skip_reason() or (
        "needs kwin_wayland, dbus-run-session, plasmawindowed, spectacle, "
        "plasma-apply-colorscheme, kdialog and zenity on PATH"
    )
    missing = [tool for tool in tools if shutil.which(tool) is None]

    def decorator(cls):
        # `unittest.skip` only annotates when its condition fails, so the
        # guard writes the attributes itself: the skip flag must be
        # present (False where every tool exists and the renderer is a GPU)
        # whatever the host has.
        cls.__unittest_skip__ = bool(missing) or software_renderer_skip_reason() is not None
        cls.__unittest_skip_why__ = reason
        return cls

    return decorator


def desktop_gate_guard():
    """Return the skip guard the desktop render gate uses.

    The desktop render CLI requires the same five Plasma tools as the applet
    render plus its own client, ``plasmashell`` (DESKTOP_REAL_TOOLS above, the
    set the CLI's desktop preflight refuses on), so the gate skips under the
    shared software-renderer condition extended with that client -- the same
    attribute-writing shape ``dialog_gate_guard`` uses, so the skip flag is
    present (False where every tool exists and the renderer is a GPU)
    whatever the host has. The desktop mode opens no kdialog or zenity
    client, so neither belongs in its guarded set.
    """
    tools = DESKTOP_REAL_TOOLS
    reason = software_renderer_skip_reason() or (
        "needs kwin_wayland, dbus-run-session, plasmawindowed, spectacle, "
        "plasma-apply-colorscheme and plasmashell on PATH"
    )
    missing = [tool for tool in tools if shutil.which(tool) is None]

    def decorator(cls):
        cls.__unittest_skip__ = bool(missing) or software_renderer_skip_reason() is not None
        cls.__unittest_skip_why__ = reason
        return cls

    return decorator


def probe_gate_skip(guard, missing):
    """Return whether *guard* skips a probe class with *missing* off PATH.

    The skip tests reapply the real guard to disposable classes with
    ``shutil.which`` stubbed and the software-renderer condition cleared:
    never altering a real gate or starting a session while simulating
    missing tools.
    """
    def which(tool):
        return None if tool == missing else "/fake/bin/" + tool

    with (
        mock.patch.object(shutil, "which", side_effect=which),
        mock.patch.object(
            sys.modules[__name__], "software_renderer_skip_reason",
            return_value=None,
        ),
    ):
        guarded = guard()(type("Probe", (), {}))
    return guarded.__unittest_skip__


def assert_gate_skips_only_when_a_tool_is_absent(case, gate):
    """Pin one dialog gate's skip flag with the shared guard choreography.

    The dialog gate suites repeat the same two-part pin beside their gates:
    the gate must skip exactly where its render CLI refuses on tools (the
    software-renderer reason applies or one of ``DIALOG_REAL_TOOLS`` is
    absent), and reapplying the real ``dialog_gate_guard`` to a disposable
    class with each tool removed in turn must skip, while the untouched
    guard must not -- never altering a real gate or starting a session
    while simulating missing tools (see :func:`probe_gate_skip`).
    *gate* is the guarded class whose ``__unittest_skip__`` flag the pin
    asserts; *case* is the test case whose failure messages and subTests
    the pin reports through. The multi-gate pin in
    ``tests/test_render_dialog_gates.py`` and the desktop gate's variant in
    ``tests/test_render_surface.py`` keep their own shapes.
    """
    expected = software_renderer_skip_reason() is not None or not all(
        shutil.which(tool) for tool in DIALOG_REAL_TOOLS
    )
    case.assertEqual(expected, gate.__unittest_skip__)
    for missing in (None, *DIALOG_REAL_TOOLS):
        with case.subTest(missing=missing):
            case.assertEqual(
                missing is not None,
                probe_gate_skip(dialog_gate_guard, missing),
            )
