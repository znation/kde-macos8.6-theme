"""Session plumbing the render capture gates share.

``tests/test_render_surface.py`` (the applet and desktop gates),
``tests/test_render_splash_gate.py`` (the splash gate),
``tests/test_render_dialog_gates.py`` (the thirteen kdialog widget gates),
``tests/test_render_calendar_dialog.py`` (the two calendar gates),
``tests/test_render_file_dialog.py`` (the file-dialog gate) and
``tests/test_render_gtk_dialog.py`` (the GTK 4 window gate) all pin
``tools/render_surface.py``'s captures. The tool lists, the software-renderer
skip condition, the pixel-reading mixin, the render session batch and the
dialog-gate scaffolding and skip guards live here so the three suites share
one copy.
"""

from __future__ import annotations

import atexit
import os
from collections import Counter
import shutil
import sys
import tempfile
import time
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


# How many trailing stderr lines a band mismatch quotes: enough for the
# render's last messages, short enough to read in a failure report.
BAND_TAIL_LINES = 12


def band_mismatch_context(colours, stderr):
    """Return the failure context that names a band's cause.

    *colours* is every cell colour of the band, row by row, and *stderr* the
    render's stderr. A first-cell mismatch (a desktop-face ``#CCCCCC`` where a
    dialog pixel belongs means the capture ran before the dialog mapped) does
    not name that cause by itself, so this quotes the band's distinct colours
    with their cell counts and the last :data:`BAND_TAIL_LINES` non-blank
    stderr lines, or says the render printed nothing.
    """
    counts = Counter(colours)
    summary = " ".join(f"{colour}:{counts[colour]}" for colour in sorted(counts))
    lines = [line for line in (stderr or "").splitlines() if line.strip()]
    if lines:
        render = "render stderr tail:\n" + "\n".join(lines[-BAND_TAIL_LINES:])
    else:
        render = "render printed no stderr"
    return f"whole band colours: {summary}\n{render}"


def first_differing_pixel_note(x, y, expected, observed):
    """Return the failing band row's first differing cell as a note line.

    *x*/*y* are the band's top-left capture coordinates and *expected*/*observed*
    the row's colour lists; the note names the first differing cell's absolute
    capture coordinates beside both hex colours, so a mismatch points at a
    pixel instead of only a row. A matching row (a length mismatch fails on
    the list comparison itself) adds nothing.
    """
    for offset, (want, got) in enumerate(zip(expected, observed)):
        if want != got:
            return (
                f"\nfirst differing pixel ({x + offset}, {y}): "
                f"expected {want}, observed {got}"
            )
    return ""


