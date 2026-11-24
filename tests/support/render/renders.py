"""The render session batch the render capture gates share.

Every gate waits on its kind's render through :class:`Renders`, which starts
the requested sessions as one concurrent batch and finishes them together.
The skip guards, the pixel-reading mixin, the capture diagnostics and the
dialog-gate scaffolding live in the sibling modules (``skip_guards.py``,
``pixel_pins.py``, ``capture_diagnostics.py`` and ``gates.py``).
"""

from __future__ import annotations

import atexit
import os
import shutil
import sys
import tempfile

from support.repo_root import ROOT
from support import process_runner  # noqa: E402  (repo_root puts the root on sys.path)
from support.render.capture_diagnostics import preserve_capture  # noqa: E402

SCRIPT = str(ROOT / "tools" / "render_surface.py")


def render_output_note(stdout, stderr):
    """Return the render's own output as a failure-message note, or ``""``.

    A passing render's stdout carries its session log tail, so a pixel
    mismatch shows which settle path ran; an empty output adds nothing.
    """
    parts = [part.rstrip("\n") for part in (stdout, stderr) if part and part.strip()]
    if not parts:
        return ""
    return "render output:\n" + "\n".join(parts)


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


class FreshRendersState:
    """Swap the ``Renders`` class state for a fresh table, and restore it.

    ``Renders`` keeps its bookkeeping as class state shared with the real
    gates, so a test that drives the batch must swap in a fresh table for
    the pinned assertions to hold whatever ran before it in the same
    process, and restore the saved table afterwards. Call
    :meth:`swap_renders_state_in` where the old code saved and reset (a
    ``setUp``, or the top of a test) and :meth:`swap_renders_state_back`
    where it restored (the ``tearDown``, or the ``finally``); the back
    swap sweeps the fresh table's scratch directories first, or every run
    leaks them into the temp dir.
    """

    _RENDERS_FIELDS = (
        "requested",
        "directories",
        "results",
        "completed",
        "failure",
    )

    def swap_renders_state_in(self):
        """Save the shared bookkeeping and reset it to a fresh table."""
        self._saved_renders_state = tuple(
            getattr(Renders, name) for name in self._RENDERS_FIELDS
        )
        Renders.requested = set()
        Renders.directories = {}
        Renders.results = {}
        Renders.completed = False
        Renders.failure = None

    def swap_renders_state_back(self):
        """Sweep the fresh table's directories, restore the saved state."""
        Renders._remove_directories()
        for name, value in zip(self._RENDERS_FIELDS, self._saved_renders_state):
            setattr(Renders, name, value)
