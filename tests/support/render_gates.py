"""Session plumbing the render capture gates share.

``tests/test_render_surface.py`` (the applet, desktop and splash gates),
``tests/test_render_dialog_gates.py`` (the thirteen kdialog widget gates)
and ``tests/test_render_file_dialog.py`` (the file-dialog gate) all pin
``tools/render_surface.py``'s captures. The tool lists, the software-renderer
skip condition, the pixel-reading mixin, the render session batch and the
dialog-gate scaffolding and skip guards live here so the three suites share
one copy.
"""

from __future__ import annotations

import atexit
import os
import shutil
import sys
import tempfile
from unittest import mock

from support.repo_root import ROOT
from support import process_runner  # noqa: E402  (repo_root puts the root on sys.path)
from support.kvantum_fixtures import SVG  # noqa: E402
from support.platinum_palette import hex_colour  # noqa: E402
from support.svg_case import parse_svg  # noqa: E402
from svg_assertions import render_slices  # noqa: E402
from tools.png import pixel_at, read_png  # noqa: E402

SCRIPT = str(ROOT / "tools" / "render_surface.py")


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


def software_renderer_skip_reason():
    """Return the capture gates' skip reason when Mesa is forced to software."""
    if os.environ.get("LIBGL_ALWAYS_SOFTWARE") == "1":
        return SOFTWARE_RENDER_SKIP_REASON
    for variable in ("MESA_LOADER_DRIVER_OVERRIDE", "GALLIUM_DRIVER"):
        if os.environ.get(variable, "").lower() in SOFTWARE_RENDERER_DRIVERS:
            return SOFTWARE_RENDER_SKIP_REASON
    return None


SOFTWARE_RENDER_SKIP_REASON = (
    "KWin's ScreenShot2 offscreen effect hangs on a software Mesa renderer "
    "(fixed in KWin 6.8); run on a GPU-backed host to exercise the capture gates"
)


class PixelPins:
    """Pixel-reading assertions the render gates share.

    A plain mixin: unittest discovers test methods only on the
    ``TestCase`` subclasses that mix it in, so the mixin itself never
    runs as a test. ``TestRender``, ``TestSplashRender`` and ``DialogGate``'s concrete
    subclasses inherit these helpers beside their own ``candidate_image``
    accessors.
    """

    def assert_pixel(self, x, y, colour):
        self.assertEqual(colour, hex_colour(pixel_at(self.candidate_image(), x, y)))

    def assert_raised_frame(self, rect, *, flat_rows=(), corner_blend=0):
        """Pin a raised frame's outline/bevel and optional label-free rows.

        *corner_blend* excludes the antialiased corner arc some buttons
        draw over the sharp rectangle's ends: 0 (the default, and the
        dialog buttons' shape) asserts the full outline rows and columns;
        *n* > 0 shrinks each asserted span by *n* pixels at the row ends
        and by *n* - 1 at the column ends (the arc covers one fewer row),
        leaving the blend greys to the caller's row pins.
        """
        x, y, width, height = rect
        if corner_blend:
            rows = range(x + corner_blend, x + width - corner_blend)
            columns = range(y + corner_blend, y + height - corner_blend)
        else:
            rows = range(x, x + width)
            columns = range(y + 1, y + height - 1)
        for xx in rows:
            self.assert_pixel(xx, y, "#000000")
            self.assert_pixel(xx, y + height - 1, "#000000")
        for yy in columns:
            self.assert_pixel(x, yy, "#000000")
            self.assert_pixel(x + 1, yy, "#FFFFFF")
            self.assert_pixel(x + width - 2, yy, "#AAAAAA")
            self.assert_pixel(x + width - 1, yy, "#000000")
        for row in flat_rows:
            self.assert_pixel(x + 2, row, "#DDDDDD")
            self.assert_pixel(x + width - 3, row, "#DDDDDD")

    def assert_band(self, rect, rows):
        """Pin every cell of *rect* at the per-row colours *rows*.

        A blended bevel arm, a lost outline row, a swapped arm colour, a
        resampled grip bar or a one-pixel crop slip shows up here
        immediately.
        """
        image = self.candidate_image()
        x, y, width, height = rect
        for row in range(height):
            with self.subTest(row=y + row):
                self.assertEqual(
                    list(rows[row]),
                    [
                        hex_colour(pixel_at(image, x + dx, y + row))
                        for dx in range(width)
                    ],
                )

    def assert_flat_window_face(self, rect):
        """Pin every cell of *rect* at the flat #DDDDDD window face.

        The calendar, colour and icon dialog gates each pin one
        face crop this way: the rows must show the window body colour
        column to column, so a stray glyph row, a title-bar bleed or a
        repaint of the chrome above the widget inside fails row by row.
        """
        self.assert_band(
            rect, [["#DDDDDD"] * rect[2] for _ in range(rect[3])]
        )


