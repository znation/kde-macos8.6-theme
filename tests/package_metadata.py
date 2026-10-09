"""Shared `metadata.json` checks for the look-and-feel and desktop-theme packages.

Both packages ship a `metadata.json` with the same shape, so the checks that do
not depend on the package kind — a plugin Version, a non-blank Description and
License, and a named Author — and the ones that differ only by constants — the
package structure, the plugin Id/Name and the Plasma API key/value — live here
once. Each suite subclasses `PackageMetadata` and sets the class attributes.
"""

import json


def load_metadata(path):
    """Read the JSON object at *path*, naming the file when it is not one.

    A ``metadata.json`` is a JSON object at the top level. A malformed file
    would otherwise surface as a bare ``json.JSONDecodeError`` and a
    well-formed file of another shape (an array, string, number or ``null``)
    as a bare ``AttributeError`` from the mixin's ``self.metadata.get(...)``;
    both name neither the file nor the type, so both are rejected here --
    with the path, and for the shape error the decoded type as well. A file
    that is not valid UTF-8 surfaces as a bare ``UnicodeDecodeError`` from
    the read, which names the byte but not the file, so that is rejected with
    the path too.
    """
    with open(path, encoding="utf-8") as handle:
        try:
            metadata = json.load(handle)
        except json.JSONDecodeError as exc:
            # Two packages ship a metadata.json, so the decoder's own message
            # (which names line and column but not the file) is ambiguous;
            # prepend the path and keep the original detail.
            raise ValueError(f"{path}: invalid JSON: {exc}") from exc
        except UnicodeDecodeError as exc:
            # The read decodes as UTF-8, so bytes in another encoding (or a
            # file corrupted mid-write) raise the decoder's own message,
            # which names the byte but neither of the two metadata.json
            # files; prepend the path and keep the byte detail.
            raise ValueError(f"{path}: not valid UTF-8 text: {exc}") from exc
    if not isinstance(metadata, dict):
        raise ValueError(
            f"{path} decoded to {type(metadata).__name__}, not a JSON object: "
            "a KDE metadata.json must be a JSON object"
        )
    return metadata


def kplugin(metadata, path):
    """Return *metadata*'s ``KPlugin`` object, naming *path* when it is not one.

    ``KPlugin`` holds the Id/Name/Version/Description/License fields, so every
    reader treats it as an object. A metadata.json missing it raises a bare
    ``KeyError`` from that read and one whose ``KPlugin`` is a string, list or
    number raises a bare ``TypeError``; neither names the file or the field, so
    both are rejected here with both. The mixin's ``_plugin`` and the
    desktop-theme wiring check share this guard.
    """
    plugin = metadata.get("KPlugin")
    if not isinstance(plugin, dict):
        raise ValueError(
            f"{path}: KPlugin must be a JSON object, not {type(plugin).__name__}"
        )
    return plugin


