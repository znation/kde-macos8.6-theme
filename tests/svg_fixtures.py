"""Shared SVG tree fixtures for the svg-assertion test modules.

``test_svg_assertions_parsing`` and ``test_svg_assertions_checks`` both build
namespaced ``<svg>`` documents to exercise ``tests/svg_assertions.py``; the
wrapper that declares the SVG namespace lives here once instead of in each
module.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET


def _svg_tree(body, **attributes):
    """Return an ElementTree for a namespaced SVG root wrapping *body*.

    The fixtures that build an SVG document root share this wrapper: a
    ``<svg xmlns=...>`` element around a body string. *attributes* are the
    extra root attributes the canvas builders need (``width``, ``height``,
    ``viewBox``). Declaring the SVG namespace is what makes ElementTree
    report each tag as ``{http://www.w3.org/2000/svg}rect``, the form
    `local_name` strips back to ``rect``.
    """
    attrs = "".join(
        f' {name}="{value}"' for name, value in attributes.items()
    )
    return ET.ElementTree(
        ET.fromstring(
            f'<svg xmlns="http://www.w3.org/2000/svg"{attrs}>{body}</svg>'
        )
    )
