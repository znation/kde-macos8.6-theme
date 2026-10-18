"""Shared, non-discovered support for the test suite.

Everything in this package is test-only infrastructure: fixtures that build the
inputs a test needs, harnesses that drive the project's commands, and assertion
helpers. None of it defines test cases, so ``unittest discover`` never runs it;
the test modules import what they need with ``from support.<module> import ...``.

The suite's test modules stay flat in ``tests/`` and match ``test*.py``;
``tests/test_suite_discovery.py`` guards that split. The SVG inspection helpers
keep their own package at ``tests/svg_assertions/`` because they form one
cohesive domain rather than loose cross-cutting helpers.
"""
