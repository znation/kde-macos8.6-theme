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

from package_metadata import PackageMetadata, kplugin, load_metadata


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
            "Authors": [{"Name": "kde-macos8.6-theme"}],
        },
        "X-Plasma-API": "5.0",
        "Keywords": "Desktop;Workspace;Appearance;",
    }


def _metadata_with_kplugin(value):
    """A fresh metadata dict whose ``KPlugin`` is *value*.

    ``None`` removes the key, matching a metadata.json that never had one;
    anything else replaces the default object so a guard sees the malformed
    value. The guard tests below that walk a table of malformed ``KPlugin``
    values share this convention here.
    """
    metadata = _metadata()
    if value is None:
        del metadata["KPlugin"]
    else:
        metadata["KPlugin"] = value
    return metadata


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
    def _load_error(self, path):
        """Assert `load_metadata` rejects *path* and return the raised ValueError."""
        with self.assertRaises(ValueError) as caught:
            load_metadata(path)
        return caught.exception

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
            error = self._load_error(path)
        message = str(error)
        self.assertIn(str(path), message)
        self.assertIn("invalid JSON", message)
        self.assertIn("line 2", message)
        self.assertIsInstance(error.__cause__, json.JSONDecodeError)

    def test_non_utf8_bytes_name_the_path_and_keep_the_detail(self):
        # A metadata.json saved in another encoding (say Latin-1) or corrupted
        # mid-write raises a bare UnicodeDecodeError from the read that names
        # the byte but neither of the two packages' files; the guard must add
        # the path and keep the decoder's own byte detail (and its cause).
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "metadata.json"
            path.write_bytes(b'{"Name": "Caf\xff"}')
            error = self._load_error(path)
        message = str(error)
        self.assertIn(str(path), message)
        self.assertIn("UTF-8", message)
        self.assertIn("0xff", message)
        self.assertIsInstance(error.__cause__, UnicodeDecodeError)

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
                    error = self._load_error(path)
                message = str(error)
                self.assertIn(decoded_type, message)
                self.assertIn(str(path), message)


class TestKPluginHelper(unittest.TestCase):
    """The shared `KPlugin` guard used by the mixin and the wiring check.

    `PackageMetadata._plugin` and `test_desktoptheme`'s defaults-wiring check
    both read `KPlugin`; pin the shared guard's message directly so either
    caller names the file and the offending type on a malformed metadata.json.
    """

    def test_returns_the_kplugin_object(self):
        self.assertEqual(
            kplugin(_metadata(), "metadata.json"), _metadata()["KPlugin"]
        )

    def test_names_the_path_and_type_when_not_an_object(self):
        for value, type_name in (
            (None, "NoneType"),
            ("text", "str"),
            ([], "list"),
            (7, "int"),
        ):
            with self.subTest(kplugin=value):
                metadata = _metadata_with_kplugin(value)
                with self.assertRaises(ValueError) as caught:
                    kplugin(metadata, "metadata.json")
                message = str(caught.exception)
                self.assertIn("metadata.json", message)
                self.assertIn("KPlugin", message)
                self.assertIn(type_name, message)


