"""The README reference-screenshot table must match the provenance record.

README's "Reference screenshots" table is the index a contributor reads to
find the right image for a surface, while
``macos8.6-screenshots/sources.txt`` is the provenance record
``tools/check_references.py`` validates. Nothing tied the two together, so an
image added to or removed from the set could leave the README listing a file
that no longer exists or omitting one that does -- the reference set is the
project's source of truth, so a stale index sends sampling work at the wrong
image. These tests derive both sides and fail when they disagree.

The same declared set must stay routed through Git LFS: README says the binary
assets are stored with Git LFS (see ``.gitattributes``), and the checker catches
an unmaterialized pointer on disk, but nothing tied the declared files to the
LFS rules. These tests also ask git for each declared file's effective
``filter`` attribute, so dropping a rule or adding an image with an unlisted
extension fails here instead of committing a raw binary.
"""

import glob
import os
import re
import unittest

import theme_install
from check_references_fixtures import CheckerTestCase
from process_assertions import assert_succeeded

_TOKEN = re.compile(r"`([^`]+)`")
_GLOB_CHARS = "*?["

# The intro states the collection's size; the table's per-row counts are pinned
# separately, but nothing ties the prose number to the provenance record.
_PROSE_COUNT = re.compile(
    r"the visual reference set for this theme:\s*(\d+)\s+images"
)


def reference_table(text):
    """Return ``(surface, count, tokens)`` for each row of README's table.

    Parsing is bounded to the ``## Reference screenshots`` section, so a later
    table elsewhere in the README cannot be mistaken for it. Rows without a
    backticked filename (the header and the ``---`` separator) are skipped.
    """
    lines = text.splitlines()
    try:
        start = next(
            index
            for index, line in enumerate(lines)
            if line.strip() == "## Reference screenshots"
        )
    except StopIteration:
        return []
    rows = []
    for line in lines[start + 1:]:
        if line.startswith("## "):
            break
        if not line.startswith("|") or "`" not in line:
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) != 3:
            continue
        surface, count, files = cells
        tokens = _TOKEN.findall(files)
        if tokens:
            rows.append((surface, count, tokens))
    return rows


def listed_files(tokens, directory):
    """Resolve each backticked *token* to the file names it names.

    A token containing a glob character is expanded against *directory* (the
    ``about_betawiki*.png`` form the table uses for a group of images); any
    other token is a literal file name.
    """
    names = []
    for token in tokens:
        if any(char in token for char in _GLOB_CHARS):
            matches = sorted(
                os.path.basename(path)
                for path in glob.glob(os.path.join(directory, token))
            )
            names.extend(matches)
        else:
            names.append(token)
    return names


def declared_files(sources_text, separator):
    """Return the file names declared in a ``sources.txt`` body.

    Mirrors the checker's line shape: one ``filename | url | label`` entry per
    line, blank and ``#`` comment lines ignored. A malformed line is left for
    ``tools/check_references.py`` to report and contributes no name here.
    """
    names = set()
    for raw in sources_text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        fields = line.split(separator)
        if len(fields) != 3:
            continue
        name = fields[0].strip()
        if name:
            names.add(name)
    return names


def lfs_filter_states(output):
    """Return ``{file name: filter state}`` from ``git check-attr`` output.

    ``git check-attr filter -- <paths>`` prints one
    ``<path>: filter: <state>`` line per path. The file name is keyed so the
    caller can match it against the names ``sources.txt`` declares; a line
    without the ``: filter: `` separator (a git warning, say) contributes
    nothing.
    """
    states = {}
    for line in output.splitlines():
        path, separator, state = line.partition(": filter: ")
        if separator:
            states[os.path.basename(path)] = state
    return states


class TestReferenceTableParser(unittest.TestCase):
    """Pin the parser's rules on a synthetic README."""

    _TEXT = (
        "## Reference screenshots\n\n"
        "| Surface | Count | Files |\n"
        "| --- | --- | --- |\n"
        "| Desktop | 2 | `a.png`, `b*.png` (1) |\n"
        "\n"
        "## Next section\n\n"
        "| Other | 1 | `ignored.png` |\n"
    )

    def test_reads_only_the_reference_section(self):
        self.assertEqual(
            reference_table(self._TEXT),
            [("Desktop", "2", ["a.png", "b*.png"])],
        )

    def test_missing_section_yields_no_rows(self):
        self.assertEqual(reference_table("# Title\n"), [])


