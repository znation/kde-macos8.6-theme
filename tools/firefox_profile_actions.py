"""Install and remove the theme's files in a Firefox profile."""

from __future__ import annotations

from pathlib import Path

if __package__:
    from tools.containment import read_bytes
    from tools.diagnostics import report_failure, report_note
    from tools.firefox_user_files import (
        MAX_PROFILE_FILE_BYTES,
        ConfigError,
        read_profile_text,
        user_chrome_path,
        user_content_path,
        user_js_path,
        write_profile_text,
    )
    from tools.firefox_user_js import first_line, remove_user_js, set_user_js
    from tools.firefox_transaction import publish_install
    from tools.repo_root import ROOT
    from tools.symlink_refusal import refuse_symlink
else:  # imported from a directly run tool
    from containment import read_bytes
    from diagnostics import report_failure, report_note
    from firefox_user_files import (
        MAX_PROFILE_FILE_BYTES,
        ConfigError,
        read_profile_text,
        user_chrome_path,
        user_content_path,
        user_js_path,
        write_profile_text,
    )
    from firefox_user_js import first_line, remove_user_js, set_user_js
    from firefox_transaction import publish_install
    from repo_root import ROOT
    from symlink_refusal import refuse_symlink

TOOL = "install_firefox"
SHEET = "theme/firefox/org.macos8.desktop/chrome/userChrome.css"
CSS_MARKER = "/* org.macos8.desktop Firefox chrome, standalone userChrome.css"
CONTENT_SHEET = "theme/firefox/org.macos8.desktop/chrome/userContent.css"
CONTENT_CSS_MARKER = (
    "/* org.macos8.desktop Firefox content, standalone userContent.css"
)
SHEETS = (
    (SHEET, CSS_MARKER, user_chrome_path),
    (CONTENT_SHEET, CONTENT_CSS_MARKER, user_content_path),
)


def _is_our_sheet(text: str, marker: str) -> bool:
    """Return whether the BOM-tolerant first line matches the owned marker."""
    return first_line(text).removeprefix("\ufeff") == marker


def apply_profile(profile: Path) -> int:
    """Install both sheets and the preference into *profile*."""
    refuse_symlink(profile / "chrome", "write", ConfigError)
    pending = []
    for source, marker, path_for in SHEETS:
        source_path = Path(ROOT) / source
        try:
            data = read_bytes(source_path, ROOT)
        except (OSError, ValueError) as exc:
            raise ConfigError(f"cannot read {source_path}: {exc}") from exc
        pending.append((source_path, marker, path_for(profile), data))

    destinations = []
    for source_path, marker, sheet_path, data in pending:
        existing_sheet = read_profile_text(sheet_path)
        if existing_sheet and not _is_our_sheet(existing_sheet, marker):
            return report_failure(
                TOOL,
                f"{sheet_path} is not our {source_path.name}; leaving it untouched",
            )
        destinations.append((sheet_path, data, existing_sheet))

    js_path = user_js_path(profile)
    existing_js = read_profile_text(js_path)
    updated_js = set_user_js(existing_js or "")
    if len(updated_js.encode("utf-8")) > MAX_PROFILE_FILE_BYTES:
        raise ConfigError(
            f"{js_path} would grow past the {MAX_PROFILE_FILE_BYTES}-byte "
            "limit this installer reads; refusing to write it"
        )
    for sheet_path, _data, _existing in destinations:
        refuse_symlink(sheet_path, "write", ConfigError)
    refuse_symlink(js_path, "write", ConfigError)
    chrome_dir = destinations[0][0].parent
    try:
        chrome_dir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise ConfigError(f"cannot create {chrome_dir}: {exc}") from exc
    publish_install(destinations, js_path, existing_js, updated_js)
    report_note(TOOL, f"installed the Firefox Platinum chrome into {profile}")
    return 0


def remove_profile(profile: Path) -> int:
    """Remove our sheets and preference block from *profile*."""
    refuse_symlink(profile / "chrome", "remove", ConfigError)
    owned = []
    for _source, marker, path_for in SHEETS:
        sheet_path = path_for(profile)
        existing_sheet = read_profile_text(sheet_path)
        if existing_sheet is not None and _is_our_sheet(existing_sheet, marker):
            owned.append((sheet_path, existing_sheet))
    js_path = user_js_path(profile)
    existing_js = read_profile_text(js_path)
    updated = None if existing_js is None else remove_user_js(existing_js)
    rewrite_js = updated is not None and updated != existing_js
    for sheet_path, _previous in owned:
        refuse_symlink(sheet_path, "remove", ConfigError)
    if rewrite_js:
        refuse_symlink(js_path, "remove", ConfigError)
    try:
        if rewrite_js:
            write_profile_text(js_path, updated)
        for sheet_path, _previous in owned:
            try:
                sheet_path.unlink()
            except OSError as exc:
                raise ConfigError(f"cannot remove {sheet_path}: {exc}") from exc
    except BaseException as exc:
        # A sheet whose unlink succeeded would otherwise stay deleted beside
        # the restored preference block: the rollback puts every already
        # deleted owned sheet back with the text the removal read, so a
        # removal that fails partway leaves the profile exactly as it was.
        # A run whose unlinks all took effect (an interrupt after the last
        # one) keeps the completed rewrite instead.
        any_sheet_left = any(path.exists() for path, _previous in owned)
        if any_sheet_left:
            rollback_errors = []
            if rewrite_js:
                try:
                    write_profile_text(js_path, existing_js)
                except ConfigError as rollback:
                    rollback_errors.append(str(rollback))
            for sheet_path, previous in owned:
                if sheet_path.exists():
                    continue
                try:
                    write_profile_text(sheet_path, previous)
                except ConfigError as rollback:
                    rollback_errors.append(str(rollback))
            if rollback_errors:
                raise ConfigError(f"{exc}; {'; '.join(rollback_errors)}") from exc
        raise
    return 0