class PackageMetadata:
    """Mixin: assert the shape of a KDE package's `metadata.json`.

    Subclasses set `METADATA_PATH`, `PACKAGE_STRUCTURE`, `PACKAGE_ID`,
    `PLASMA_API_KEY` and `PLASMA_API_VERSION`. It is a plain mixin, not a
    `TestCase`, so importing it does not collect the unconfigured base.
    """

    METADATA_PATH = None
    PACKAGE_STRUCTURE = None
    PACKAGE_ID = None
    PLASMA_API_KEY = None
    PLASMA_API_VERSION = None

    def setUp(self):
        self.metadata = load_metadata(self.METADATA_PATH)

    def _plugin(self):
        """Return the metadata's `KPlugin` object, failing with the path.

        The Id/Name/Version/Description/License checks below read `KPlugin`,
        but a metadata.json missing it raises a bare ``KeyError`` and one
        whose ``KPlugin`` is not an object (a string, list or number) raises
        a bare ``TypeError`` from indexing it -- neither names the file or
        the field. Report the actual value instead.
        """
        try:
            return kplugin(self.metadata, self.METADATA_PATH)
        except ValueError as exc:
            self.fail(str(exc))

    def _plugin_field(self, key, expected=None):
        """Return `KPlugin`'s *key*, naming the file and field when it is absent.

        Id/Name/Version/Description/License are required `KPlugin` strings. A
        metadata.json that drops Id or Name raises a bare ``KeyError``, and one
        that drops Version/Description/License makes the caller's type check
        fail on ``None``; neither names the file or the field's parent. Name
        both here, with *expected* (when given) so a missing Id/Name also shows
        the value the package must carry.
        """
        plugin = self._plugin()
        if key not in plugin:
            suffix = "" if expected is None else f" (expected {expected!r})"
            self.fail(
                f"{self.METADATA_PATH}: KPlugin is missing {key!r}{suffix}"
            )
        return plugin[key]

    def _top_level_field(self, key, expected=None):
        """Return top-level *key*, naming the file and key when it is absent.

        `Keywords`, `KPackageStructure` and the Plasma API key are top-level
        strings. A metadata.json that drops one raises a bare ``KeyError``
        from indexing it or makes the caller's truthiness check fail on
        ``None``; neither names the file or the key. Name both here, with
        *expected* (when given) so a missing key also shows the value the
        package must carry.
        """
        if key not in self.metadata:
            suffix = "" if expected is None else f" (expected {expected!r})"
            self.fail(
                f"{self.METADATA_PATH}: missing top-level {key!r}{suffix}"
            )
        return self.metadata[key]

    def _top_level(self, key, expected):
        """Assert top-level *key* equals *expected*, naming the file and key.

        `KPackageStructure` and the Plasma API key are top-level strings. A
        metadata.json that drops one would fail the equality as ``None !=
        expected``, naming neither the file nor the missing key, so name both
        when the key is absent and label a mismatched value with the file too.
        """
        self.assertEqual(
            self._top_level_field(key, expected),
            expected,
            f"{self.METADATA_PATH}: top-level {key!r}",
        )

    def test_package_structure(self):
        self._top_level("KPackageStructure", self.PACKAGE_STRUCTURE)

    def test_plugin_id_and_name(self):
        # Indexing Id/Name directly would raise a bare KeyError naming only
        # the key, with neither the file nor the expected value; report both
        # so a metadata.json that drops a field is diagnosable.
        for key, expected in (("Id", self.PACKAGE_ID), ("Name", "Mac OS 8.6")):
            self.assertEqual(
                self._plugin_field(key, expected),
                expected,
                f"{self.METADATA_PATH}: KPlugin.{key}",
            )

    def test_plugin_version(self):
        version = self._plugin_field("Version")
        self.assertIsInstance(
            version, str, f"{self.METADATA_PATH}: KPlugin.Version"
        )
        self.assertTrue(
            version.strip(),
            f"{self.METADATA_PATH}: KPlugin.Version must not be blank",
        )

    def test_plasma_api_version(self):
        self._top_level(self.PLASMA_API_KEY, self.PLASMA_API_VERSION)

    def test_plugin_authors_are_named(self):
        # Both metadata.json files declare KPlugin.Authors as a non-empty list
        # of objects, and KDE's About dialog reads each entry's Name. Nothing
        # else pins that shape: a metadata.json that drops Authors, replaces
        # the list with a string, empties it, or blanks an entry's Name still
        # installs, so pin it here with the rest of the KPlugin contract.
        authors = self._plugin_field("Authors")
        self.assertIsInstance(
            authors, list, f"{self.METADATA_PATH}: KPlugin.Authors"
        )
        self.assertTrue(
            authors,
            f"{self.METADATA_PATH}: KPlugin.Authors must not be empty",
        )
        for index, author in enumerate(authors):
            where = f"{self.METADATA_PATH}: KPlugin.Authors[{index}]"
            self.assertIsInstance(author, dict, where)
            name = author.get("Name")
            self.assertIsInstance(name, str, f"{where}.Name")
            self.assertTrue(
                name.strip(), f"{where}.Name must not be blank"
            )

    def test_plugin_description_and_license_are_non_empty(self):
        # Description is shown in System Settings and License is the package's
        # legal metadata; a blank or non-string value installs cleanly but
        # misreports the package, so pin both here.
        for key in ("Description", "License"):
            value = self._plugin_field(key)
            self.assertIsInstance(
                value, str, f"{self.METADATA_PATH}: KPlugin.{key}"
            )
            self.assertTrue(
                value.strip(),
                f"{self.METADATA_PATH}: KPlugin.{key} must not be blank",
            )
