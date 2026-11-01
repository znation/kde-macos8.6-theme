"""Focused tests for Firefox profile publication rollback."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from tools import firefox_transaction


class TestPublishInstall(unittest.TestCase):
    def test_failed_user_js_write_preserves_a_concurrent_edit_and_restores_sheets(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sheet = root / "userChrome.css"
            second_sheet = root / "userContent.css"
            user_js = root / "user.js"
            sheet.write_bytes(b"previous chrome")
            second_sheet.write_bytes(b"previous content")
            user_js.write_text("previous preferences\n", encoding="utf-8")

            real_write_text = firefox_transaction.write_profile_text

            def fail_after_concurrent_edit(path: Path, published: str) -> None:
                if path == user_js:
                    path.write_text("concurrent preferences\n", encoding="utf-8")
                    raise OSError("simulated publication failure")
                real_write_text(path, published)

            with mock.patch.object(
                firefox_transaction, "write_profile_text", fail_after_concurrent_edit
            ):
                with self.assertRaisesRegex(OSError, "simulated publication failure"):
                    firefox_transaction.publish_install(
                        (
                            (sheet, b"new chrome", "previous chrome"),
                            (second_sheet, b"new content", "previous content"),
                        ),
                        user_js,
                        "previous preferences\n",
                        "published preferences\n",
                    )

            self.assertEqual(b"previous chrome", sheet.read_bytes())
            self.assertEqual(b"previous content", second_sheet.read_bytes())
            self.assertEqual(
                "concurrent preferences\n", user_js.read_text(encoding="utf-8")
            )


if __name__ == "__main__":
    unittest.main()
