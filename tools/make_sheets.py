"""Generate the shipped stylesheets by concatenating their source partials.

Each entry in ``SHEETS`` pairs a source directory of partials with the shipped
sheet it produces. A partial is a ``*.css`` file in the source directory; the
generator joins them in sorted filename order, byte for byte with nothing
inserted between them, and writes the result as the shipped sheet. Other files
in a source directory are ignored. Contributors edit the partials, never the
shipped sheet, and rerun the generator.

Run ``python3 tools/make_sheets.py`` from anywhere; the output is deterministic,
so re-running rewrites identical bytes.

Every pair is validated before any file is written: a source directory with no
partial, or a partial that is empty or does not end in a newline, stops the run
with a diagnostic naming it. A shipped sheet's directory that resolves outside
the repository (a checked-in symlink) is refused by name before anything is
written.

Exit status: 0 when every sheet was written (and for ``--help``/``-h``), 2 for
a usage error, a source that fails validation, a directory that resolves outside
the repository, or a directory or file that cannot be read, created or written.
"""

from __future__ import annotations

import sys
from pathlib import Path

if __package__:
    from tools.argument_parsing import EscapingArgumentParser
    from tools.containment import require_within_repo
    from tools.diagnostics import report_error
    from tools.generated_files import write_generated_files
    from tools.repo_root import ROOT
else:  # run directly: python3 tools/make_sheets.py
    from argument_parsing import EscapingArgumentParser
    from containment import require_within_repo
    from diagnostics import report_error
    from generated_files import write_generated_files
    from repo_root import ROOT

TOOL = "make_sheets"
SHEETS = (
    (
        "theme/gtk/src/gtk-3.0",
        "theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css",
    ),
)


def sheet_bytes(source_dir: Path) -> bytes:
    """Return the concatenation of *source_dir*'s ``*.css`` partials in sorted order.

    Raises ``ValueError`` naming *source_dir* when it holds no ``*.css`` partial,
    and naming the partial when one is empty or does not end in a newline.
    """
    partials = sorted(p for p in source_dir.iterdir() if p.is_file() and p.suffix == ".css")
    if not partials:
        raise ValueError(f"no .css partial in {source_dir}")
    chunks = []
    for partial in partials:
        data = partial.read_bytes()
        if not data or not data.endswith(b"\n"):
            raise ValueError(
                f"partial {partial} is empty or does not end in a newline"
            )
        chunks.append(data)
    return b"".join(chunks)


def main(argv: list[str] | None = None) -> int:
    """Run the generator CLI; *argv* is the argument list without a program name.

    The generator takes no options, but its command line is still parsed so a
    mistaken argument is a diagnostic instead of being silently ignored.
    """
    parser = EscapingArgumentParser(
        prog=TOOL,
        description="Regenerate the shipped stylesheets from their source partials.",
        epilog="exit status: 0 when every sheet was written, 2 on a usage or read/write error",
    )
    parser.parse_args(argv)
    # Validate every pair before writing anything, so a bad partial in one
    # family leaves every shipped sheet untouched.
    rendered = []
    try:
        for source, shipped in SHEETS:
            target = ROOT / shipped
            # Refuse a sheet directory that resolves outside the repository
            # before any file in any family is written.
            require_within_repo(target.parent, ROOT, action="write")
            rendered.append((target, sheet_bytes(ROOT / source)))
    except (ValueError, OSError) as exc:
        return report_error(TOOL, str(exc))
    status = 0
    for target, data in rendered:
        status = write_generated_files(TOOL, ROOT, target.parent, [(target, data)])
        if status:
            return status
    return status


if __name__ == "__main__":
    sys.exit(main())
