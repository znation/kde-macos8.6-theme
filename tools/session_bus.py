"""Resolve the session-bus address the apply tools hand to their children.

``make apply`` may run from a non-login shell (the local ``post-commit`` hook,
for example) that carries neither ``DBUS_SESSION_BUS_ADDRESS`` nor a login
environment. The Plasma selection tools and the keyboard reload need the
running session's bus, so the address is defaulted from the runtime directory
when it is unset or empty. Keeping the rule here means ``apply_theme`` and
``apply_keymap`` cannot disagree about which socket they address.
"""

from __future__ import annotations

import os
from pathlib import Path


def session_env(environ: dict[str, str]) -> dict[str, str]:
    """Return *environ* with the session-bus address defaulted if needed.

    When ``DBUS_SESSION_BUS_ADDRESS`` is unset or empty, ``XDG_RUNTIME_DIR``
    is absolute, and ``$XDG_RUNTIME_DIR/bus`` exists, point the variable at
    that socket so the session tools can reach the running session. Otherwise
    the environment is returned unchanged. An empty address names no bus, so
    it is defaulted like an unset one.
    """
    env = dict(environ)
    if env.get("DBUS_SESSION_BUS_ADDRESS"):
        return env
    runtime = env.get("XDG_RUNTIME_DIR", "")
    if os.path.isabs(runtime):
        bus = Path(runtime) / "bus"
        if bus.exists():
            env["DBUS_SESSION_BUS_ADDRESS"] = f"unix:path={bus}"
    return env
