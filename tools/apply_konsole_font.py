"""Write the theme's fixed-width font into Konsole's default profile.

``apply_theme`` selects JetBrains Mono for KDE's fixed-width role in
``kdeglobals``, but a Konsole profile carries its own ``[Appearance] Font``
that overrides the system fixed font in every new Konsole session, so the
selection never reaches a terminal whose profile names a face of its own.
This helper, called from :func:`tools.apply_theme._apply` after the required
Plasma selections and under the same data-home lock, points Konsole's
default profile at the packaged face:

- it reads ``[Desktop Entry] DefaultProfile`` from ``konsolerc`` with
  ``kreadconfig6``;
- an unset value gets a new ``konsole/Platinum.profile`` under the data
  home -- ``[General] Name=Platinum`` and ``Parent=FALLBACK/``, Konsole's
  built-in fallback profile the new one inherits everything from, plus the
  font -- and ``konsolerc`` then names that file;
- an explicitly named profile is resolved through the XDG data search path:
  ``konsole/`` under the data home, then under each absolute
  ``XDG_DATA_DIRS`` entry. A profile in the user's data home is edited in
  place; a profile in a system data directory is first copied into the
  user's ``konsole/`` directory under the same basename -- Konsole reads the
  data home first, so the copy is the profile new sessions load -- and the
  copy is edited. The system source is never modified.

Only ``[Appearance] Font`` is written into a profile, and only through
``kwriteconfig6``, so every other key -- the profile's name, its shell,
colors, shortcuts and keyboard mappings -- survives untouched; ``konsolerc``
is written only to name a default profile that is not set yet. Profile
names that are not plain file names (absolute paths, path separators,
traversal), symlinked profile destinations and an unresolvable profile name
are refused with an actionable diagnostic instead of guessed at.
Non-default profiles are never read or written, and ``make uninstall``
leaves ``konsolerc`` and the profiles alone: uninstalling the theme keeps
the user's terminal configuration.
"""

from __future__ import annotations

import os
from pathlib import Path

if __package__:
    from tools.atomic_write import write_bytes_atomically
    from tools.repo_root import ROOT
    from tools.required_command import run_required, run_required_output
    from tools.symlink_refusal import refuse_symlink
    from tools import xdg_homes
else:  # run directly: python3 tools/apply_konsole_font.py
    from atomic_write import write_bytes_atomically
    from repo_root import ROOT
    from required_command import run_required, run_required_output
    from symlink_refusal import refuse_symlink
    import xdg_homes

TOOL = "apply_theme"
KONSOLERC = "konsolerc"
# The keys are Konsole's own, grounded against upstream Konsole source
# (KDE Gear 25.04, the installed Konsole is 25.04.2): konsolerc names the
# default profile under [Desktop Entry] DefaultProfile as a file name
# relative to the konsole/ data directory; a profile names itself under
# [General] Name, inherits another one through [General] Parent (FALLBACK/
# is Konsole's built-in fallback profile), and overrides the system
# fixed-width font through [Appearance] Font. No reference screenshot shows
# a terminal, so this provenance is recorded in docs/installing.md.
PROFILE_GROUP = "Desktop Entry"
PROFILE_KEY = "DefaultProfile"
FALLBACK_PROFILE = "Platinum.profile"
FALLBACK_PARENT = "FALLBACK/"
FALLBACK_NAME = "Platinum"
FONT_GROUP = "Appearance"
FONT_KEY = "Font"
PROFILE_DIR = "konsole"
# The XDG Base Directory spec's default search path, used when XDG_DATA_DIRS
# is unset or empty; a relative entry in the variable is ignored, as the
# spec requires.
DEFAULT_DATA_DIRS = "/usr/local/share:/usr/share"


def apply(
    scratch: Path,
    env: dict[str, str],
    data_home: Path,
    font: str,
    error: type[Exception],
    timeout: float,
) -> int | None:
    """Point Konsole's default profile at *font*; return the status to exit.

    Called from :func:`tools.apply_theme._apply` under the data-home lock.
    ``scratch`` receives the commands' logs, ``env`` is the run environment,
    ``data_home`` the resolved XDG data home, ``font`` the serialized QFont
    ``apply_theme`` writes into ``kdeglobals``, ``error`` the refusal class
    the caller catches (``apply_theme``'s own, so its ``main`` reports the
    diagnostic as its exit-2 error), and ``timeout`` the command timeout.
    ``None`` on success; otherwise the exit status a failed required command
    reported, which the caller returns directly so the apply stops.
    """
    config_home = xdg_homes.require_home(
        xdg_homes.config_home(env),
        env,
        "XDG_CONFIG_HOME",
        "$HOME/.config",
        error=error,
    )
    stdout_log = scratch / "kreadconfig6.out"
    stderr_log = scratch / "kreadconfig6.err"
    raw, status = run_required_output(
        TOOL,
        [
            "kreadconfig6",
            "--file",
            str(config_home / KONSOLERC),
            "--group",
            PROFILE_GROUP,
            "--key",
            PROFILE_KEY,
            "--default",
            "",
        ],
        env,
        stdout_log,
        stderr_log,
        timeout,
        ROOT,
    )
    if status is not None:
        return status
    # KConfig trims an entry's value, so an absent or blank one is unset.
    name = raw.decode("utf-8", "surrogateescape").strip()
    if not name:
        return _apply_fallback(
            scratch, env, data_home, config_home, font, error, timeout
        )
    profile = _checked_name(name, error)
    path, in_data_home = _resolve(profile, env, data_home, error)
    if not in_data_home:
        path = _copy_to_data_home(path, name, data_home, error)
    return _write_font(scratch, env, path, font, timeout)


