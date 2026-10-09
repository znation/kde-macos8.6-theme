"""Document-safety guards for the SVG test helpers.

The package's guards that read the parsed tree and reject artwork a pixel test
cannot see: an executable ``<script>``, a ``<style>`` element that moves colours
out of presentation attributes, an external file or ``data:`` reference, and a
duplicate id.
"""

from __future__ import annotations

import re

from .tree import local_name

def assert_no_script_elements(case, tree):
    """Assert *tree* holds no ``<script>`` element.

    KSvg executes a script element rather than drawing it, so a pixel check
    would not notice one; only this structural assertion catches it. *case* is
    the calling ``unittest.TestCase``; its assertion names the element.
    """
    for element in tree.iter():
        tag = local_name(element)
        case.assertFalse(tag.endswith("script"), tag)

def _local_attribute_name(name):
    """Return an attribute *name* without its `{namespace}` prefix.

    An SVG that declares the xlink namespace makes ElementTree report
    ``xlink:href`` as ``{http://www.w3.org/1999/xlink}href``; one that leaves
    it undeclared reports the bare ``xlink:href``. Both name the same
    reference, so strip any namespace before matching.
    """
    return name.rsplit("}", 1)[-1]

def assert_no_style_elements(case, tree):
    """Assert *tree* holds no ``<style>`` element.

    The widget tests read an element's colours from its presentation
    ``fill``/``stroke`` attributes (``attribute_values``), and the slice
    renderer composites only the rects and groups it models. A ``<style>``
    element moves the artwork's colours into CSS selectors neither the pixel
    tests nor the palette checks can see, so a widget whose rendered colour
    changed could still pass. Keep the colours on the elements; *case* is the
    calling ``unittest.TestCase`` and its assertion names the element.
    """
    for element in tree.iter():
        tag = local_name(element)
        case.assertNotEqual(tag, "style", f"<{tag}> element")

# CSS/SVG ``url(...)`` target: unquoted, single-quoted or double-quoted,
# padded with whitespace. SVG uses the form in presentation attributes such as
# ``fill``, ``filter``, ``clip-path`` and ``mask``, and in an inline ``style``.
_URL_REFERENCE = re.compile(
    r"""url\(\s*(?:'([^']*)'|"([^"]*)"|([^)]*?))\s*\)""",
    re.IGNORECASE,
)

def _url_targets(value):
    """Yield the target of every ``url(...)`` reference in an attribute value.

    The target may be unquoted or wrapped in single or double quotes and
    padded with whitespace; it is returned without that quoting or padding so
    the caller can tell an in-file ``#id`` from a file or ``data:`` reference.
    """
    for match in _URL_REFERENCE.finditer(value):
        target = next(group for group in match.groups() if group is not None)
        yield target.strip()

def assert_no_external_references(case, tree):
    """Assert every reference in *tree* is a same-document ``#id``.

    The package is installed by copying its directory, so an ``<image>``, an
    ``href``/``xlink:href``, or a ``url(...)`` in a presentation attribute or
    inline ``style`` that names a file (or a ``data:`` URI) points at
    something the installed theme does not ship, so the reference cannot
    resolve. The pixel tests composite only rects and groups, so they cannot
    notice one; *case* is the calling ``unittest.TestCase`` and its assertion
    names the element and value instead. A bare ``#id`` fragment is allowed.
    """
    for element in tree.iter():
        tag = local_name(element)
        case.assertNotEqual(
            tag, "image", f"<{tag}> references an external file"
        )
        for name, value in element.attrib.items():
            if _local_attribute_name(name) == "href" and not value.startswith(
                "#"
            ):
                case.fail(
                    f"<{tag}> reference {value!r} is not an in-file #id"
                )
            for target in _url_targets(value):
                if not target.startswith("#"):
                    case.fail(
                        f"<{tag}> {name} reference {target!r} is not an "
                        f"in-file #id"
                    )

def assert_unique_ids(case, tree):
    """Assert every ``id`` in *tree* is unique.

    `elements_by_id` and `rect_geometry` key their maps by id, so a duplicate
    silently keeps only the later element and a test that reads by id sees the
    wrong one; `attribute_values` reads ids as a set, which cannot see a
    duplicate either. KSvg resolves an id to a single element, so a duplicate
    is an artwork defect regardless. *case* is the calling
    ``unittest.TestCase``; its assertion names each repeated id.
    """
    seen = set()
    duplicates = set()
    for element in tree.iter():
        element_id = element.get("id")
        if element_id is None:
            continue
        if element_id in seen:
            duplicates.add(element_id)
        else:
            seen.add(element_id)
    case.assertEqual(sorted(duplicates), [], "duplicate ids")