# The dialog render's engine-drawn widget gate: `--checkbox-dialog` opens a
# kdialog warning at the headless KWin session's centre in a 480x360 capture,
# and its dontagain check box draws the theme's `checkbox-normal` art through
# `[Session] check_size`. KWin centres the session's only window in the
# virtual framebuffer, so these crops are measured on this capture size; they
# assume the session the CLI builds for `--checkbox-dialog` (the same scratch
# config home, the applied kdeglobals defaults and the Kvantum selection).
DIALOG_WIDTH = 480
DIALOG_HEIGHT = 360

class Renders:
    """The render capture gates' sessions, started together, finished once.

    Every render sleeps its configured settle budget before it captures --
    that budget is the paint budget the gate promises, and the
    byte-compare gates must not render below it -- so serial back-to-back
    renders cost one settle budget per gate. The sessions are independent
    -- each has its own ``dbus-run-session``, scratch XDG tree (and with it
    its own ``render-surface`` socket) and capture path -- and the settle
    is a sleep rather than CPU, so starting all at once and finishing them
    together costs one budget.

    Each gate module registers the kinds its gates wait on -- the
    ``DialogGate`` subclasses through ``__init_subclass__``, the applet,
    desktop and splash gates through a module-level ``request`` call -- so
    ``ensure`` starts exactly the kinds this process needs as one batch: a
    worker process that runs one gate module renders that module's
    captures, not every kind the table lists. A gate whose skip guard
    holds never calls ``ensure``, so its kind's request never starts a
    render: on a host that merely lacks the tools, or forces a software
    renderer, no render runs at all.
    The first gate class to set up records all results;
    :func:`_remove_directories` removes every scratch directory at
    interpreter exit, so a run that reaches only some of the classes still
    cleans up behind the others.
    """
    KINDS = (
        ("applet", (), "render.png"),
        ("checkbox", ("--checkbox-dialog",), "dialog.png"),
        ("combobox", ("--combobox-dialog",), "dialog.png"),
        ("lineedit", ("--lineedit-dialog",), "dialog.png"),
        ("menu", ("--menu-dialog",), "dialog.png"),
        ("radiolist", ("--radiolist-dialog",), "dialog.png"),
        ("calendar", ("--calendar-dialog",), "dialog.png"),
        ("color", ("--color-dialog",), "dialog.png"),
        ("icon", ("--icon-dialog",), "dialog.png"),
        ("progressbar", ("--progressbar-dialog",), "dialog.png"),
        ("slider", ("--slider-dialog",), "dialog.png"),
        ("textbox", ("--textbox-dialog",), "dialog.png"),
        ("gtk", ("--gtk-dialog", "--settle", "20"), "dialog.png"),
        ("inactive", ("--inactive-dialog",), "dialog.png"),
        ("file_dialog", ("--file-dialog",), "dialog.png"),
        ("desktop", ("--desktop",), "desktop.png"),
        ("splash", ("--splash",), "splash.png"),
    )
    # A kind whose tool runs a longer internal timeout waits on that budget
    # plus margin, not the shared 150 s dialog wait: the desktop render's
    # documented timeout default is 180 s (tools/render_surface.py's
    # _DESKTOP_TIMEOUT), so finishing it at 150 s would SIGKILL a legitimate
    # slow first plasmashell start the tool itself would still have served.
    FINISH_TIMEOUTS = {"desktop": 240}
    requested: set[str] = set()
    directories: dict[str, str] = {}
    results: dict[str, tuple[str, str, int, str]] = {}
    completed = False
    failure: BaseException | None = None

    @classmethod
    def request(cls, *kinds):
        """Record the render kinds this process's gates wait on."""
        cls.requested.update(kinds)

    @classmethod
    def ensure(cls, kind):
        """Finish the requested renders once and return *kind*'s result."""
        if not cls.completed:
            cls.completed = True
            # The sweep joins before the renders start: all scratch
            # directories may already exist by the time a render fails, and
            # a failed run must still remove them at interpreter exit.
            atexit.register(cls._remove_directories)
            try:
                cls._run_all()
            except Exception as error:
                cls.failure = error
                raise
        if cls.failure is not None:
            # The sibling gate re-raises the failed run's error instead of a
            # KeyError about a result the failed run never recorded.
            raise cls.failure
        return cls.results[kind]

    @classmethod
    def _run_all(cls):
        started = {}
        for kind, flags, filename in cls.KINDS:
            if kind not in cls.requested:
                continue
            directory = tempfile.mkdtemp(prefix=f"{kind}-render-test-")
            cls.directories[kind] = directory
            started[kind] = process_runner.start(
                [sys.executable, SCRIPT, os.path.join(directory, filename), *flags],
                capture_output=True,
                text=True,
            )
        for kind, _, _ in cls.KINDS:
            if kind not in cls.requested:
                continue
            # The first finish below waits one settle budget while the
            # other two renders run alongside it.
            stdout, stderr = process_runner.finish(
                started[kind], timeout=cls.FINISH_TIMEOUTS.get(kind, 150)
            )
            cls.results[kind] = (
                stdout,
                stderr,
                started[kind].returncode,
                cls.directories[kind],
            )

    @classmethod
    def _remove_directories(cls):
        for directory in cls.directories.values():
            shutil.rmtree(directory, ignore_errors=True)