def _checked_name(name: str, error: type[Exception]) -> str:
    """Return *name* unchanged, or refuse a value that is not a file name.

    ``DefaultProfile`` must name a profile file inside a ``konsole/`` data
    directory; a path with a separator or traversal would reach outside
    that directory, so it is refused by name instead of resolved.
    """
    if name in (".", "..") or "/" in name or "\\" in name:
        raise error(
            f"refusing the Konsole default profile name {name!r}: a profile "
            "name must be a plain file name inside a konsole data directory, "
            "not a path; correct [Desktop Entry] DefaultProfile in konsolerc"
        )
    return name


def _resolve(
    name: str, env: dict[str, str], data_home: Path, error: type[Exception]
) -> tuple[Path, bool]:
    """Find *name* in the konsole data directories; refuse when unresolvable.

    Returns the profile path and whether it lives in the user's data home.
    The data home is searched first, then each absolute ``XDG_DATA_DIRS``
    entry, so a same-named profile in the data home shadows a system one
    exactly as Konsole's own search does. A symlinked profile is refused:
    writing through it would silently edit whatever file the link names.
    """
    for base in _search_bases(env, data_home):
        candidate = base / PROFILE_DIR / name
        if candidate.is_symlink():
            refuse_symlink(candidate, "write", error)
        if candidate.is_file():
            return candidate, base == data_home
    raise error(
        f"the Konsole default profile {name!r} does not exist in "
        f"{PROFILE_DIR}/ under the data home {data_home} or under any "
        "XDG_DATA_DIRS entry; create the profile in Konsole, or correct "
        "[Desktop Entry] DefaultProfile in konsolerc"
    )


def _search_bases(env: dict[str, str], data_home: Path) -> list[Path]:
    """Return the data directories the profile search visits, in order."""
    bases = [data_home]
    raw = env.get("XDG_DATA_DIRS") or DEFAULT_DATA_DIRS
    for entry in raw.split(":"):
        if entry and os.path.isabs(entry):
            bases.append(Path(entry))
    return bases


def _copy_to_data_home(
    source: Path, name: str, data_home: Path, error: type[Exception]
) -> Path:
    """Copy the system profile *source* into the data home and return it.

    Konsole reads ``konsole/`` under the data home before the system
    directories, so a copy with the same basename becomes the profile new
    sessions load without touching ``konsolerc``. An earlier copy is kept:
    a repeat apply must not discard the font edits it made before. The
    destination is refused when it is a symbolic link, and a failed
    directory creation or copy is a refusal, not a traceback.
    """
    destination_dir = data_home / PROFILE_DIR
    destination = destination_dir / name
    refuse_symlink(destination, "write", error)
    if destination.exists():
        return destination
    try:
        data = source.read_bytes()
    except OSError as exc:
        raise error(f"cannot read {source}: {exc}") from exc
    _make_dir(destination_dir, error)
    try:
        write_bytes_atomically(destination, data)
    except OSError as exc:
        raise error(f"cannot write {destination}: {exc}") from exc
    return destination


def _apply_fallback(
    scratch: Path,
    env: dict[str, str],
    data_home: Path,
    config_home: Path,
    font: str,
    error: type[Exception],
    timeout: float,
) -> int | None:
    """Create the fallback-derived profile and select it; return the status.

    With no ``DefaultProfile`` set, Konsole uses its built-in fallback, so
    there is no profile file to edit; a new one naming the packaged font is
    created instead and ``konsolerc`` selects it, which changes the default
    for new sessions only. ``kwriteconfig6`` replaces an existing key, so a
    repeat apply rewrites the same keys in place.
    """
    profile_dir = data_home / PROFILE_DIR
    profile = profile_dir / FALLBACK_PROFILE
    refuse_symlink(profile, "write", error)
    _make_dir(profile_dir, error)
    # The selection write lands in the config home, whose directory a
    # first-time user may not have yet; kwriteconfig6 would fail on it.
    _make_dir(config_home, error)
    writes = (
        (profile, "General", "Name", FALLBACK_NAME),
        (profile, "General", "Parent", FALLBACK_PARENT),
        (profile, FONT_GROUP, FONT_KEY, font),
        (config_home / KONSOLERC, PROFILE_GROUP, PROFILE_KEY, FALLBACK_PROFILE),
    )
    for file, group, key, value in writes:
        status = run_required(
            TOOL,
            ["kwriteconfig6", "--file", str(file), "--group", group, "--key", key, value],
            env,
            scratch / f"kwriteconfig6-{key}.log",
            timeout,
            ROOT,
        )
        if status is not None:
            return status
    return None


def _write_font(
    scratch: Path, env: dict[str, str], profile: Path, font: str, timeout: float
) -> int | None:
    """Write ``[Appearance] Font`` into *profile*; return the status.

    ``kwriteconfig6`` edits only the named key in place, so the profile's
    other keys -- and the shell, colors, shortcuts and keyboard mappings
    they hold -- are left byte-identical.
    """
    return run_required(
        TOOL,
        [
            "kwriteconfig6",
            "--file",
            str(profile),
            "--group",
            FONT_GROUP,
            "--key",
            FONT_KEY,
            font,
        ],
        env,
        scratch / "kwriteconfig6-Font.log",
        timeout,
        ROOT,
    )


def _make_dir(directory: Path, error: type[Exception]) -> None:
    """Create *directory*, refusing a failure with an actionable diagnostic.

    A ``konsole`` path that exists as a regular file, or a parent a plain
    ``mkdir`` cannot create, is refused by name instead of surfacing as a
    traceback out of the apply.
    """
    if directory.exists() and not directory.is_dir():
        raise error(f"cannot create {directory}: it is not a directory")
    try:
        directory.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise error(f"cannot create {directory}: {exc}") from exc