class TestPackageMetadata(unittest.TestCase):
    def _guard_message(self, method, metadata):
        """Return the AssertionError message from guard *method* on *metadata*.

        Build a `PackageMetadata` case for *method* and run it against the
        deliberately broken *metadata*; the guard must reject it. Return the
        message so the caller can assert the file and field it names.
        """
        with self.assertRaises(AssertionError) as caught:
            getattr(_case(method, metadata), method)()
        return str(caught.exception)

    def _assert_guard_names(self, method, metadata, *names):
        """Assert guard *method* rejects *metadata*, naming the file and *names*.

        Every guard message names the ``metadata.json`` it came from so the
        two packages' failures are distinguishable, plus the field or field
        path it rejected. This wraps `_guard_message` for the cases that pin
        both, so the file name is asserted in one place.
        """
        message = self._guard_message(method, metadata)
        self.assertIn("metadata.json", message)
        for name in names:
            self.assertIn(name, message)
        return message

    def test_accepts_well_formed_metadata(self):
        # Positive control: every guard passes on the shape the real packages
        # use, so a guard that rejects everything cannot pass the failure
        # cases below by accident.
        metadata = _metadata()
        for method in (
            "test_package_structure",
            "test_plugin_id_and_name",
            "test_plugin_version",
            "test_plugin_authors_are_named",
            "test_plasma_api_version",
            "test_plugin_description_and_license_are_non_empty",
        ):
            with self.subTest(method=method):
                case = _case(method, metadata)
                getattr(case, method)()

    def test_package_structure_guard(self):
        metadata = _metadata()
        metadata["KPackageStructure"] = "Plasma/LookAndFeel"
        self._guard_message("test_package_structure", metadata)

    def test_top_level_key_missing_names_the_file_and_field(self):
        # A metadata.json that drops a top-level key used to fail as
        # ``None != expected``, naming neither the file nor the key; the mixin
        # must name both.
        for key, method in (
            ("KPackageStructure", "test_package_structure"),
            ("X-Plasma-API", "test_plasma_api_version"),
        ):
            with self.subTest(key=key):
                metadata = _metadata()
                del metadata[key]
                self._assert_guard_names(method, metadata, key)

    def test_top_level_key_mismatch_names_the_file(self):
        # The mismatch case used to report only the two values; label it with
        # the metadata.json the value came from.
        metadata = _metadata()
        metadata["KPackageStructure"] = "Plasma/LookAndFeel"
        self._assert_guard_names("test_package_structure", metadata)

    def test_top_level_field_returns_the_value(self):
        case = _case("test_package_structure", _metadata())
        self.assertEqual(
            case._top_level_field("Keywords"), _metadata()["Keywords"]
        )

    def test_top_level_field_missing_names_the_file_and_field(self):
        # `test_lookandfeel`'s `test_keywords_non_empty` reads Keywords through
        # this helper; a metadata.json that drops it used to fail as ``None is
        # not true``, naming neither the file nor the key.
        metadata = _metadata()
        del metadata["Keywords"]
        with self.assertRaises(AssertionError) as caught:
            _case(
                "test_package_structure", metadata
            )._top_level_field("Keywords")
        message = str(caught.exception)
        self.assertIn("metadata.json", message)
        self.assertIn("Keywords", message)

    def test_kplugin_guard_names_the_file_and_field(self):
        # A metadata.json that decodes to an object but whose KPlugin is
        # missing or not an object used to fail with a bare KeyError/TypeError
        # naming neither the file nor the field; the mixin must name both.
        for value in (None, "text", [], 7):
            with self.subTest(kplugin=value):
                metadata = _metadata_with_kplugin(value)
                for method in (
                    "test_plugin_id_and_name",
                    "test_plugin_version",
                    "test_plugin_authors_are_named",
                    "test_plugin_description_and_license_are_non_empty",
                ):
                    with self.subTest(method=method):
                        self._assert_guard_names(method, metadata, "KPlugin")

    def test_plugin_id_and_name_guard(self):
        for key, value in (("Id", "org.other.desktop"), ("Name", "Something")):
            with self.subTest(key=key):
                metadata = _metadata()
                metadata["KPlugin"][key] = value
                self._guard_message("test_plugin_id_and_name", metadata)

    def test_plugin_id_and_name_missing_key_names_the_file_and_field(self):
        # A metadata.json whose KPlugin drops Id or Name used to fail with a
        # bare KeyError naming only the key, with neither the file nor the
        # expected value; the mixin must name the file and the field.
        for key in ("Id", "Name"):
            with self.subTest(key=key):
                metadata = _metadata()
                del metadata["KPlugin"][key]
                self._assert_guard_names(
                    "test_plugin_id_and_name", metadata, key
                )

    def test_plugin_string_field_missing_names_the_file_and_field(self):
        # A metadata.json whose KPlugin drops Version, Description or License
        # used to fail as a ``None`` type check naming neither the file nor
        # the field's parent; the mixin must name the file and the field.
        for key, method in (
            ("Version", "test_plugin_version"),
            ("Description", "test_plugin_description_and_license_are_non_empty"),
            ("License", "test_plugin_description_and_license_are_non_empty"),
        ):
            with self.subTest(key=key):
                metadata = _metadata()
                del metadata["KPlugin"][key]
                self._assert_guard_names(method, metadata, key)

    def test_plugin_version_guard(self):
        for value in (None, "", "   ", 7):
            with self.subTest(version=value):
                metadata = _metadata()
                metadata["KPlugin"]["Version"] = value
                self._assert_guard_names("test_plugin_version", metadata)

    def test_plasma_api_version_guard(self):
        metadata = _metadata()
        metadata["X-Plasma-API"] = "6.0"
        self._guard_message("test_plasma_api_version", metadata)

    def test_description_and_license_guard(self):
        for key in ("Description", "License"):
            for value in (None, "", "   ", 7):
                with self.subTest(key=key, value=value):
                    metadata = _metadata()
                    metadata["KPlugin"][key] = value
                    self._assert_guard_names(
                        "test_plugin_description_and_license_are_non_empty",
                        metadata,
                    )

    def test_plugin_authors_guard(self):
        # Both packages ship Authors as a list of named objects, but nothing
        # pinned that shape. A metadata.json that drops the field used to be
        # ignored entirely; one whose Authors is not a list, is empty, holds a
        # non-object entry, or blanks an entry's Name installs cleanly too, so
        # pin each rejection with the file and the offending field.
        metadata = _metadata()
        del metadata["KPlugin"]["Authors"]
        self._assert_guard_names(
            "test_plugin_authors_are_named", metadata, "Authors"
        )

        for value in (None, "text", 7):
            with self.subTest(authors=value):
                metadata = _metadata()
                metadata["KPlugin"]["Authors"] = value
                self._assert_guard_names(
                    "test_plugin_authors_are_named", metadata, "Authors"
                )

        metadata = _metadata()
        metadata["KPlugin"]["Authors"] = []
        self._assert_guard_names(
            "test_plugin_authors_are_named", metadata, "Authors"
        )

        for author in ("text", 7, {"Name": ""}, {"Name": "   "}, {"Name": 7}, {}):
            with self.subTest(author=author):
                metadata = _metadata()
                metadata["KPlugin"]["Authors"] = [author]
                self._assert_guard_names(
                    "test_plugin_authors_are_named", metadata, "Authors[0]"
                )


if __name__ == "__main__":
    unittest.main()