class DialogGate(PixelPins):
    """Test scaffolding the fourteen dialog render gates share.

    Each gate is a ``unittest.TestCase`` only through its concrete subclass
    (unittest discovers tests on the subclasses alone) and waits on its own
    ``Renders`` render; the gates differ in the kind key they wait
    on, in the shipped slice and cell geometry they byte-compare and in the
    extra widget-specific tests their modules add.
    """

    KIND: str

    def __init_subclass__(cls, **kwargs):
        # Register the kind this concrete gate waits on at class-definition
        # (import) time, so the first gate class to set up can start every
        # kind this process needs as one batch (see Renders). A gate whose
        # skip guard holds never calls ensure, so its registration never
        # starts a render.
        super().__init_subclass__(**kwargs)
        Renders.request(cls.KIND)

    @classmethod
    def setUpClass(cls):
        # All renders run concurrently (see Renders); this class
        # waits for its own and leaves its siblings' to their own classes.
        cls.stdout, cls.stderr, cls.returncode, cls.directory = (
            Renders.ensure(cls.KIND)
        )
        cls.output = os.path.join(cls.directory, "dialog.png")
        cls._candidate = None

    @classmethod
    def candidate_image(cls):
        """Return the dialog render decoded once, reused by every read below."""
        if cls._candidate is None:
            cls._candidate = read_png(cls.output)
        return cls._candidate

    def test_exits_zero(self):
        self.assertEqual(0, self.returncode, self.stderr)

    def test_writes_a_480x360_png(self):
        image = self.candidate_image()
        self.assertEqual((DIALOG_WIDTH, DIALOG_HEIGHT), (image.width, image.height))

    def assert_cell_matches(self, slice_name, cell):
        """Byte-compare the engine-drawn cell at *cell* with the shipped art.

        The expected pixels are the named shipped slice itself, at its canvas
        size, re-derived from the same SVG the Kvantum reference suites use:
        the engine may neither resample the art nor fill the cell from a
        foreign element.
        """
        expected = dict(render_slices(parse_svg(SVG))[slice_name])
        x0, y0, width, height = cell
        actual = {
            (x, y): hex_colour(
                pixel_at(self.candidate_image(), x0 + x, y0 + y)
            )
            for x in range(width)
            for y in range(height)
        }
        self.assertEqual(expected, actual)

    def assert_push_button_recipe(self, rect, cell, flat_rows):
        """Pin the raised push-button recipe over its full-height cell.

        The engine's raised button recipe is one contract, so its outline,
        bevel arms, face rows and shadow arm are asserted here and both
        gates that pin a push button walk their own rect and cell through
        it (the color and icon dialog gates below).
        """
        self.assert_raised_frame(rect, flat_rows=flat_rows)
        face_row = [
            "#FFFFFF",
            *["#DDDDDD"] * 4,
        ]
        arm_row = [
            "#FFFFFF",
            *["#AAAAAA"] * 4,
        ]
        rows = (
            [["#000000"] * 5]
            + [["#FFFFFF"] * 5]
            + [face_row] * 20
            + [arm_row]
            + [["#000000"] * 5]
        )
        self.assert_band(cell, rows)

    def assert_push_button_face_reaches_its_row(self, rect):
        """Pin the raised recipe's flat face across its label-free row.

        The raised recipe's flat face must reach the whole label-free
        row: a rounded stock face, a duplicated or shifted bevel arm or
        a recoloured face fails on the row's columns. Shared with
        ``assert_push_button_recipe`` by the color and icon dialog gates.
        """
        image = self.candidate_image()
        x, y, width, height = rect
        self.assertEqual(
            ["#DDDDDD"] * (width - 4),
            [hex_colour(pixel_at(image, x + 2 + dx, y + height - 4))
             for dx in range(width - 4)],
        )


def dialog_gate_guard():
    """Return the skip guard the fourteen dialog render gates share.

    The dialog render CLI needs the same five Plasma tools as the applet
    render plus the client its requested mode opens (it exits 2 with a
    missing-tool diagnostic when one is absent: kdialog for the thirteen
    kdialog modes, zenity for the GTK mode), so the fourteen dialog gates skip
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
