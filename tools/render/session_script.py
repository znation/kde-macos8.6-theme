"""Build the shell script that runs a render session."""

from __future__ import annotations

import shlex

try:
    from tools.render.settle_scripts import READINESS_INTERFACE, READINESS_MEMBER
except ImportError:  # imported from a directly run tool
    from render.settle_scripts import READINESS_INTERFACE, READINESS_MEMBER

COLOR_SCHEME = "MacOS8"
CLIENT_EXITED_DURING_CAPTURE = "render-session: client exited during the capture"


def _prologue(focus: str, readiness: str, report: str | None = None) -> str:
    report_part = f"report={report}; " if report else ""
    return (
        "export QT_QPA_PLATFORM=wayland; "
        f"plasma-apply-colorscheme {COLOR_SCHEME} || exit 1; "
        'settle="$1"; capture="$2"; shift 2; '
        f"focus={focus}; readiness={readiness}; {report_part}"
    )


def _readiness_listener(readiness: str = "readiness") -> str:
    return (
        'ceiling="$capture.ceiling"; ready="$capture.ready"; '
        'rm -f "$ceiling" "$ready"; export RENDER_SESSION_READY_FILE="$ready"; '
        'listener=""; monitor_pid=""; events="$capture.events"; '
        f'if [ -n "${readiness}" ]; then '
        'monitor="$(command -v dbus-monitor)"; '
        'qdbus="$(command -v qdbus6 || command -v qdbus)"; '
        'if [ -z "$monitor" ]; then echo "render-session: no dbus-monitor for client readiness" >&2; '
        'elif [ -z "$qdbus" ]; then echo "render-session: no qdbus for client readiness" >&2; '
        'else '
        'rm -f "$events"; '
        'if ! mkfifo "$events"; then echo "render-session: cannot create readiness listener pipe" >&2; '
        'else '
        f"\"$monitor\" --session \"type='method_call',interface='{READINESS_INTERFACE}',member='{READINESS_MEMBER}'\" >\"$events\" & monitor_pid=$!; "
        '(while IFS= read -r line; do case "$line" in *member=ClientReady*) '
        'printf "%s\\n" dbus-window-added >"$ready"; break;; esac; done <"$events") & listener=$!; '
        'id=$("$qdbus" org.kde.KWin /Scripting org.kde.kwin.Scripting.loadScript "$readiness" 2>/dev/null); '
        'case "$id" in ""|*[!0-9]*) echo "render-session: the readiness settle script did not load" >&2;; '
        '*) "$qdbus" org.kde.KWin "/Scripting/Script$id" run >/dev/null 2>&1 || '
        'echo "render-session: the readiness settle script did not run" >&2;; esac; fi; fi; fi; '
    )


def _client_start() -> str:
    return (
        'started=$(date +%s%3N); "$@" & client=$!; '
        'export RENDER_SESSION_CLIENT_PID="$client"; '
        'echo "render-session: client started at $started" >&2; '
    )


def _focus_settle(focus: str = "focus") -> str:
    return (
        f'if [ -n "${focus}" ]; then '
        'qdbus="$(command -v qdbus6 || command -v qdbus)"; '
        'if [ -n "$qdbus" ]; then '
        'id=$("$qdbus" org.kde.KWin /Scripting '
        'org.kde.kwin.Scripting.loadScript "$focus" 2>/dev/null); '
        'case "$id" in ""|*[!0-9]*) '
        'echo "render-session: the focus settle script did not load" >&2;; '
        '*) (while [ ! -e "$focus.done" ]; do '
        '"$qdbus" org.kde.KWin "/Scripting/Script$id" run >/dev/null 2>&1; '
        'command sleep 0.25; done) & settle_loop=$!; '
        'echo "render-session: focus settle loop running (script $id)" >&2;; '
        'esac; '
        'else echo "render-session: no qdbus for the focus settle" >&2; fi; fi; '
    )


