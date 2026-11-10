"""Decode a JPEG image into a temporary PNG for tools/sample.py.

The PNG decode pipeline in ``tools/png/`` is stdlib-only PNG, so the sampler
reads JPEG screenshots -- reference-set members shipped as JPEG -- through
this bridge instead: :func:`convert_jpeg` pipes the bytes once through
ImageMagick's ``convert`` into a caller-provided private temporary PNG and
the sampler treats that file exactly like any PNG input. Everything the
JPEG branch shares lives here; the sampler's sniffer calls :func:`is_jpeg`
and nothing else about the bridge.
"""

from __future__ import annotations

import os
import re
import shutil
import tempfile
from pathlib import Path

if __package__:
    from tools.process_group import run_logged_split
else:  # imported as a plain module by the direct-run path
    from process_group import run_logged_split

# JPEGs start with the SOI marker FF D8; the third byte is the marker that
# follows, FF by standard. Three bytes are enough to refuse while the bytes
# are still in the caller's buffer.
JPEG_MAGIC = bytes((0xFF, 0xD8, 0xFF))

_CONVERT_TIMEOUT = 60.0


def is_jpeg(head: bytes) -> bool:
    """Return whether the leading bytes *head* start a JPEG stream."""
    return head.startswith(JPEG_MAGIC)


def convert_jpeg(input_bytes: bytes, temp_png: Path) -> str | None:
    """Decode *input_bytes* into *temp_png* with ImageMagick's convert.

    Returns None on success, or a diagnostic for the sampler to print. The
    converter runs ``convert jpeg:- PNG24:<temp_png>`` supervised through
    :func:`run_logged_split`: the input arrives on stdin, so no path in the
    user's tree is followed, and the output is written to the caller-provided
    path inside the caller's private temporary directory. Logs live in a
    second private temporary directory of this function's own, dropped when
    the call returns.
    """
    executable = shutil.which("convert")
    if executable is None:
        return (
            "the input is a JPEG image, and decoding it needs ImageMagick's "
            "convert, which is not installed"
        )
    with tempfile.TemporaryDirectory(prefix="sample-convert-") as log_dir:
        stdout_log = Path(log_dir) / "convert-stdout.log"
        stderr_log = Path(log_dir) / "convert-stderr.log"
        try:
            status = run_logged_split(
                # PNG24 forces an 8-bit truecolor output: a paletted PNG's
                # bit depth would be changed by the shared PNG loader's
                # refusal, not decoded, and the sampler must see the same
                # RGB channels a truecolor screenshot carries.
                [executable, "jpeg:-", f"PNG24:{temp_png}"],
                dict(os.environ),
                stdout_log,
                stderr_log,
                _CONVERT_TIMEOUT,
                Path.cwd(),
                stdin_bytes=input_bytes,
            )
        except OSError as exc:
            return f"cannot run convert: {exc}"
        if status is None:
            return (
                f"convert did not decode the JPEG input within "
                f"{_CONVERT_TIMEOUT:g}s"
            )
        if status != 0:
            return _failed_output(
                f"convert exited {status}", temp_png, stdout_log, stderr_log
            )
    if not temp_png.exists() or temp_png.stat().st_size == 0:
        return "convert wrote no PNG for the JPEG input"
    return None


def _failed_output(headline: str, temp_png: Path, *logs: Path) -> str:
    """Return the convert failure diagnostic with any temp path scrubbed.

    A decode failure's own output belongs to the operator, but it can name
    the temporary PNG's path, which tells them nowhere they typed;
    occurrences of the private paths are blanked so the diagnostic names
    surfaces the user chose, never the scratch file.
    """
    lines: list[str] = []
    for log in logs:
        try:
            tail = log.read_text(errors="replace").strip()
        except OSError:
            tail = ""
        if tail:
            lines.append(tail)
    message = f"{headline}: {lines[0]}" if lines else headline
    message = re.sub(r"/\S*magick-\S*", "<an ImageMagick temporary>", message)
    return (
        message.replace(str(temp_png), "<the temporary decoded PNG>")
        .replace(str(temp_png.parent), "<a temporary directory>")
    )
