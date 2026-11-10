"""Check README same-document links against its plain ATX headings."""

from __future__ import annotations

import re
import unittest

from support import containment
from support.repo_root import ROOT

_HEADING = re.compile(r"^ {0,3}#{1,6}[ \t]+(.+?)[ \t]*#*[ \t]*$")
_LINK = re.compile(r"\[[^\]]*\]\(#([^\s)]+)\)")
_PUNCTUATION = re.compile(r"[^\w\s-]", re.UNICODE)
_FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})")


def read_readme() -> str:
    return containment.read_text(f"{ROOT}/README.md", ROOT, encoding="utf-8")


def _slug(text: str) -> str:
    text = _PUNCTUATION.sub("", text.lower())
    return re.sub(r"\s+", "-", text.strip())


def local_link_errors(text: str) -> list[str]:
    """Return unresolved local fragments outside fenced code blocks."""
    destinations: set[str] = set()
    links: list[str] = []
    fence_char = None
    fence_size = 0
    used: set[str] = set()
    for line in text.splitlines():
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
        heading = _HEADING.match(line)
        if heading:
            base = _slug(heading.group(1))
            slug = base
            suffix = 1
            while slug in used:
                slug = f"{base}-{suffix}"
                suffix += 1
            used.add(slug)
            destinations.add(slug)
        links.extend(_LINK.findall(line))
    return [target for target in links if target not in destinations]


class TestReadmeLinks(unittest.TestCase):
    def test_local_links_resolve(self):
        readme = read_readme()
        self.assertTrue(readme, "README is empty")
        errors = local_link_errors(readme)
        self.assertEqual([], errors, f"unresolved README fragments: {errors}")

    def test_link_resolves_and_renamed_heading_is_reported(self):
        self.assertEqual([], local_link_errors("# Removing the theme\n[remove](#removing-the-theme)"))
        self.assertEqual(["removing-the-theme"], local_link_errors("# Removing Platinum\n[remove](#removing-the-theme)"))

    def test_fences_exclude_headings_and_links_for_both_markers(self):
        text = """~~~md
# hidden
[hidden](#missing)
~~~
```md
# also hidden
[ignored](#missing)
```
[real](#real)
# Real
"""
        self.assertEqual([], local_link_errors(text))

    def test_heading_slugs_duplicates_and_numeric_collision(self):
        text = """# MiXeD, punctuation! keep-this_and
[one](#mixed-punctuation-keep-this_and)
# Repeated
# repeated
# repeated-1
# repeated
[two](#repeated-2)
"""
        self.assertEqual([], local_link_errors(text))

    def test_external_and_relative_links_are_ignored(self):
        self.assertEqual([], local_link_errors("[web](https://example.test) [file](guide.md)"))

    def test_unresolved_link_in_empty_document_is_reported(self):
        self.assertEqual(["missing"], local_link_errors("[link](#missing)"))


if __name__ == "__main__":
    unittest.main()
