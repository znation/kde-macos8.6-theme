"""Read README.md together with the docs/ guides it links, as one user-docs corpus."""

from __future__ import annotations

import re
from pathlib import Path

from support import containment
from support.repo_root import ROOT

_GUIDE_LINK = re.compile(r"\]\((docs/[^\s)#]+\.md)(?:#[^\s)]*)?\)")
_FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})")


def linked_guides(readme_text: str) -> list[str]:
    """Return the repo-relative ``docs/*.md`` paths README's inline links name.

    Links inside fenced code blocks are ignored. Each path appears once, in
    the order it is first linked.
    """
    guides: list[str] = []
    fence_char = None
    fence_size = 0
    for line in readme_text.splitlines():
        fence = _FENCE.match(line)
        if fence:
            marker = fence.group(1)
            if fence_char is None:
                fence_char, fence_size = marker[0], len(marker)
            elif marker[0] == fence_char and len(marker) >= fence_size:
                fence_char, fence_size = None, 0
            continue
        if fence_char is not None:
            continue
        for guide in _GUIDE_LINK.findall(line):
            if guide not in guides:
                guides.append(guide)
    return guides


def read_user_docs(root: str | Path = ROOT) -> str:
    """Return README.md's text followed by each guide it links, joined by blank lines.

    Every read goes through the containment reader, so a symlinked guide that
    escapes *root* is refused the same way a symlinked README is.
    """
    root = Path(root)
    readme = containment.read_text(root / "README.md", root, encoding="utf-8")
    parts = [readme]
    for guide in linked_guides(readme):
        parts.append(containment.read_text(root / guide, root, encoding="utf-8"))
    return "\n\n".join(parts)