def _settle_wait() -> str:
    return (
        '( command sleep "$settle"; touch "$ceiling" ) & ceiling_timer=$!; '
        'while [ ! -e "$ready" ] && [ ! -e "$ceiling" ]; do '
        'command sleep 0.1; done; '
        'if [ -n "$monitor_pid" ]; then kill "$monitor_pid" 2>/dev/null; wait "$monitor_pid" 2>/dev/null; fi; '
        'if [ -n "$listener" ]; then kill "$listener" 2>/dev/null; wait "$listener" 2>/dev/null; fi; '
        'rm -f "$events"; '
        'ready_source=""; if [ -e "$ready" ]; then IFS= read -r ready_source <"$ready" || :; fi; '
        'if [ "$ready_source" = dbus-window-added ]; then '
        'grace=0; while [ "$grace" -lt 10 ] && [ ! -e "$ceiling" ]; do '
        'command sleep 0.1; grace=$((grace + 1)); done; fi; '
        'kill "$ceiling_timer" 2>/dev/null; wait "$ceiling_timer" 2>/dev/null; '
        'rm -f "$ceiling"; '
        'if [ -e "$ready" ]; then echo "render-session: client ready at $(date +%s%3N)" >&2; '
        'else echo "render-session: settle ceiling reached before a client ready file" >&2; fi; '
        'echo "render-session: settle done at $(date +%s%3N)" >&2; '
        'if ! kill -0 "$client" 2>/dev/null; then '
        'echo "$1 exited before the capture" >&2; exit 1; fi; '
    )


def _window_report(report: str = "report") -> str:
    return (
        'qdbus="$(command -v qdbus6 || command -v qdbus)"; '
        'if [ -n "$qdbus" ]; then '
        'id=$("$qdbus" org.kde.KWin /Scripting '
        'org.kde.kwin.Scripting.loadScript "$report" 2>/dev/null); '
        'case "$id" in ""|*[!0-9]*) '
        'echo "render-session: the window report script did not load" >&2;; '
        '*) "$qdbus" org.kde.KWin "/Scripting/Script$id" run >/dev/null 2>&1;; '
        'esac; '
        'else echo "render-session: no qdbus for the window report" >&2; fi; '
    )


def _capture_and_terminate(focus: str = "focus") -> str:
    return (
        'if kill -STOP "$client" 2>/dev/null; then '
        'echo "render-session: client held at $(date +%s%3N)" >&2; fi; '
        'echo "render-session: capturing at $(date +%s%3N)" >&2; '
        'spectacle -b -n -f -o "$capture"; status=$?; '
        'capture_done=$(date +%s%3N); '
        'echo "render-session: capture status $status at $capture_done" >&2; '
        'if [ -n "${settle_loop:-}" ]; then '
        f'touch "${focus}.done"; '
        'kill "$settle_loop" 2>/dev/null; wait "$settle_loop" 2>/dev/null; fi; '
        'if kill -0 "$client" 2>/dev/null; then '
        'echo "render-session: client alive after the capture at $capture_done" >&2; '
        'else '
        f'echo "{CLIENT_EXITED_DURING_CAPTURE} at $capture_done" >&2; fi; '
        'kill -CONT "$client" 2>/dev/null; '
        'resumed=0; while [ "$resumed" -lt 50 ]; do '
        'state=$(sed \'s/.*) //; s/ .*//\' "/proc/$client/stat" 2>/dev/null); '
        '[ "$state" != T ] && break; '
        # `command sleep` keeps the wait on the real binary: the session
        # environment inherits the caller's, so an exported `sleep` function
        # would otherwise shadow these waits as it would the settle stages'.
        'command sleep 0.1; resumed=$((resumed + 1)); done; '
        'kill "$client" 2>/dev/null; '
        'waited=0; '
        'while kill -0 "$client" 2>/dev/null && [ "$waited" -lt 50 ]; do '
        'command sleep 0.1; waited=$((waited + 1)); done; '
        'kill -9 "$client" 2>/dev/null; '
        'wait "$client" 2>/dev/null; '
        'echo "render-session: client reaped" >&2; '
        'exit $status'
    )


