"""Focused tests for Firefox profile publication rollback."""

from __future__ import annotations

import tempfile
import unittest
from errno import EPERM
from pathlib import Path
from unittest import mock

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from tools.firefox import profile_actions as firefox_profile_actions
from tools.firefox import transaction as firefox_transaction


class TestPublishInstall(unittest.TestCase):
    def test_removal_rollback_checks_sheets_after_restoring_preferences(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sheet = root / "userChrome.css"
            user_js = root / "user.js"
            real_write = firefox_profile_actions.write_profile_text

            def restore_preferences(path, text):
                real_write(path, text)
                if path == user_js:
                    sheet.write_text("concurrent sheet", encoding="utf-8")

            with mock.patch.object(
                firefox_profile_actions, "write_profile_text", restore_preferences
            ):
                errors = firefox_profile_actions._restore_removed_files(
                    [(sheet, "previous sheet")], user_js, "previous preferences", True
                )

            self.assertEqual(errors, [])
            self.assertEqual(user_js.read_text(encoding="utf-8"), "previous preferences")
            self.assertEqual(sheet.read_text(encoding="utf-8"), "concurrent sheet")

    def test_rollback_error_collection_continues_after_a_refusal(self):
        attempted = []

        def refused():
            attempted.append("refused")
            raise firefox_transaction.ConfigError("cannot restore first")

        def succeeds():
            attempted.append("succeeded")

        errors = firefox_transaction.collect_rollback_errors((refused, succeeds))

        self.assertEqual(attempted, ["refused", "succeeded"])
        self.assertEqual(errors, ["cannot restore first"])

    def test_a_created_sheet_with_no_previous_is_removed_on_rollback(self):
        # A sheet the transaction itself created (no previous file) must not
        # survive a later sheet's failure: publish_install restores "the
        # published state on any failure", and for a created file that state
        # is absence, not a partial theme half the sheets of.
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first = root / "userChrome.css"
            second = root / "userContent.css"
            user_js = root / "user.js"

            def fail_on_second(path: Path, data: bytes) -> None:
                if path == second:
                    raise OSError("simulated publication failure")
                firefox_transaction.write_profile_bytes(path, data)

            with self.assertRaisesRegex(OSError, "simulated publication failure"):
                firefox_transaction.publish_install(
                    ((first, b"new chrome", None), (second, b"new content", None)),
                    user_js,
                    None,
                    "published preferences\n",
                    write_operation=fail_on_second,
                )

            self.assertFalse(first.exists())
            self.assertFalse(second.exists())
            self.assertFalse(user_js.exists())

    def test_a_rollback_that_cannot_remove_collects_its_refusal_into_the_error(
        self,
    ):
        # The rollback's own failure must reach the operator too: the raised
        # ConfigError carries the publication failure and every rollback
        # refusal, naming the path, with the original failure as its cause.
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first = root / "userChrome.css"
            second = root / "userContent.css"

            def fail_on_second(path: Path, data: bytes) -> None:
                if path == second:
                    raise OSError("simulated publication failure")
                firefox_transaction.write_profile_bytes(path, data)

            with mock.patch.object(
                Path, "unlink", side_effect=OSError(EPERM, "simulated refusal")
            ):
                with self.assertRaises(firefox_transaction.ConfigError) as caught:
                    firefox_transaction.publish_install(
                        ((first, b"new chrome", None), (second, b"new content", None)),
                        root / "user.js",
                        None,
                        "published preferences\n",
                        write_operation=fail_on_second,
                    )

            message = str(caught.exception)
            self.assertIn("simulated publication failure", message)
            self.assertIn(f"cannot restore {first}", message)
            self.assertIn("simulated refusal", message)
            self.assertTrue(isinstance(caught.exception.__cause__, OSError))

    def test_a_failed_write_that_published_our_text_restores_the_previous_user_js(
        self,
    ):
        # A publication failure can land after the write itself succeeded
        # (a report, a rename flag, anything the publisher raises once the
        # bytes are out). The previous user.js must come back whenever what
        # the failed run left behind is exactly the text this run meant to
        # publish -- and never a concurrent edit, which the other test pins.
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sheet = root / "userChrome.css"
            user_js = root / "user.js"
            user_js.write_text("previous preferences\n", encoding="utf-8")

            real_write_text = firefox_transaction.write_profile_text
            state = {"failed": False}

            def publish_then_fail(path: Path, published: str) -> None:
                if path == user_js and not state["failed"]:
                    real_write_text(path, published)
                    state["failed"] = True
                    raise OSError("simulated publication failure")
                real_write_text(path, published)

            with mock.patch.object(
                firefox_transaction, "write_profile_text", publish_then_fail
            ):
                with self.assertRaisesRegex(OSError, "simulated publication failure"):
                    firefox_transaction.publish_install(
                        ((sheet, b"new chrome", "previous chrome"),),
                        user_js,
                        "previous preferences\n",
                        "published preferences\n",
                    )

            self.assertEqual(b"previous chrome", sheet.read_bytes())
            self.assertEqual(
                "previous preferences\n", user_js.read_text(encoding="utf-8")
            )

    def test_a_user_js_the_transaction_created_is_removed_when_its_write_completes(self):
        # user.js did not exist before the run. The publication write completes
        # and then the publisher raises: the published state for a file that
        # had no previous version is absence, so the rollback must remove the
        # user.js it just wrote, and the sheet it created must go too.
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sheet = root / "userChrome.css"
            user_js = root / "user.js"

            real_write_text = firefox_transaction.write_profile_text

            def publish_then_fail(path: Path, published: str) -> None:
                if path == user_js:
                    real_write_text(path, published)
                    raise OSError("simulated publication failure")
                real_write_text(path, published)

            with mock.patch.object(
                firefox_transaction, "write_profile_text", publish_then_fail
            ):
                with self.assertRaisesRegex(OSError, "simulated publication failure"):
                    firefox_transaction.publish_install(
                        ((sheet, b"new chrome", None),),
                        user_js,
                        None,
                        "published preferences\n",
                    )

            self.assertFalse(sheet.exists())
            self.assertFalse(user_js.exists())

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

    def test_an_interrupt_mid_publication_rolls_back_and_propagates(self):
        # The rollback runs on any failure, an interrupt included: publish_install
        # would otherwise leave sheets the interrupted run already wrote, and no
        # user.js -- a half-published profile. The interrupt itself must reach the
        # caller unchanged (a bare re-raise, not a ConfigError wrap).
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first = root / "userChrome.css"
            second = root / "userContent.css"
            user_js = root / "user.js"

            def interrupt_on_second(path: Path, data: bytes) -> None:
                if path == second:
                    raise KeyboardInterrupt
                firefox_transaction.write_profile_bytes(path, data)

            with self.assertRaises(KeyboardInterrupt):
                firefox_transaction.publish_install(
                    ((first, b"new chrome", None), (second, b"new content", None)),
                    user_js,
                    None,
                    "published preferences\n",
                    write_operation=interrupt_on_second,
                )

            self.assertFalse(first.exists())
            self.assertFalse(second.exists())
            self.assertFalse(user_js.exists())

    def test_a_user_js_rollback_refusal_is_collected_into_the_error(self):
        # A refusal while restoring user.js must join the report, not mask
        # the publication failure: publish_install wraps the user.js restore
        # in its own refusal collector, so the rollback finishes (the previous
        # sheets are already back) and the raise carries the publication
        # failure first, then the cannot-restore refusal, with the original
        # failure as its cause.
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sheet = root / "userChrome.css"
            user_js = root / "user.js"
            sheet.write_bytes(b"previous chrome")

            real_write_text = firefox_transaction.write_profile_text
            state = {"failed": False}

            def publish_then_fail(path: Path, published: str) -> None:
                if path == user_js and not state["failed"]:
                    real_write_text(path, published)
                    state["failed"] = True
                    raise OSError("simulated publication failure")
                real_write_text(path, published)

            with mock.patch.object(
                firefox_transaction, "write_profile_text", publish_then_fail
            ), mock.patch.object(
                Path, "unlink", side_effect=OSError(EPERM, "simulated refusal")
            ):
                with self.assertRaises(
                    firefox_transaction.ConfigError
                ) as caught:
                    firefox_transaction.publish_install(
                        ((sheet, b"new chrome", "previous chrome"),),
                        user_js,
                        None,
                        "published preferences\n",
                    )

            message = str(caught.exception)
            self.assertIn("simulated publication failure", message)
            self.assertIn(f"cannot restore {user_js}", message)
            self.assertIn("simulated refusal", message)
            self.assertTrue(isinstance(caught.exception.__cause__, OSError))
            # The rollback reached the end despite the refusal: the sheet got
            # its previous text back before the user.js restore was attempted.
            self.assertEqual(b"previous chrome", sheet.read_bytes())

    def test_an_unreadable_published_user_js_collects_its_refusal_into_the_error(
        self,
    ):
        # The user.js restore reads the path first: it must see the published
        # text before it removes or rewrites anything. A concurrent program
        # clobbering the file with non-UTF-8 bytes after the failed publication
        # write took effect makes that read refuse with "cannot read"
        # (invalid UTF-8), not remove a file the operator could inspect. The
        # refusal joins the report as its own record instead of masking the
        # publication failure or aborting the rollback: the previous sheets
        # are already written back when the message arrives, the publication
        # failure leads the records, the read refusal follows, and the original
        # failure stays the cause.
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sheet = root / "userChrome.css"
            user_js = root / "user.js"
            sheet.write_bytes(b"previous chrome")

            real_write_text = firefox_transaction.write_profile_text
            state = {"failed": False}

            def publish_then_clobber(path: Path, published: str) -> None:
                if path == user_js and not state["failed"]:
                    real_write_text(path, published)
                    state["failed"] = True
                    path.write_bytes(b"\xff\xfe")
                    raise OSError("simulated publication failure")
                real_write_text(path, published)

            with mock.patch.object(
                firefox_transaction, "write_profile_text", publish_then_clobber
            ):
                with self.assertRaises(
                    firefox_transaction.ConfigError
                ) as caught:
                    firefox_transaction.publish_install(
                        ((sheet, b"new chrome", "previous chrome"),),
                        user_js,
                        None,
                        "published preferences\n",
                    )

            message = str(caught.exception)
            self.assertTrue(
                message.startswith("simulated publication failure; "), message
            )
            self.assertIn(f"cannot read {user_js}", message)
            self.assertTrue(isinstance(caught.exception.__cause__, OSError))
            # The rollback finished: the sheet carries its previous text while
            # the unloaded read leaves the clobbered bytes in place.
            self.assertEqual(b"previous chrome", sheet.read_bytes())
            self.assertEqual(b"\xff\xfe", user_js.read_bytes())

    def test_a_reinstall_over_identical_user_js_skips_its_restore(self):
        # When user.js already held exactly the text this run publishes, a
        # failed publication leaves nothing to undo for user.js: the rollback
        # neither reads nor rewrites it, so a file clobbered after the write
        # cannot produce a "cannot read" refusal. The original failure reaches
        # the caller unchanged, and the sheet's previous text is still restored.
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sheet = root / "userChrome.css"
            user_js = root / "user.js"
            sheet.write_bytes(b"previous chrome")
            user_js.write_text("published preferences\n", encoding="utf-8")

            real_write_text = firefox_transaction.write_profile_text
            state = {"failed": False}

            def publish_then_clobber(path: Path, published: str) -> None:
                if path == user_js and not state["failed"]:
                    real_write_text(path, published)
                    state["failed"] = True
                    path.write_bytes(b"\xff\xfe")
                    raise OSError("simulated publication failure")
                real_write_text(path, published)

            with mock.patch.object(
                firefox_transaction, "write_profile_text", publish_then_clobber
            ):
                with self.assertRaises(OSError) as caught:
                    firefox_transaction.publish_install(
                        ((sheet, b"new chrome", "previous chrome"),),
                        user_js,
                        "published preferences\n",
                        "published preferences\n",
                    )

            self.assertNotIsInstance(caught.exception, firefox_transaction.ConfigError)
            self.assertEqual("simulated publication failure", str(caught.exception))
            self.assertEqual(b"previous chrome", sheet.read_bytes())
            self.assertEqual(b"\xff\xfe", user_js.read_bytes())


class TestRollbackRestoreRefusal(unittest.TestCase):
    def test_a_refused_restore_of_a_previous_sheet_is_collected_and_the_rest_restored(self):
        # The restore of a sheet that had previous text is a write, not an
        # unlink. When that write is refused, the refusal must be named in
        # the raised error, the other sheet must still be restored, and the
        # refused sheet keeps the text the publication wrote.
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sheet = root / "userChrome.css"
            second_sheet = root / "userContent.css"
            user_js = root / "user.js"
            sheet.write_bytes(b"previous chrome")
            second_sheet.write_bytes(b"previous content")
            user_js.write_text("previous preferences\n", encoding="utf-8")

            real_write_text = firefox_transaction.write_profile_text

            def refuse_restore_of_first_sheet(path: Path, text: str) -> None:
                if path == user_js:
                    raise OSError("simulated publication failure")
                if path == sheet:
                    raise firefox_transaction.ConfigError("simulated restore refusal")
                real_write_text(path, text)

            with mock.patch.object(
                firefox_transaction, "write_profile_text", refuse_restore_of_first_sheet
            ):
                with self.assertRaises(firefox_transaction.ConfigError) as caught:
                    firefox_transaction.publish_install(
                        (
                            (sheet, b"new chrome", "previous chrome"),
                            (second_sheet, b"new content", "previous content"),
                        ),
                        user_js,
                        "previous preferences\n",
                        "published preferences\n",
                    )

            self.assertEqual(
                "simulated publication failure; simulated restore refusal",
                str(caught.exception),
            )
            self.assertIsInstance(caught.exception.__cause__, OSError)
            self.assertEqual(b"new chrome", sheet.read_bytes())
            self.assertEqual(b"previous content", second_sheet.read_bytes())
            self.assertEqual(
                "previous preferences\n", user_js.read_text(encoding="utf-8")
            )


class TestRaiseWithRollbackErrors(unittest.TestCase):
    def test_no_rollback_errors_reraises_the_failure_itself(self):
        failure = OSError("publication failed")
        with self.assertRaises(OSError) as caught:
            firefox_transaction.raise_with_rollback_errors(failure, [])
        self.assertIs(failure, caught.exception)

    def test_rollback_errors_are_named_in_a_config_error_caused_by_the_failure(self):
        failure = OSError("publication failed")
        with self.assertRaises(firefox_transaction.ConfigError) as caught:
            firefox_transaction.raise_with_rollback_errors(
                failure, ["first refusal", "second refusal"]
            )
        self.assertEqual(
            "publication failed; first refusal; second refusal",
            str(caught.exception),
        )
        self.assertIs(failure, caught.exception.__cause__)


if __name__ == "__main__":
    unittest.main()
