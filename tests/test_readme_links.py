"""Check README same-document links against headings and explicit anchors."""

from __future__ import annotations

import re
import unittest
from pathlib import Path
from unittest import mock

from support import containment
from support.repo_root import ROOT
from support.tmp_dir import make_tmp_dir
from support.user_docs import linked_guides

_HEADING = re.compile(r"^ {0,3}#{1,6}[ \t]+(.+?)[ \t]*#*[ \t]*$")
_LINK = re.compile(r"\[[^\]]*\]\(#([^\s)]+)\)")
_CROSS_LINK = re.compile(r"\]\(([^)\s#]+\.md)(?:#([^\s)]+))?\)")
_SCHEME = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
_ANCHOR = re.compile(r"^\s{0,3}<a\s+id\s*=\s*(['\"])([^'\"]+)\1\s*>\s*</a>\s*$")
_PUNCTUATION = re.compile(r"[^\w\s-]", re.UNICODE)
_FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})")


def read_readme() -> str:
    """Return the repository README's text."""
    return containment.read_text(f"{ROOT}/README.md", ROOT, encoding="utf-8")


def _slug(text: str) -> str:
    """Return the GitHub-style heading anchor slug for *text*."""
    text = _PUNCTUATION.sub("", text.lower())
    return re.sub(r"\s+", "-", text.strip())


def _prose_lines(text: str):
    """Yield the lines of *text* outside fenced code blocks, fences excluded."""
    fence_char = None
    fence_size = 0
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
        yield line


def _destinations(text: str) -> set[str]:
    """Return the fragment destinations *text* defines: heading slugs and explicit anchors."""
    destinations: set[str] = set()
    used: set[str] = set()
    for line in _prose_lines(text):
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
    return destinations


def local_link_errors(text: str) -> list[str]:
    """Return unresolved local fragments outside fenced code blocks."""
    destinations = _destinations(text)
    links: list[str] = []
    for line in _prose_lines(text):
        links.extend(_LINK.findall(line))
    return [target for target in links if target not in destinations]


def cross_file_link_errors(source_path, text: str, root=ROOT) -> list[str]:
    """Return ``](<file>.md)`` and ``](<file>.md#frag)`` links that do not resolve.

    A target resolves relative to *source_path*'s directory. It is an error when
    the file is missing, or when the fragment names no heading slug or explicit
    anchor in that file. URL-scheme targets are ignored. Files are read through
    the containment reader bounded by *root*.
    """
    source_dir = Path(source_path).parent
    errors: list[str] = []
    for line in _prose_lines(text):
        for target, fragment in _CROSS_LINK.findall(line):
            if _SCHEME.match(target):
                continue
            path = source_dir / target
            label = f"{target}#{fragment}" if fragment else target
            if not path.is_file():
                errors.append(label)
                continue
            if fragment:
                linked = containment.read_text(path, root, encoding="utf-8")
                if fragment not in _destinations(linked):
                    errors.append(label)
    return errors


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

    def test_cross_file_missing_file_and_unmatched_fragment_are_reported(self):
        root = make_tmp_dir(self)
        (root / "docs").mkdir()
        (root / "README.md").write_text(
            "# Real heading\n\n[missing](docs/invariants.md) [bad fragment](docs/principles-rationale.md#nope)\n",
            encoding="utf-8",
        )
        (root / "docs" / "principles-rationale.md").write_text("# Real heading\n", encoding="utf-8")
        readme = (root / "README.md").read_text(encoding="utf-8")
        self.assertEqual(
            ["docs/invariants.md", "docs/principles-rationale.md#nope"],
            cross_file_link_errors(root / "README.md", readme, root),
        )

    def test_cross_file_fragment_matching_heading_slug_or_anchor_resolves(self):
        root = make_tmp_dir(self)
        (root / "docs").mkdir()
        readme = "[h](docs/principles-rationale.md#real-heading) [a](docs/principles-rationale.md#explicit)\n"
        (root / "README.md").write_text(readme, encoding="utf-8")
        (root / "docs" / "principles-rationale.md").write_text(
            "# Real heading\n<a id='explicit'></a>\n", encoding="utf-8"
        )
        self.assertEqual([], cross_file_link_errors(root / "README.md", readme, root))

    def test_cross_file_targets_resolve_relative_to_the_source_directory(self):
        root = make_tmp_dir(self)
        (root / "docs").mkdir()
        guide = "# Guide\n\n[back](../README.md#installing)\n"
        (root / "README.md").write_text("# Installing\n", encoding="utf-8")
        (root / "docs" / "guide.md").write_text(guide, encoding="utf-8")
        self.assertEqual([], cross_file_link_errors(root / "docs" / "guide.md", guide, root))
        moved = guide.replace("../README.md", "README.md")
        self.assertEqual(
            ["README.md#installing"],
            cross_file_link_errors(root / "docs" / "guide.md", moved, root),
        )

    def test_cross_file_scheme_targets_are_ignored(self):
        root = make_tmp_dir(self)
        text = "[web](https://example.com/elsewhere/b.md) [other scheme](mailto:b.md)\n"
        self.assertEqual([], cross_file_link_errors(root / "README.md", text, root))

    def test_linked_guide_with_unresolved_local_fragment_is_rejected(self):
        root = make_tmp_dir(self)
        (root / "docs").mkdir()
        (root / "README.md").write_text("[guide](docs/invariants.md)\n", encoding="utf-8")
        guide_path = root / "docs" / "invariants.md"
        guide_path.write_text("# Guide\n[broken](#missing)\n", encoding="utf-8")
        with mock.patch.dict(globals(), ROOT=root):
            with self.assertRaisesRegex(AssertionError, "unresolved local links in docs/invariants.md"):
                self.test_cross_file_links_resolve_in_readme_and_its_linked_guides()
            guide_path.write_text("# Guide\n[working](#guide)\n", encoding="utf-8")
            self.test_cross_file_links_resolve_in_readme_and_its_linked_guides()

    def test_cross_file_links_resolve_in_readme_and_its_linked_guides(self):
        readme = read_readme()
        readme_path = Path(ROOT) / "README.md"
        self.assertEqual([], cross_file_link_errors(readme_path, readme))
        for guide in linked_guides(readme):
            guide_text = containment.read_text(f"{ROOT}/{guide}", ROOT, encoding="utf-8")
            local_errors = local_link_errors(guide_text)
            self.assertEqual([], local_errors, f"unresolved local links in {guide}: {local_errors}")
            errors = cross_file_link_errors(Path(ROOT) / guide, guide_text)
            self.assertEqual([], errors, f"unresolved links in {guide}: {errors}")


if __name__ == "__main__":
    unittest.main()
