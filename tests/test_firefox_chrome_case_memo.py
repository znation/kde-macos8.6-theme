"""Tests for the Firefox sheet fixtures' per-process memo.

The chrome and content base cases read the same shipped sheet in every
derived class's ``setUpClass`` -- the Library chrome module and the
Preferences content module each derive six classes. The memo keeps the
read -- and, for the chrome case, the parse -- to the first
``setUpClass`` of a worker process. These tests pin that the shared
fixture equals a direct read-and-parse and that the memo is keyed once
for every derived class.

The memo globals are saved and restored around each test so the pin
stays order-independent when the whole suite runs in one process.
"""

from __future__ import annotations

import unittest
from unittest import mock

from support import containment
import support.firefox_chrome_cases as chrome_cases
import support.firefox_content_cases as content_cases
from support.firefox_chrome_cases import FirefoxChromeTestCase
from support.firefox_content_cases import FirefoxContentTestCase
from support.repo_root import ROOT


def _snapshot_memo():
    """Return both Firefox case modules' memoized fixture attributes."""
    return (chrome_cases._chrome_fixture, content_cases._content_fixture)


def _restore_memo(snapshot):
    """Write a :func:`_snapshot_memo` pair back into the case modules."""
    chrome_cases._chrome_fixture, content_cases._content_fixture = snapshot


def _fresh_chrome_classes():
    """Return two fresh FirefoxChromeTestCase subclasses."""
    return (type("ProbeChromeOne", (FirefoxChromeTestCase,), {}),
            type("ProbeChromeTwo", (FirefoxChromeTestCase,), {}))


def _fresh_content_classes(first_url, second_url):
    """Return two fresh FirefoxContentTestCase subclasses with distinct AT_RULE_URLs."""
    return (type("ProbeContentOne", (FirefoxContentTestCase,),
                 {"AT_RULE_URL": first_url}),
            type("ProbeContentTwo", (FirefoxContentTestCase,),
                 {"AT_RULE_URL": second_url}))


class CountingRead:
    """Count calls without replacing the real read's behaviour."""

    def __init__(self):
        self.real = containment.read_text
        self.count = 0

    def __call__(self, relative, root, *, encoding):
        self.count += 1
        return self.real(relative, root, encoding=encoding)


class CountingParse:
    """Count ``parse_css`` calls without replacing its behaviour."""

    def __init__(self, real, counter):
        self.real = real
        self.counter = counter

    def __call__(self, text, *, source):
        self.counter["parse"] += 1
        return self.real(text, source=source)


class SheetFixtureMemo(unittest.TestCase):
    """Pin the shared-fixture memo on both Firefox sheet base cases."""

    def setUp(self):
        self._snapshot = _snapshot_memo()
        _restore_memo((None, None))

    def tearDown(self):
        _restore_memo(self._snapshot)

    def test_chrome_fixture_is_read_and_parsed_once_and_shared(self):
        reads, parse_calls = CountingRead(), {"parse": 0}
        parse = CountingParse(chrome_cases.parse_css, parse_calls)
        first, second = _fresh_chrome_classes()
        with (
            mock.patch.object(containment, "read_text", reads),
            mock.patch.object(chrome_cases, "parse_css", parse),
        ):
            first.setUpClass()
            second.setUpClass()
        self.assertEqual(parse_calls["parse"], 1)
        # The sheet read plus the corpus read (README and the guides it links).
        self.assertEqual(reads.count, 6)
        self.assertIs(first.text, second.text)
        self.assertIs(first.readme, second.readme)
        self.assertIs(first.rules, second.rules)
        self.assertIs(first.selectors, second.selectors)

    def test_content_fixture_is_read_once_and_shared_between_urls(self):
        reads = CountingRead()
        first, second = _fresh_content_classes("about:downloads",
                                               "about:config")
        with mock.patch.object(containment, "read_text", reads):
            first.setUpClass()
            second.setUpClass()
        self.assertEqual(reads.count, 1)
        self.assertIs(first.text, second.text)
        self.assertIs(first.bodies, second.bodies)


class FreshDerivation(unittest.TestCase):
    """Pin that memoized fixtures match a direct read-and-parse."""

    def setUp(self):
        self._snapshot = _snapshot_memo()
        _restore_memo((None, None))

    def tearDown(self):
        _restore_memo(self._snapshot)

    def test_chrome_fresh_derivation_matches_a_direct_read(self):
        chrome, _ = _fresh_chrome_classes()
        chrome.setUpClass()
        direct_sheet = containment.read_text(
            chrome_cases.SHEET, ROOT, encoding="utf-8"
        )
        self.assertEqual(chrome.text, direct_sheet)
        self.assertIs(chrome.text, chrome_cases._chrome_fixture[0])
        self.assertTrue(chrome.rules, "the memoized rule map is empty")
        self.assertTrue(chrome.selectors, "the memoized selector map is empty")
        self.assertIn(":root", chrome.selectors)

    def test_content_fresh_split_matches_a_direct_read(self):
        content, _ = _fresh_content_classes("about:downloads", "about:config")
        content.setUpClass()
        direct_sheet = containment.read_text(
            content_cases.SHEET, ROOT, encoding="utf-8"
        )
        self.assertEqual(content.text, direct_sheet)
        self.assertIs(content.text, content_cases._content_fixture[0])
        self.assertIn("about:downloads", content.bodies)
        self.assertIn("about:config", content.bodies)


if __name__ == "__main__":
    unittest.main()
