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

    def _plugin(self):
        """Return the metadata's `KPlugin` object, failing with the path.

        The Id/Name/Version/Description/License checks below read `KPlugin`,
        but a metadata.json missing it raises a bare ``KeyError`` and one
        whose ``KPlugin`` is not an object (a string, list or number) raises
        a bare ``TypeError`` from indexing it -- neither names the file or
        the field. Report the actual value instead.
        """
        plugin = self.metadata.get("KPlugin")
        if not isinstance(plugin, dict):
            self.fail(
                f"{self.METADATA_PATH}: KPlugin must be a JSON object, not "
                f"{type(plugin).__name__}"
            )
        return plugin

    def test_package_structure(self):
        self.assertEqual(
            self.metadata.get("KPackageStructure"), self.PACKAGE_STRUCTURE
        )

    def test_plugin_id_and_name(self):
        plugin = self._plugin()
        self.assertEqual(plugin["Id"], self.PACKAGE_ID)
        self.assertEqual(plugin["Name"], "Mac OS 8.6")

    def test_plugin_version(self):
        version = self._plugin().get("Version")
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
        plugin = self._plugin()
        for key in ("Description", "License"):
            value = plugin.get(key)
            self.assertIsInstance(value, str, key)
            self.assertTrue(value.strip(), f"KPlugin.{key} must not be blank")
