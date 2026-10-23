"""Temporary repositories whose file is a symlink, for containment tests."""

from __future__ import annotations

from pathlib import Path


def symlinked_repo(tmp, name, content, *, target=None):
    """Create ``tmp/repo`` and return ``(root, link)`` with ``root/name`` a symlink.

    ``content`` is written to the link's target first: text encoded as UTF-8,
    or bytes as-is. ``target`` is resolved under ``root`` unless absolute; it
    defaults to a same-named file beside ``root``, so the link escapes the
    repository. Pass a target relative to the temporary root for the allow
    case. The target's and link's parent directories are created as needed.
    """
    tmp = Path(tmp)
    root = tmp / "repo"
    root.mkdir(exist_ok=True)
    if target is None:
        target_path = root / ".." / Path(name).name
    else:
        target_path = Path(target)
        if not target_path.is_absolute():
            target_path = root / target_path
    target_path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, (bytes, bytearray)):
        target_path.write_bytes(bytes(content))
    else:
        target_path.write_text(content, encoding="utf-8")
    link = root / name
    link.parent.mkdir(parents=True, exist_ok=True)
    link.symlink_to(target_path)
    return root, link
