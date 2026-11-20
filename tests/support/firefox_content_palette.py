"""Palette declaration assertions shared by Firefox preferences suites."""

from support.gtk_css import HEX


def assert_palette_declarations(case, selectors, allowed, important=None):
    """Pin every declaration of each selector in ``selectors``.

    Each declaration's hex tokens must come from ``allowed``. The properties in
    ``important`` must carry ``!important``; ``None`` means every property must.
    """
    for selector in selectors:
        declarations = case.rules[selector]
        with case.subTest(selector=selector):
            case.assertTrue(declarations)
        for name, value in declarations.items():
            with case.subTest(property=name):
                must_be_important = important is None or name in important
                assert_pinned_value(case, value, allowed, must_be_important)


def assert_pinned_value(case, value, allowed, must_be_important):
    """Assert *value* carries ``!important`` when required and only *allowed* hex colors."""
    if must_be_important:
        case.assertIn("!important", value)
    for token in HEX.findall(value):
        case.assertIn(token, allowed)
