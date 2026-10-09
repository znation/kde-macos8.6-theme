"""Tests for tests/package_metadata.py -- the shared `metadata.json` mixin.

`test_lookandfeel` and `test_desktoptheme` each run these checks against their
own real `metadata.json`, so the passing path is exercised twice over. Every
guard, though, is only ever fed good data: a guard that stopped rejecting a
blank Description, a missing Version or a mismatched package structure would
keep both suites green. Pin each guard against deliberately broken metadata
here, and pin `load_metadata`'s explicit UTF-8 decode and JSON-object guard.
"""

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from package_metadata import PackageMetadata, load_metadata


def _metadata():
    """A minimal metadata.json that every `PackageMetadata` check accepts."""
    return {
        "KPackageStructure": "Plasma/Theme",
        "KPlugin": {
            "Id": "org.example.desktop",
            "Name": "Mac OS 8.6",
            "Description": "An example package",
            "License": "GPL-2.0-or-later",
            "Version": "0.1.0",
        },
        "X-Plasma-API": "5.0",
    }


def _case(method, metadata):
    """Return a configured `PackageMetadata` case, without running setUp.

    The subclass is built inside the function so unittest discovery does not
    collect it and run its mixin methods against the unset class attributes.
    """
    class _Case(PackageMetadata, unittest.TestCase):
        METADATA_PATH = "metadata.json"
        PACKAGE_STRUCTURE = "Plasma/Theme"
        PACKAGE_ID = "org.example.desktop"
        PLASMA_API_KEY = "X-Plasma-API"
        PLASMA_API_VERSION = "5.0"

    case = _Case(method)
    case.metadata = metadata
    return case


class TestLoadMetadata(unittest.TestCase):
    def test_reads_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "metadata.json"
            path.write_text(json.dumps(_metadata()), encoding="utf-8")
            self.assertEqual(load_metadata(path), _metadata())

    def test_values_are_read_as_utf8(self):
        # A package Description or Author name can hold non-ASCII text; the
        # file must be decoded as UTF-8 rather than the platform locale's
        # encoding. The locale here is UTF-8, so pin the argument passed to
        # open() instead.
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "metadata.json"
            path.write_text('{"Name": "Caf\u00e9"}', encoding="utf-8")
            with mock.patch("builtins.open", wraps=open) as spy:
                metadata = load_metadata(path)
        self.assertEqual(spy.call_args.kwargs.get("encoding"), "utf-8")
        self.assertEqual(metadata["Name"], "Caf\u00e9")

    def test_malformed_json_names_the_path_and_keeps_the_detail(self):
        # Two packages ship a metadata.json, so a bare JSONDecodeError names
        # neither which file is broken nor where; the guard must add the path
        # and keep the decoder's own line/column detail (and its cause).
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "metadata.json"
            path.write_text('{\n  "KPlugin": ,\n}', encoding="utf-8")
            with self.assertRaises(ValueError) as caught:
                load_metadata(path)
        message = str(caught.exception)
        self.assertIn(str(path), message)
        self.assertIn("invalid JSON", message)
        self.assertIn("line 2", message)
        self.assertIsInstance(caught.exception.__cause__, json.JSONDecodeError)

    def test_non_object_json_names_the_type_and_path(self):
        # Valid JSON of the wrong top-level shape reaches the mixin's
        # ``self.metadata.get(...)`` as a bare AttributeError; the guard must
        # name both the file and the decoded type instead.
        for text, decoded_type in (
            ("[]", "list"),
            ('"text"', "str"),
            ("42", "int"),
            ("null", "NoneType"),
        ):
            with self.subTest(json=text):
                with tempfile.TemporaryDirectory() as tmp:
                    path = Path(tmp) / "metadata.json"
                    path.write_text(text, encoding="utf-8")
                    with self.assertRaises(ValueError) as caught:
                        load_metadata(path)
                message = str(caught.exception)
                self.assertIn(decoded_type, message)
                self.assertIn(str(path), message)


class TestPackageMetadata(unittest.TestCase):
    def test_accepts_well_formed_metadata(self):
        # Positive control: every guard passes on the shape the real packages
        # use, so a guard that rejects everything cannot pass the failure
        # cases below by accident.
        metadata = _metadata()
        for method in (
            "test_package_structure",
            "test_plugin_id_and_name",
            "test_plugin_version",
            "test_plasma_api_version",
            "test_plugin_description_and_license_are_non_empty",
        ):
            with self.subTest(method=method):
                case = _case(method, metadata)
                getattr(case, method)()

    def test_package_structure_guard(self):
        metadata = _metadata()
        metadata["KPackageStructure"] = "Plasma/LookAndFeel"
        with self.assertRaises(AssertionError):
            _case("test_package_structure", metadata).test_package_structure()

    def test_kplugin_guard_names_the_file_and_field(self):
        # A metadata.json that decodes to an object but whose KPlugin is
        # missing or not an object used to fail with a bare KeyError/TypeError
        # naming neither the file nor the field; the mixin must name both.
        for value in (None, "text", [], 7):
            with self.subTest(kplugin=value):
                metadata = _metadata()
                if value is None:
                    del metadata["KPlugin"]
                else:
                    metadata["KPlugin"] = value
                for method in (
                    "test_plugin_id_and_name",
                    "test_plugin_version",
                    "test_plugin_description_and_license_are_non_empty",
                ):
                    with self.subTest(method=method):
                        with self.assertRaises(AssertionError) as caught:
                            getattr(_case(method, metadata), method)()
                        message = str(caught.exception)
                        self.assertIn("metadata.json", message)
                        self.assertIn("KPlugin", message)

    def test_plugin_id_and_name_guard(self):
        for key, value in (("Id", "org.other.desktop"), ("Name", "Something")):
            with self.subTest(key=key):
                metadata = _metadata()
                metadata["KPlugin"][key] = value
                with self.assertRaises(AssertionError):
                    _case(
                        "test_plugin_id_and_name", metadata
                    ).test_plugin_id_and_name()

    def test_plugin_version_guard(self):
        for value in (None, "", "   ", 7):
            with self.subTest(version=value):
                metadata = _metadata()
                metadata["KPlugin"]["Version"] = value
                with self.assertRaises(AssertionError):
                    _case("test_plugin_version", metadata).test_plugin_version()

    def test_plasma_api_version_guard(self):
        metadata = _metadata()
        metadata["X-Plasma-API"] = "6.0"
        with self.assertRaises(AssertionError):
            _case(
                "test_plasma_api_version", metadata
            ).test_plasma_api_version()

    def test_description_and_license_guard(self):
        for key in ("Description", "License"):
            for value in (None, "", "   ", 7):
                with self.subTest(key=key, value=value):
                    metadata = _metadata()
                    metadata["KPlugin"][key] = value
                    with self.assertRaises(AssertionError):
                        _case(
                            "test_plugin_description_and_license_are_non_empty",
                            metadata,
                        ).test_plugin_description_and_license_are_non_empty()


if __name__ == "__main__":
    unittest.main()
