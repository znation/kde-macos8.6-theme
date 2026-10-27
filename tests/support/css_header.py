"""Shared assertion for a Firefox sheet's comment-header provenance lines.

Both Firefox sheets open with a comment block that names the reference
surfaces, Firefox source files and platform adaptations each themed
section derives from. The suites testing them keep the sheet text in
``self.text`` and pin every provenance entry against the header before
the first ``*/``; this mixin holds that one assertion. Its only call
sites are ``FirefoxChromeTestCase`` (serving the provenance tests of
``tests/test_firefox_theme_shell.py``, ``tests/test_firefox_theme_panels.py``,
``tests/test_firefox_theme_popups.py`` and
``tests/test_firefox_theme_page_info.py``) and ``SheetCase`` in
``tests/test_firefox_content_theme.py``.
"""

from __future__ import annotations


def comment_header(text):
    """Return the comment block before the first ``*/`` of *text*."""
    return text.split("*/", 1)[0]


class CommentHeaderAssertions:
    """Mixin for suites whose ``self.text`` sheet has a provenance header."""

    def assert_header_names(self, provenances):
        """Assert the comment header before the first ``*/`` names each entry."""
        header = comment_header(self.text)
        for provenance in provenances:
            with self.subTest(provenance=provenance):
                self.assertIn(provenance, header)