def session_script(
    focus_script: str | None = None,
    readiness_script: str | None = None,
    window_report_script: str | None = None,
) -> str:
    """Return the ``sh -c`` script that opens the client, settles and captures.

    The positional parameters are the settle seconds, the capture path and
    the client argv itself, so ``sh`` receives them after the script and
    never parses them as shell syntax: the client words are passed through
    ``shlex``-joined child ``sh -c`` argv, each a separate positional word
    of this script. The script fails the session if the backgrounded
    client is no longer running after the settle; without that check
    ``spectacle`` would still publish a capture of an empty session.

    *focus_script* is the scratch path of a KWin settle script (the
    inactive-dialog render passes one, the other modes ``None``): when it
    is set, the shell loads it into KWin right after the client starts and
    re-runs it in a bounded background loop until the capture has
    returned, so the two-window pair's focus state is settled by
    re-activation before the frame is read, not left to the window
    manager's newest-window race (see
    ``tools/render/settle_scripts.py::focus_settle_text``). The loop's
    ``qdbus6``/``qdbus`` fallback is resolved inside the session: a host
    without either only logs the omission and keeps the older race.
    With no script given the whole block is inert (an empty ``$focus``
    fails its guard), so the other modes' session stages are unchanged.

    *readiness_script* is a KWin script path used with the session D-Bus
    monitor: when an eligible window maps (for the inactive-dialog pair,
    when both titled windows are in their settled focus state), the
    listener writes ``RENDER_SESSION_READY_FILE`` and ends the settle
    early. The listener
    starts before the render client so a fast window cannot beat the signal
    subscription.

    *window_report_script* is a one-shot KWin script path: after the settle
    ends and before the capture starts, the session loads it into KWin and
    runs it once, so its ``print`` lines in the session log are the
    capture-time window report -- one line per listed window with its
    caption, active state and kind (see
    ``tools/render/settle_scripts.py::window_report_text``). A host without
    ``qdbus`` only logs the omission and the capture proceeds unchanged.
    With no path given the stage is not joined at all, so the earlier
    callers' session text is byte-identical.

    Missing tools or a client that never maps retain the settle ceiling.
    D-Bus readiness includes up to one second of paint grace before capture,
    bounded by the settle ceiling.

    Every stage logs a millisecond timestamp, so a failed capture's log
    shows the client's start, the settle's end and the capture's span on
    one wall clock. After the capture returns, the script records whether
    the client was still running: a client that died between the settle's
    liveness check and the capture's end took its window with it, and its
    timestamped exit marker is what lets the black-capture diagnosis
    distinguish a vanished client from a window that never painted.

    The client that passed the liveness check is frozen with SIGSTOP
    before the capture starts and resumed with SIGCONT immediately before
    the post-capture termination: Spectacle's startup latency is unbounded
    under concurrent renders, while a client such as ``ksplashqml --test``
    has a finite lifetime, so an unfrozen client could take its window
    down mid-capture. A stopped client keeps its last-painted buffer —
    the compositor captures from it — and the aliveness check after the
    capture still reads it (a stopped process answers ``kill -0``), so
    the diagnosis and the ``kill -9`` fallback are unchanged. The shell
    also exports the client's pid as ``RENDER_SESSION_CLIENT_PID``: a
    capture-side helper can only target the client through a pid the
    session shell owns, because the freeze can land before the client's
    first instruction and a pidfile the client was meant to write then
    never appears."""
    focus = shlex.quote(focus_script) if focus_script is not None else '""'
    readiness = shlex.quote(readiness_script) if readiness_script is not None else '""'
    report = (
        shlex.quote(window_report_script)
        if window_report_script is not None else None
    )
    return "".join((
        _prologue(focus, readiness, report),
        _readiness_listener("readiness"),
        _client_start(),
        _focus_settle("focus"),
        _settle_wait(),
        # Unlike the focus and readiness stages, whose inert guards are part
        # of the pre-split fixture bytes, the report stage is joined only
        # when a caller passes a script: the four fixture combinations must
        # keep their byte-identical text.
        *(() if report is None else (_window_report("report"),)),
        _capture_and_terminate("focus"),
    ))
