"""Check README same-document links against headings and explicit anchors."""

from __future__ import annotations

import re
import unittest

from support import containment
from support.repo_root import ROOT

_HEADING = re.compile(r"^ {0,3}#{1,6}[ \t]+(.+?)[ \t]*#*[ \t]*$")
_LINK = re.compile(r"\[[^\]]*\]\(#([^\s)]+)\)")
_ANCHOR = re.compile(r"^\s{0,3}<a\s+id\s*=\s*(['\"])([^'\"]+)\1\s*>\s*</a>\s*$")
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
        anchor = _ANCHOR.match(line)
        if anchor:
            destinations.add(anchor.group(2))
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

    def test_explicit_anchors_resolve_forward_links_without_changing_heading_slugs(self):
        for quote in ('"', "'"):
            text = f"[legacy](#navigation)\n  <a id={quote}navigation{quote}></a>\n# Navigation\n# Navigation\n[heading](#navigation-1)"
            self.assertEqual([], local_link_errors(text))
        self.assertEqual(["navigation"], local_link_errors("[legacy](#navigation)\n<a id='Navigation'></a>"))

    def test_explicit_anchors_inside_fences_are_not_destinations(self):
        for fence in ("```", "~~~"):
            text = f"{fence}\n<a id='navigation'></a>\n{fence}\n[legacy](#navigation)"
            self.assertEqual(["navigation"], local_link_errors(text))

    def test_navigation_anchor_precedes_contents_in_repository_readme(self):
        readme = read_readme()
        self.assertEqual([], local_link_errors(readme + "\n[legacy](#navigation)"))

        def navigation_position(text):
            lines = text.splitlines()
            anchor = next((i for i, line in enumerate(lines) if _ANCHOR.match(line) and _ANCHOR.match(line).group(2) == "navigation"), None)
            contents = next((i for i, line in enumerate(lines) if line == "## Contents"), None)
            return anchor, contents

        anchor, contents = navigation_position(readme)
        self.assertIsNotNone(anchor)
        self.assertIsNotNone(contents)
        self.assertTrue(all(not line.strip() for line in readme.splitlines()[anchor + 1:contents]))
        self.assertLess(anchor, contents)

        removed = readme.replace('<a id="navigation"></a>', "", 1)
        renamed = readme.replace('<a id="navigation"></a>', '<a id="other"></a>', 1)
        moved = readme.replace('<a id="navigation"></a>\n\n## Contents', '## Contents\n\n<a id="navigation"></a>', 1)
        self.assertIn("navigation", local_link_errors(removed + "\n[legacy](#navigation)"))
        self.assertIn("navigation", local_link_errors(renamed + "\n[legacy](#navigation)"))
        self.assertGreater(navigation_position(moved)[0], navigation_position(moved)[1])


if __name__ == "__main__":
    unittest.main()
