"""Test the user-docs corpus reader over README.md and the guides it links."""

from __future__ import annotations

import unittest

from support import containment
from support.repo_root import ROOT
from support.tmp_dir import make_tmp_dir
from support.user_docs import linked_guides, prose_lines, read_user_docs


def _readme_linking(guide_link: str) -> str:
    return f"# Title\n\nSee [the guide]({guide_link}) for details.\n"


class TestLinkedGuides(unittest.TestCase):
    def test_repeated_and_anchored_links_to_one_guide_are_listed_once(self):
        text = "[a](docs/principles-rationale.md) [b](docs/principles-rationale.md#x) [c](docs/principles-rationale.md)"
        self.assertEqual(["docs/principles-rationale.md"], linked_guides(text))

    def test_guides_are_listed_in_first_seen_order(self):
        text = "[b](docs/principles-rationale.md) then [a](docs/invariants.md) then [b again](docs/principles-rationale.md#y)"
        self.assertEqual(["docs/principles-rationale.md", "docs/invariants.md"], linked_guides(text))

    def test_link_inside_a_fenced_code_block_is_ignored(self):
        text = "~~~md\n[fenced](docs/invariants.md)\n~~~\n[real](docs/principles-rationale.md)\n```md\n[also fenced](docs/invariants.md)\n```\n"
        self.assertEqual(["docs/principles-rationale.md"], linked_guides(text))

    def test_non_relative_targets_are_ignored(self):
        text = "[web](https://example.com/elsewhere/b.md) [local](#frag) [other](../docs/elsewhere.md)"
        self.assertEqual([], linked_guides(text))


class TestProseLines(unittest.TestCase):
    def test_fences_exclude_their_lines_for_both_markers(self):
        # An opener and its closer must share a character, and the closer
        # must be at least as long as the opener: a shorter `` inside an
        # open ``` fence stays hidden, while a longer ~~~~ closes a ~~~.
        text = (
            "before\n"
            "```py\n"
            "hidden\n"
            "``\n"
            "```\n"
            "shown\n"
            "~~~\n"
            "hidden too\n"
            "~~~~\n"
            "after\n"
        )
        self.assertEqual(["before", "shown", "after"], list(prose_lines(text)))

    def test_a_fence_of_the_other_character_inside_an_open_fence_is_hidden(self):
        # While a ``` fence is open, a ~~~ line neither closes nor switches
        # the fence, and prose resumes only after the matching ``` closer.
        text = "before\n```\n~~~\nstill hidden\n```\nshown\n"
        self.assertEqual(["before", "shown"], list(prose_lines(text)))


class TestReadUserDocs(unittest.TestCase):
    def test_joins_readme_and_its_linked_guides_with_blank_lines(self):
        root = make_tmp_dir(self)
        (root / "docs").mkdir()
        readme = _readme_linking("docs/principles-rationale.md")
        (root / "README.md").write_text(readme, encoding="utf-8")
        (root / "docs" / "principles-rationale.md").write_text("# Guide\n\nBody.\n", encoding="utf-8")
        self.assertEqual(
            readme + "\n\n" + "# Guide\n\nBody.\n",
            read_user_docs(root),
        )

    def test_on_this_repository_readme_links_the_installed_guides(self):
        readme = containment.read_text(f"{ROOT}/README.md", ROOT, encoding="utf-8")
        self.assertEqual(
            ["docs/rendering.md", "docs/installing.md", "docs/sampling.md"],
            linked_guides(readme),
        )
        parts = [readme]
        for guide in ("docs/rendering.md", "docs/installing.md", "docs/sampling.md"):
            parts.append(
                containment.read_text(f"{ROOT}/{guide}", ROOT, encoding="utf-8")
            )
        self.assertEqual("\n\n".join(parts), read_user_docs())

    def test_a_symlinked_guide_that_escapes_the_repository_is_refused(self):
        root = make_tmp_dir(self)
        outside = root.parent / f"outside-{root.name}.md"
        self.addCleanup(outside.unlink, missing_ok=True)
        outside.write_text("secret\n", encoding="utf-8")
        (root / "docs").mkdir()
        (root / "README.md").write_text(_readme_linking("docs/principles-rationale.md"), encoding="utf-8")
        (root / "docs" / "principles-rationale.md").symlink_to(outside)
        with self.assertRaises(ValueError):
            read_user_docs(root)


if __name__ == "__main__":
    unittest.main()