def _stream_text(part):
    """Return an exception's partial stream output as text, or ``""``.

    ``support.process_runner.finish`` attaches the drained pipes as text
    (the batch starts every render with ``text=True``), so *part* is
    normally ``None`` or ``str``; a ``bytes`` decode keeps a non-text
    exception's output quotable too.
    """
    if part is None:
        return ""
    if isinstance(part, bytes):
        return part.decode("utf-8", errors="replace")
    return part


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
        # The coordinates ride in the failure message (after the standard
        # ``'expected' != 'observed'`` text) so a mismatch names the pixel.
        self.assertEqual(
            colour,
            hex_colour(pixel_at(self.candidate_image(), x, y)),
            f"pixel ({x}, {y})",
        )

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
        immediately. Each mismatch also carries :func:`band_mismatch_context`
        so a failure names the band's whole colour set and the render's
        stderr, not only the first cell that differed, and
        :func:`first_differing_pixel_note` names that cell's absolute capture
        coordinates beside both colours at the call site below.
        """
        image = self.candidate_image()
        x, y, width, height = rect
        band = [
            hex_colour(pixel_at(image, x + dx, y + row))
            for row in range(height)
            for dx in range(width)
        ]
        context = band_mismatch_context(band, getattr(self, "stderr", ""))
        for row in range(height):
            expected = list(rows[row])
            observed = band[row * width:(row + 1) * width]
            with self.subTest(row=y + row):
                self.assertEqual(
                    expected,
                    observed,
                    context + first_differing_pixel_note(x, y + row, expected, observed),
                )

    def candidate_colour_map(self, rect):
        """Return *rect*'s candidate pixels as a rect-relative colour map.

        The byte-compare gates re-derive an expected ``{(x, y): "#RRGGBB"}``
        map keyed from the rect's top-left and compare it with the capture;
        the seven call sites (the GTK window gate's four cell pins, the
        file-dialog gate's ``assert_box_matches_svg``, the checkbox gate's
        close-box pin and :meth:`DialogGate.assert_cell_matches`) build the
        actual side here so their key schemes cannot drift apart.
        """
        image = self.candidate_image()
        x0, y0, width, height = rect
        return {
            (x, y): hex_colour(pixel_at(image, x0 + x, y0 + y))
            for x in range(width)
            for y in range(height)
        }

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

    def assert_inks_off_the_face(self, x0, y0, x1, y1, message):
        """Assert the inclusive rect draws at least one pixel off the face.

        The live-ink probe the app-drawn label, caption and mark pins
        share (9 call sites in tests/test_render_file_dialog.py): the
        glyphs themselves stay unpinned, but a band that drew nothing
        over the flat #DDDDDD face fails here. The rectangle is
        inclusive on all four edges, the form the measured band
        constants already carry.
        """
        image = self.candidate_image()
        self.assertTrue(
            any(
                hex_colour(pixel_at(image, x, y)) != "#DDDDDD"
                for x in range(x0, x1 + 1)
                for y in range(y0, y1 + 1)
            ),
            message,
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
        ("combobox", ("--combobox-dialog", "--settle", "20"), "dialog.png"),
        ("lineedit", ("--lineedit-dialog",), "dialog.png"),
        ("menu", ("--menu-dialog",), "dialog.png"),
        ("radiolist", ("--radiolist-dialog",), "dialog.png"),
        ("calendar", ("--calendar-dialog",), "dialog.png"),
        ("calendar_locale", ("--calendar-dialog",), "dialog.png"),
        ("color", ("--color-dialog",), "dialog.png"),
        ("icon", ("--icon-dialog", "--settle", "20"), "dialog.png"),
        ("progressbar", ("--progressbar-dialog",), "dialog.png"),
        ("slider", ("--slider-dialog",), "dialog.png"),
        ("textbox", ("--textbox-dialog",), "dialog.png"),
        ("gtk", ("--gtk-dialog", "--settle", "20"), "dialog.png"),
        ("inactive", ("--inactive-dialog", "--settle", "45"), "dialog.png"),
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
    # A kind whose render must start from a caller the gate pins itself
    # rather than this process's environment: the calendar-locale render
    # starts under a Monday-first caller locale, so a scratch session that
    # leaks the caller's LANG/LC_* (a Monday-first day grid the calendar
    # pins do not describe) fails that gate instead of on a user's shell.
    # Every other kind inherits this process's environment unchanged.
    HOSTILE_ENVIRONMENTS = {
        "calendar_locale": {
            "LANG": "de_DE.UTF-8",
            "LC_ALL": "de_DE.UTF-8",
            "LANGUAGE": "de",
        },
    }
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
            hostile = cls.HOSTILE_ENVIRONMENTS.get(kind)
            environment = dict(os.environ, **hostile) if hostile else None
            started[kind] = process_runner.start(
                [sys.executable, SCRIPT, os.path.join(directory, filename), *flags],
                capture_output=True,
                text=True,
                env=environment,
            )
        for kind, _, filename in cls.KINDS:
            if kind not in cls.requested:
                continue
            # The first finish below waits one settle budget while the
            # other two renders run alongside it.
            try:
                stdout, stderr = process_runner.finish(
                    started[kind], timeout=cls.FINISH_TIMEOUTS.get(kind, 150)
                )
            except Exception as error:
                raise cls._finish_failure(kind, filename, error) from error
            cls.results[kind] = (
                stdout,
                stderr,
                started[kind].returncode,
                cls.directories[kind],
            )

    @classmethod
    def _finish_failure(cls, kind, filename, error):
        """Return the attributable failure for a finish of *kind* that raised.

        An exception from ``process_runner.finish`` -- the
        ``subprocess.TimeoutExpired`` of a hung render, or any other failure
        -- reaches :meth:`ensure` with no kind name and no output, so every
        sibling gate re-raises the same unattributable error. The
        replacement names the kind and its capture path and quotes the
        partial output the exception carries (``output``/``stderr``, which
        ``support.process_runner.finish`` attaches), so a recurrence records
        its cause by itself, and the capture the kind already wrote is
        preserved outside the scratch tree the exit sweep removes (or the
        message says the render wrote no capture).
        """
        capture = os.path.join(cls.directories[kind], filename)
        message = (
            f"the {kind} render failed while the batch finished it "
            f"(capture {capture})"
        )
        note = render_output_note(
            _stream_text(getattr(error, "output", None)),
            _stream_text(getattr(error, "stderr", None)),
        )
        if note:
            message = f"{message}\n{note}"
        preserved = preserve_capture(kind, cls.directories[kind], filename)
        if preserved is None:
            message = f"{message}\nthe render wrote no capture"
        else:
            message = f"{message}\ncapture preserved at {preserved}"
        return RuntimeError(message)

    @classmethod
    def _remove_directories(cls):
        for directory in cls.directories.values():
            shutil.rmtree(directory, ignore_errors=True)


def render_output_note(stdout, stderr):
    """Return the render's own output as a failure-message note, or ``""``.

    A passing render's stdout carries its session log tail, so a pixel
    mismatch shows which settle path ran; an empty output adds nothing.
    """
    parts = [part.rstrip("\n") for part in (stdout, stderr) if part and part.strip()]
    if not parts:
        return ""
    return "render output:\n" + "\n".join(parts)


# Where a failed gate's capture survives the scratch-tree sweep: the
# diagnostics root sits outside every scratch directory the batch's exit
# sweep removes, and keeping only the newest timestamped directories bounds
# the space parallel workers and repeated runs spend on captures.
DIAGNOSTICS_DIRECTORY = "platinum-render-diagnostics"
DIAGNOSTIC_DIRECTORIES_KEPT = 8


def diagnostics_root():
    """Return the capture-diagnostics root under this run's ``TMPDIR``."""
    return os.path.join(os.environ.get("TMPDIR", "/tmp"), DIAGNOSTICS_DIRECTORY)


