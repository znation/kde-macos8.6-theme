"""Resolve the session-bus address the apply tools hand to their children.

``make apply`` may run from a non-login shell (the local ``post-commit`` hook,
for example) that carries neither ``DBUS_SESSION_BUS_ADDRESS`` nor a login
environment. The Plasma selection tools need the
running session's bus, so the address is defaulted from the runtime directory
when it is unset or empty. Keeping the rule here gives the selection tools a
consistent socket address.
"""

from __future__ import annotations

import os
from pathlib import Path

# Characters the D-Bus address grammar reserves as its own syntax inside a
# transport argument's value: ``%`` introduces the %HH escape, ``;``
# separates the address list's entries, ``,`' separates one entry's
# key=value pairs and ``=`` separates a key from its value. Left raw in a
# composed ``unix:path=`` value, a runtime directory carrying any of them
# truncates the path or splits the address, so the session tools reach the
# wrong socket or none; each becomes its uppercase percent escape instead,
# which every reader of ``DBUS_SESSION_BUS_ADDRESS`` decodes back to the
# same byte. A path holding none of them is returned unchanged.
_ADDRESS_SYNTAX = {"%": "%25", ";": "%3B", ",": "%2C", "=": "%3D"}


def _escape_address_value(value: str) -> str:
    """Return *value* with the D-Bus address syntax characters %-encoded."""
    return "".join(_ADDRESS_SYNTAX.get(char, char) for char in value)


def session_env(environ: dict[str, str]) -> dict[str, str]:
    """Return *environ* with the session-bus address defaulted if needed.

    When ``DBUS_SESSION_BUS_ADDRESS`` is unset or empty, ``XDG_RUNTIME_DIR``
    is absolute, and ``$XDG_RUNTIME_DIR/bus`` exists, point the variable at
    that socket so the session tools can reach the running session. Otherwise
    the environment is returned unchanged. An empty address names no bus, so
    it is defaulted like an unset one. The composed value percent-encodes
    the address grammar's own characters in the socket path (see
    :func:`_escape_address_value`); a caller-supplied
    ``DBUS_SESSION_BUS_ADDRESS`` is never rewritten.
    """
    env = dict(environ)
    if env.get("DBUS_SESSION_BUS_ADDRESS"):
        return env
    runtime = env.get("XDG_RUNTIME_DIR", "")
    if os.path.isabs(runtime):
        bus = Path(runtime) / "bus"
        if bus.exists():
            env["DBUS_SESSION_BUS_ADDRESS"] = (
                f"unix:path={_escape_address_value(str(bus))}"
            )
    return env
