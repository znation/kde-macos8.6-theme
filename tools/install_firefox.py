"""Install the Firefox Platinum chrome into one opt-in Firefox profile.

``make install-firefox`` copies the standalone ``userChrome.css`` into a
profile's ``chrome/`` directory and adds the preference that makes Firefox
read it; ``make remove-firefox`` removes exactly those two changes. The
profile is named with ``--profile``/``FIREFOX_PROFILE`` or, without either,
resolved from ``installs.ini`` and ``profiles.ini`` under
``$HOME/.mozilla/firefox``.

Usage::

    python3 tools/install_firefox.py [--profile PATH]
    python3 tools/install_firefox.py --remove [--profile PATH]

Exit status: 0 when the install or removal ran, 1 when a foreign
``userChrome.css`` is left untouched, 2 for a usage error, an unresolvable
profile, or a file that cannot be read or written.
"""

from __future__ import annotations

import configparser
import os
import sys
from collections import Counter
from pathlib import Path

if __package__:
    from tools.argument_parsing import EscapingArgumentParser
    from tools.atomic_write import write_atomically
    from tools.containment import read_bytes
    from tools.diagnostics import report_error, report_failure
    from tools.repo_root import ROOT
    from tools.terminal import escape_controls
else:  # run directly: python3 tools/install_firefox.py
    from argument_parsing import EscapingArgumentParser
    from atomic_write import write_atomically
    from containment import read_bytes
    from diagnostics import report_error, report_failure
    from repo_root import ROOT
    from terminal import escape_controls

TOOL = "install_firefox"
SHEET = "theme/firefox/org.macos8.desktop/chrome/userChrome.css"
CSS_MARKER = "/* org.macos8.desktop Firefox chrome, standalone userChrome.css"
USER_JS_MARKER = "// org.macos8.desktop Firefox Platinum userChrome"
PREF_LINE = 'user_pref("toolkit.legacyUserProfileCustomizations.stylesheets", true);'


class ConfigError(Exception):
    """A profile or text file cannot be used; ``main`` reports it by name."""


def _note(message: str) -> None:
    """Print ``install_firefox: note: <message>`` on stdout."""
    print(f"{TOOL}: note: {escape_controls(message)}")


def _lines(text: str) -> list[tuple[str, str]]:
    """Return ``(content, ending)`` pairs, keeping every line's own ending.

    The final pair's ending is ``""`` when the text does not end with a line
    break, so joining the pairs reproduces *text* exactly.
    """
    lines = []
    index = 0
    while index < len(text):
        end = index
        while end < len(text) and text[end] not in "\r\n":
            end += 1
        if end == len(text):
            lines.append((text[index:end], ""))
            break
        if text[end] == "\r" and end + 1 < len(text) and text[end + 1] == "\n":
            lines.append((text[index:end], "\r\n"))
            end += 2
        else:
            lines.append((text[index:end], text[end]))
            end += 1
        index = end
    return lines


def _join(lines: list[tuple[str, str]]) -> str:
    """Join ``(content, ending)`` pairs back into text."""
    return "".join(content + ending for content, ending in lines)


def _dominant_ending(lines: list[tuple[str, str]]) -> str:
    """Return the line ending the file uses most, or ``"\\n"`` for no lines.

    Ties keep the earliest-seen ending, so a file with one CRLF and one LF
    keeps the CRLF its first line used.
    """
    endings = Counter(ending for _, ending in lines if ending)
    if not endings:
        return "\n"
    return endings.most_common(1)[0][0]


def _without_block(lines: list[tuple[str, str]]) -> list[tuple[str, str]]:
    """Drop each marker line and the exact pref line immediately after it."""
    kept = []
    index = 0
    while index < len(lines):
        if lines[index][0] == USER_JS_MARKER:
            index += 1
            if index < len(lines) and lines[index][0] == PREF_LINE:
                index += 1
            continue
        kept.append(lines[index])
        index += 1
    return kept