def preserve_capture(kind, directory, filename):
    """Copy the capture at *directory*/*filename* into the diagnostics root.

    The scratch tree is removed at interpreter exit, so a gate failure's
    capture would vanish with it; this copies the PNG byte for byte into
    ``<TMPDIR>/platinum-render-diagnostics/<UTC timestamp>-<pid>-<kind>/``
    under the capture's own filename and returns the copy's path. A ``None``
    return is itself a diagnostic the quarantined gate entries ask for: a
    finished render with no capture says the capture never happened. The
    diagnostics root is pruned to its newest
    :data:`DIAGNOSTIC_DIRECTORIES_KEPT` timestamped directories, and no copy
    or prune error may mask the gate's own failure, so every fault here
    falls back to ``None``.
    """
    try:
        capture = os.path.join(directory, filename)
        if not os.path.isfile(capture):
            return None
        root = diagnostics_root()
        stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
        target_directory = os.path.join(root, f"{stamp}-{os.getpid()}-{kind}")
        os.makedirs(target_directory, exist_ok=True)
        target = os.path.join(target_directory, filename)
        shutil.copyfile(capture, target)
        _prune_diagnostics(root)
        return target
    except Exception:
        return None


def _prune_diagnostics(root):
    """Remove every diagnostics directory but the newest kept count."""
    names = sorted(os.listdir(root))
    for name in names[:-DIAGNOSTIC_DIRECTORIES_KEPT]:
        shutil.rmtree(os.path.join(root, name), ignore_errors=True)


class DiagnosticsRootSteering:
    """Give a preservation probe a diagnostics root only it can reach.

    The four test classes that drive :func:`preserve_capture` directly
    (three in ``test_render_gate_messages`` and the finish-failure class in
    ``test_render_gates_batch``) steer the root into a scratch parent by
    pointing ``TMPDIR`` at it, so pruning assertions see only directories
    the probe seeded and a concurrent run's live diagnostics directory is
    never touched. Mix it in before ``unittest.TestCase`` and start the
    subclass's ``setUp`` with ``super().setUp()``; the probe then reads
    :attr:`root` (the path :func:`diagnostics_root` returns).
    """

    def setUp(self):
        parent = tempfile.mkdtemp(prefix="preservation-root-")
        self.addCleanup(shutil.rmtree, parent, ignore_errors=True)
        patcher = mock.patch.dict(os.environ, {"TMPDIR": parent})
        patcher.start()
        self.addCleanup(patcher.stop)
        self.root = diagnostics_root()


class RenderOutputMessages:
    """Append the render's own output to every pixel assertion's failure.

    A pixel assertion passes no message, so the render's stdout and stderr
    join the mismatch: a recurrence then names the settle path that ran
    instead of a bare colour pair. An explicit message is kept as given, and
    every failure additionally names the preserved capture's path (or says
    the render wrote no capture) through :meth:`capture_preservation_note`.
    The mixin reads ``stdout`` and ``stderr`` from the gate's ``setUpClass``.
    """

    def assertEqual(self, first, second, msg=None):
        if msg is None:
            msg = render_output_note(self.stdout, self.stderr) or None
        try:
            super().assertEqual(first, second, msg)
        except AssertionError as error:
            note = self.capture_preservation_note()
            if note:
                # unittest builds the ``msg`` argument eagerly even for
                # passing assertions, so the preservation must happen here,
                # in the failure path only; the note is spliced into the
                # caught error instead of a re-raise with a new traceback.
                error.args = (f"{error}\n{note}",)
            raise

    def capture_preservation_note(self):
        """Preserve this gate's capture on a failure and return the note line.

        A gate without a ``directory`` -- the plain message probes -- adds
        nothing. The capture's filename comes from the gate's ``output``
        when it sets one (the dialog gates' ``dialog.png``) and defaults to
        the dialog capture otherwise, and the kind label from the gate's
        ``KIND`` when it has one.
        """
        directory = getattr(self, "directory", None)
        if directory is None:
            return ""
        filename = os.path.basename(
            getattr(self, "output", "") or os.path.join(directory, "dialog.png")
        )
        preserved = preserve_capture(getattr(self, "KIND", "gate"), directory, filename)
        if preserved is None:
            return "the render wrote no capture"
        return f"capture preserved at {preserved}"


class DialogGate(RenderOutputMessages, PixelPins):
    """Test scaffolding the fifteen dialog render gates share.

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
        # The failure message is built from both streams: a failed render's
        # session-log tail lands on stdout and may print nothing on stderr,
        # so quoting stderr alone would report a bare ``0 != 1``.
        self.assertEqual(
            0,
            self.returncode,
            render_output_note(self.stdout, self.stderr) or None,
        )

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
        self.assertEqual(expected, self.candidate_colour_map(cell))

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
