"""Edit the one marker-delimited Platinum block in a Ghostty config file.

``make apply-ghostty`` (through ``tools/apply_ghostty.py``) writes a three-line
block at the end of ``<config home>/ghostty/config.ghostty``::

    # >>> Platinum theme (managed by make apply-ghostty) >>>
    theme = <absolute path to the installed Platinum theme file>
    # <<< Platinum theme <<<

These functions work on the file's bytes so that every byte outside the block
is kept exactly. They never touch the filesystem; the CLI owns reading and the
atomic write.

Removing the block restores the original bytes exactly, with one exception: a
file that did not end in a newline gets one from the apply, because the block
must start on its own line. Removal keeps that newline, since nothing records
that it was added.
"""

from __future__ import annotations

BEGIN_MARKER = b"# >>> Platinum theme (managed by make apply-ghostty) >>>"
END_MARKER = b"# <<< Platinum theme <<<"


class GhosttyConfigError(Exception):
    """The config file's Platinum markers cannot be edited safely."""


def _block_lines(theme_path: bytes) -> list[bytes]:
    """Return the block's lines, each with its newline."""
    return [
        BEGIN_MARKER + b"\n",
        b"theme = " + theme_path + b"\n",
        END_MARKER + b"\n",
    ]


def _find_block(lines: list[bytes]) -> tuple[int, int] | None:
    """Return ``(start, stop)`` so ``lines[start:stop]`` is the block, or ``None``.

    *stop* is exclusive. A begin marker without a later end marker, an end
    marker without a begin marker, or more than one block is refused, because
    the rest of the file could not be kept byte-identical around a guess.
    """
    begins = [i for i, line in enumerate(lines) if _is_marker(line, BEGIN_MARKER)]
    ends = [i for i, line in enumerate(lines) if _is_marker(line, END_MARKER)]
    if not begins and not ends:
        return None
    if len(begins) != 1 or len(ends) != 1 or begins[0] > ends[0]:
        raise GhosttyConfigError(
            "the Platinum theme markers are unbalanced or repeated in the "
            "Ghostty config; fix or remove the marker lines by hand"
        )
    return begins[0], ends[0] + 1


def _is_marker(line: bytes, marker: bytes) -> bool:
    """Return whether *line* is *marker* alone on its line."""
    return line.rstrip(b"\r\n") == marker


def apply_block(data: bytes, theme_path: bytes) -> bytes:
    """Return *data* with the Platinum block naming *theme_path* in place.

    An existing block is replaced where it stands; otherwise the block is
    appended after a newline that ends the last line. Applying twice gives the
    same bytes as applying once.
    """
    if b"\n" in theme_path or b"\r" in theme_path:
        raise GhosttyConfigError("the theme path contains a line break")
    lines = data.splitlines(keepends=True)
    found = _find_block(lines)
    block = _block_lines(theme_path)
    if found is not None:
        start, stop = found
        return b"".join(lines[:start] + block + lines[stop:])
    if data and not data.endswith(b"\n"):
        data += b"\n"
    return data + b"".join(block)


def remove_block(data: bytes) -> bytes:
    """Return *data* without its Platinum block; unchanged when there is none."""
    lines = data.splitlines(keepends=True)
    found = _find_block(lines)
    if found is None:
        return data
    start, stop = found
    return b"".join(lines[:start] + lines[stop:])