def set_user_js(text: str) -> str:
    """Return *text* with exactly one marker-plus-pref block at the end.

    Foreign lines keep their own endings. An earlier block is removed first,
    so a repeat install does not duplicate it. An unterminated last foreign
    line is terminated before the block is appended, and the block uses the
    file's dominant ending (``"\\n"`` for a new file). A foreign setting of
    the same preference is left alone, so our line follows it.
    """
    lines = _without_block(_lines(text))
    ending = _dominant_ending(lines)
    if lines and not lines[-1][1]:
        content, _ = lines[-1]
        lines[-1] = (content, ending)
    lines.append((USER_JS_MARKER, ending))
    lines.append((PREF_LINE, ending))
    return _join(lines)


def remove_user_js(text: str) -> str:
    """Return *text* without our marker-plus-pref block, foreign lines intact."""
    return _join(_without_block(_lines(text)))


def _first_line(text: str) -> str:
    """Return *text*'s first line without its ending."""
    lines = _lines(text)
    return lines[0][0] if lines else ""


def _read_text(path: Path) -> str | None:
    """Return *path*'s UTF-8 text, or ``None`` when it does not exist.

    A directory, a device, an unreadable file and invalid UTF-8 are reported
    by name as a :class:`ConfigError` rather than escaping as a traceback.
    """
    try:
        data = path.read_bytes()
    except FileNotFoundError:
        return None
    except OSError as exc:
        raise ConfigError(f"cannot read {path}: {exc}") from exc
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ConfigError(f"cannot read {path}: {exc}") from exc


def _write_bytes(path: Path, data: bytes) -> None:
    """Publish *data* at *path*, reporting a write failure by path."""
    try:
        write_atomically(path, lambda handle: handle.write(data))
    except OSError as exc:
        raise ConfigError(f"cannot write {path}: {exc}") from exc


def _write_text(path: Path, text: str) -> None:
    """Publish *text* as UTF-8 at *path*, reporting a write failure by path."""
    _write_bytes(path, text.encode("utf-8"))


def _read_ini(path: Path) -> configparser.ConfigParser | None:
    """Return *path* parsed without interpolation, or ``None`` when absent."""
    parser = configparser.ConfigParser(interpolation=None)
    try:
        with path.open(encoding="utf-8") as handle:
            parser.read_file(handle)
    except FileNotFoundError:
        return None
    except (OSError, UnicodeDecodeError, configparser.Error) as exc:
        raise ConfigError(f"cannot read {path}: {exc}") from exc
    return parser


def _candidate(
    root: Path, section: configparser.SectionProxy, key: str
) -> Path | None:
    """Return the directory *section* names under *key*, or ``None``.

    The path is relative to *root* unless the section sets ``IsRelative=0``.
    ``installs.ini`` names its default under ``Default`` while a
    ``profiles.ini`` profile names its directory under ``Path``.
    """
    value = section.get(key, fallback="").strip()
    if not value:
        return None
    path = Path(value)
    if section.get("IsRelative", fallback="1").strip() != "0":
        return root / path
    return path


def _candidates(root: Path) -> list[Path]:
    """Return profile candidates in Firefox's own preference order."""
    candidates = []
    installs = _read_ini(root / "installs.ini")
    if installs is not None:
        for name in installs.sections():
            # Firefox names these sections by install hash (and older releases
            # by ``Install`` plus a suffix), so any section can hold Default.
            candidate = _candidate(root, installs[name], "Default")
            if candidate is not None:
                candidates.append(candidate)
                break
    profiles = _read_ini(root / "profiles.ini")
    if profiles is not None:
        sections = [
            profiles[name]
            for name in profiles.sections()
            if name.startswith("Profile")
        ]
        for section in sections:
            if section.get("Default", fallback="").strip() == "1":
                candidate = _candidate(root, section, "Path")
                if candidate is not None:
                    candidates.append(candidate)
                break
        for section in sections:
            candidate = _candidate(root, section, "Path")
            if candidate is not None:
                candidates.append(candidate)
                break
    return candidates