class TestReadmeReferenceTable(CheckerTestCase):
    """README's table must list exactly the images sources.txt declares."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.directory = os.path.join(
            theme_install.ROOT, cls.checker.REFERENCE_DIR
        )
        with open(
            os.path.join(theme_install.ROOT, "README.md"), encoding="utf-8"
        ) as handle:
            cls.text = handle.read()
        cls.rows = reference_table(cls.text)
        # The checker reads sources.txt as UTF-8 with an optional BOM; match it
        # so a BOM does not glue itself to the first declared file name.
        with open(
            os.path.join(cls.directory, cls.checker.SOURCES_NAME),
            encoding="utf-8-sig",
        ) as handle:
            cls.declared = declared_files(handle.read(), cls.checker.SEPARATOR)

    def test_table_is_present(self):
        # A README restructuring that drops the table would make the coverage
        # assertion below compare an empty set; this names the cause instead.
        self.assertTrue(self.rows, "README has no reference-screenshot table")

    def test_each_row_count_matches_its_files(self):
        for surface, count, tokens in self.rows:
            with self.subTest(surface=surface):
                self.assertRegex(count, r"^\d+$", "count is not an integer")
                names = listed_files(tokens, self.directory)
                self.assertEqual(len(names), int(count), f"{surface} count")

    def test_table_covers_the_declared_reference_set(self):
        listed = []
        for _, _, tokens in self.rows:
            listed.extend(listed_files(tokens, self.directory))
        self.assertEqual(
            len(listed), len(set(listed)), "an image is listed more than once"
        )
        self.assertEqual(set(listed), self.declared)

    def test_prose_count_matches_the_declared_set(self):
        # The intro says how many images the collection holds, and the label
        # below marks the 8.5 supplement, beta builds and photos; adding or
        # removing an image updates the table but can leave the prose count
        # stale. Derive the number from sources.txt and require the prose to
        # state it, so the two cannot drift apart silently.
        match = _PROSE_COUNT.search(self.text)
        self.assertIsNotNone(
            match, "README no longer states the reference-set image count"
        )
        self.assertEqual(int(match.group(1)), len(self.declared))


class TestLfsFilterStates(unittest.TestCase):
    """Pin the ``git check-attr`` output parser."""

    def test_reads_the_state_per_file(self):
        self.assertEqual(
            lfs_filter_states(
                "macos8.6-screenshots/about_betawiki.png: filter: lfs\n"
                "macos8.6-screenshots/sherlock_fandom.jpg: filter: "
                "unspecified\n"
            ),
            {
                "about_betawiki.png": "lfs",
                "sherlock_fandom.jpg": "unspecified",
            },
        )

    def test_ignores_a_line_without_the_separator(self):
        self.assertEqual(lfs_filter_states("warning: not an attribute\n"), {})


class TestReferenceLfsTracking(CheckerTestCase):
    """Every image ``sources.txt`` declares must be routed through Git LFS."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.relative_dir = cls.checker.REFERENCE_DIR
        with open(
            os.path.join(theme_install.ROOT, cls.relative_dir, cls.checker.SOURCES_NAME),
            encoding="utf-8-sig",
        ) as handle:
            cls.declared = declared_files(handle.read(), cls.checker.SEPARATOR)

    def test_every_declared_file_is_routed_through_lfs(self):
        # Ask git for the effective attribute rather than re-implementing its
        # pattern matching, so a directory-scoped rule or a later override is
        # honoured. The paths are relative to the repository root, matching
        # the working-tree .gitattributes git reads.
        paths = [
            os.path.join(self.relative_dir, name)
            for name in sorted(self.declared)
        ]
        result = theme_install.run_captured(
            ["git", "check-attr", "filter", "--", *paths],
            cwd=theme_install.ROOT,
        )
        assert_succeeded(self, result)
        states = lfs_filter_states(result.stdout)
        for name in sorted(self.declared):
            with self.subTest(file=name):
                self.assertEqual(
                    states.get(name),
                    "lfs",
                    f"{name} is not routed through Git LFS by .gitattributes",
                )


if __name__ == "__main__":
    unittest.main()
