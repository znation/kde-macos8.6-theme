"""Read and parse the bounded ``sources.txt`` provenance record."""

from __future__ import annotations

from pathlib import Path

if __package__:
    from tools.text_lines import split_lines
else:
    from text_lines import split_lines

if __package__:
    from tools.containment import open_regular_binary
    from tools.url_check import url_problem
else:  # imported from a directly run tool
    from containment import open_regular_binary
    from url_check import url_problem

SOURCES_NAME = "sources.txt"
SEPARATOR = " | "
_MAX_SOURCES_BYTES = 1 << 20


def read_sources_text(sources: Path) -> tuple[str | None, str | None]:
    """Return ``(text, None)`` or ``(None, problem)`` for the bounded record."""
    try:
        with open_regular_binary(sources) as handle:
            data = handle.read(_MAX_SOURCES_BYTES + 1)
    except (OSError, ValueError) as exc:
        return None, f"{sources}: could not be read: {exc}"
    if len(data) > _MAX_SOURCES_BYTES:
        return None, (
            f"{sources}: is larger than the {_MAX_SOURCES_BYTES}-byte limit "
            "for a provenance record"
        )
    try:
        return data.decode("utf-8-sig"), None
    except UnicodeDecodeError as exc:
        return None, f"{sources}: not valid UTF-8 text: {exc}"


def parse_sources(
    directory: Path, sources: Path, text: str
) -> tuple[list[tuple[int, str]], dict[str, int]]:
    """Validate record syntax and return accepted filename declarations."""
    problems: list[tuple[int, str]] = []
    entries: dict[str, int] = {}
    for lineno, raw in enumerate(split_lines(text), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        fields = line.split(SEPARATOR)
        if len(fields) != 3:
            problems.append(
                (lineno, f"{sources}:{lineno}: expected 3 fields separated by {SEPARATOR.strip()!r}, "
                 f"got {len(fields)}: {line!r}")
            )
            continue
        filename, url, label = (field.strip() for field in fields)
        if not filename or not url or not label:
            problems.append((lineno, f"{sources}:{lineno}: empty field in entry: {line!r}"))
            continue
        if "\x00" in filename:
            problems.append(
                (lineno, f"{sources}:{lineno}: {filename!r} contains a NUL byte and "
                 "cannot name a file")
            )
            continue
        problem = url_problem(url)
        if problem is not None:
            problems.append((lineno, f"{sources}:{lineno}: source URL {url!r} {problem}"))
            continue
        if Path(filename).name != filename or filename in (".", ".."):
            problems.append(
                (lineno, f"{sources}:{lineno}: {filename!r} must be a bare filename in "
                 f"{directory}/, not a path")
            )
            continue
        if filename in entries:
            problems.append(
                (lineno, f"{sources}:{lineno}: duplicate entry for {filename!r} "
                 f"(first at line {entries[filename]})")
            )
            continue
        entries[filename] = lineno
    return problems, entries
