"""Shared `metadata.json` checks for the look-and-feel and desktop-theme packages.

Both packages ship a `metadata.json` with the same shape, so the checks that do
not depend on the package kind — a plugin Version, a non-blank Description and
License — and the ones that differ only by constants — the package structure,
the plugin Id/Name and the Plasma API key/value — live here once. Each suite
subclasses `PackageMetadata` and sets the class attributes.
"""

import json


def load_metadata(path):
    """Read the JSON object at *path*, naming the file when it is not one.

    A ``metadata.json`` is a JSON object at the top level. A malformed file
    would otherwise surface as a bare ``json.JSONDecodeError`` and a
    well-formed file of another shape (an array, string, number or ``null``)
    as a bare ``AttributeError`` from the mixin's ``self.metadata.get(...)``;
    both name neither the file nor the type, so both are rejected here --
    with the path, and for the shape error the decoded type as well.
    """
    with open(path, encoding="utf-8") as handle:
        try:
            metadata = json.load(handle)
        except json.JSONDecodeError as exc:
            # Two packages ship a metadata.json, so the decoder's own message
            # (which names line and column but not the file) is ambiguous;
            # prepend the path and keep the original detail.
            raise ValueError(f"{path}: invalid JSON: {exc}") from exc
    if not isinstance(metadata, dict):
        raise ValueError(
            f"{path} decoded to {type(metadata).__name__}, not a JSON object: "
            "a KDE metadata.json must be a JSON object"
        )
    return metadata


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

    def test_package_structure(self):
        self.assertEqual(
            self.metadata.get("KPackageStructure"), self.PACKAGE_STRUCTURE
        )

    def test_plugin_id_and_name(self):
        plugin = self.metadata["KPlugin"]
        self.assertEqual(plugin["Id"], self.PACKAGE_ID)
        self.assertEqual(plugin["Name"], "Mac OS 8.6")

    def test_plugin_version(self):
        version = self.metadata["KPlugin"].get("Version")
        self.assertIsInstance(version, str, "KPlugin.Version")
        self.assertTrue(version.strip(), "KPlugin.Version must not be blank")

    def test_plasma_api_version(self):
        self.assertEqual(
            self.metadata.get(self.PLASMA_API_KEY), self.PLASMA_API_VERSION
        )

    def test_plugin_description_and_license_are_non_empty(self):
        # Description is shown in System Settings and License is the package's
        # legal metadata; a blank or non-string value installs cleanly but
        # misreports the package, so pin both here.
        plugin = self.metadata["KPlugin"]
        for key in ("Description", "License"):
            value = plugin.get(key)
            self.assertIsInstance(value, str, key)
            self.assertTrue(value.strip(), f"KPlugin.{key} must not be blank")