def resolve_profile(explicit: str | None, env: dict[str, str]) -> Path:
    """Return the profile directory named by *explicit*, the environment or INI.

    *explicit* is the ``--profile`` value; when it is ``None`` an
    ``FIREFOX_PROFILE`` environment variable is used. Either named path must
    be an absolute existing directory. Without one, ``HOME`` must be absolute
    and the profile is resolved from ``$HOME/.mozilla/firefox``.
    """
    named = explicit if explicit is not None else env.get("FIREFOX_PROFILE")
    if named is not None:
        path = Path(named)
        if not path.is_absolute():
            raise ConfigError(f"Firefox profile must be an absolute path: {path}")
        if not path.is_dir():
            raise ConfigError(f"Firefox profile is not a directory: {path}")
        return path

    home = env.get("HOME", "")
    if not os.path.isabs(home):
        raise ConfigError(
            "HOME is unset or not absolute and no Firefox profile was named"
        )
    root = Path(home) / ".mozilla" / "firefox"
    candidates = _candidates(root)
    for candidate in candidates:
        if candidate.is_dir():
            return candidate
    tried = ", ".join(str(path) for path in candidates) or "none"
    raise ConfigError(
        f"no Firefox profile found under {root}; candidates tried: {tried}"
    )


def _paths(profile: Path) -> tuple[Path, Path]:
    """Return the profile's ``userChrome.css`` and ``user.js`` paths."""
    return profile / "chrome" / "userChrome.css", profile / "user.js"


def _apply(profile: Path) -> int:
    """Install the sheet and preference into *profile*."""
    try:
        sheet = read_bytes(Path(ROOT) / SHEET, ROOT)
    except (OSError, ValueError) as exc:
        raise ConfigError(f"cannot read {Path(ROOT) / SHEET}: {exc}") from exc
    sheet_path, js_path = _paths(profile)
    existing_sheet = _read_text(sheet_path)
    if existing_sheet is not None and _first_line(existing_sheet) != CSS_MARKER:
        return report_failure(
            TOOL,
            f"{sheet_path} is not our userChrome.css; leaving it untouched",
        )
    existing_js = _read_text(js_path)
    try:
        sheet_path.parent.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise ConfigError(f"cannot create {sheet_path.parent}: {exc}") from exc
    _write_bytes(sheet_path, sheet)
    _write_text(js_path, set_user_js(existing_js or ""))
    _note(f"installed the Firefox Platinum chrome into {profile}")
    return 0


def _remove(profile: Path) -> int:
    """Remove our sheet and preference block from *profile*."""
    sheet_path, js_path = _paths(profile)
    existing_sheet = _read_text(sheet_path)
    existing_js = _read_text(js_path)
    if existing_sheet is not None and _first_line(existing_sheet) == CSS_MARKER:
        try:
            sheet_path.unlink()
        except OSError as exc:
            raise ConfigError(f"cannot remove {sheet_path}: {exc}") from exc
    if existing_js is not None:
        updated = remove_user_js(existing_js)
        if updated != existing_js:
            _write_text(js_path, updated)
    return 0


def main(argv: list[str] | None = None) -> int:
    """Run the Firefox profile install CLI; *argv* excludes the program name."""
    parser = EscapingArgumentParser(
        prog=TOOL,
        description=(
            "Install or remove the Mac OS 8.6 Firefox Platinum userChrome.css "
            "in one Firefox profile."
        ),
        epilog=(
            "exit status: 0 when the install or removal ran, 1 when a foreign "
            "userChrome.css is left untouched, 2 for a usage error, an "
            "unresolvable profile, or a file that cannot be read or written"
        ),
    )
    parser.add_argument(
        "--profile",
        metavar="PATH",
        help="absolute Firefox profile directory (default: FIREFOX_PROFILE "
        "or the active profile under $HOME/.mozilla/firefox)",
    )
    parser.add_argument(
        "--remove",
        action="store_true",
        help="remove our userChrome.css and user.js preference block",
    )
    args = parser.parse_args(argv)

    try:
        profile = resolve_profile(args.profile, os.environ)
        if args.remove:
            return _remove(profile)
        return _apply(profile)
    except ConfigError as exc:
        return report_error(TOOL, str(exc))


if __name__ == "__main__":
    sys.exit(main())
