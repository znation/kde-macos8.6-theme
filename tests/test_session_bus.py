"""Direct tests for tools/session_bus.py.

The `apply_theme` suite exercises the defaulted address
through its command stubs; these pin the helper's own contract directly.
For an absolute `XDG_RUNTIME_DIR` whose `bus` socket does not exist,
the environment must be returned unchanged instead of pointing
a session tool at a socket that is not there.
"""

from __future__ import annotations

import os
import unittest

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support import tmp_dir
from tools import session_bus


class TestSessionEnv(unittest.TestCase):
    def setUp(self):
        self.directory = tmp_dir.make_tmp_dir(self)

    def test_an_existing_address_is_returned_unchanged(self):
        self.assertEqual(
            {"XDG_RUNTIME_DIR": str(self.directory),
             "DBUS_SESSION_BUS_ADDRESS": "unix:path=/existing"},
            session_bus.session_env(
                {"XDG_RUNTIME_DIR": str(self.directory),
                 "DBUS_SESSION_BUS_ADDRESS": "unix:path=/existing"}
            ),
        )

    def test_an_absolute_runtime_dir_with_a_bus_socket_names_it(self):
        (self.directory / "bus").write_text("", encoding="utf-8")
        self.assertEqual(
            {"XDG_RUNTIME_DIR": str(self.directory),
             "DBUS_SESSION_BUS_ADDRESS": f"unix:path={self.directory}/bus"},
            session_bus.session_env({"XDG_RUNTIME_DIR": str(self.directory)}),
        )

    def test_an_empty_address_is_defaulted_like_an_unset_one(self):
        # The docstring says an empty address names no bus, so a bus socket
        # under the runtime directory must still be named.
        (self.directory / "bus").write_text("", encoding="utf-8")
        self.assertEqual(
            {"XDG_RUNTIME_DIR": str(self.directory),
             "DBUS_SESSION_BUS_ADDRESS": f"unix:path={self.directory}/bus"},
            session_bus.session_env(
                {"XDG_RUNTIME_DIR": str(self.directory),
                 "DBUS_SESSION_BUS_ADDRESS": ""}
            ),
        )

    def test_an_empty_address_without_a_bus_socket_stays_empty(self):
        # With no socket to name, the environment is returned unchanged, so
        # the empty value is not replaced by a path that does not exist.
        self.assertEqual(
            {"XDG_RUNTIME_DIR": str(self.directory),
             "DBUS_SESSION_BUS_ADDRESS": ""},
            session_bus.session_env(
                {"XDG_RUNTIME_DIR": str(self.directory),
                 "DBUS_SESSION_BUS_ADDRESS": ""}
            ),
        )

    def test_a_runtime_dir_with_address_syntax_characters_is_percent_encoded(self):
        # The D-Bus address grammar uses %, ;, , and = as its own syntax, so
        # a runtime directory carrying one of them would otherwise truncate
        # the composed path or split it into a second address; each becomes
        # its uppercase percent escape. A literal %2C lookalike in the name
        # becomes %252C, so no parser decodes it back to the comma it mimics.
        odd = self.directory / "a,b=c;d%2Ce"
        odd.mkdir()
        (odd / "bus").write_text("", encoding="utf-8")
        self.assertEqual(
            {"XDG_RUNTIME_DIR": str(odd),
             "DBUS_SESSION_BUS_ADDRESS":
                 f"unix:path={self.directory}/a%2Cb%3Dc%3Bd%252Ce/bus"},
            session_bus.session_env({"XDG_RUNTIME_DIR": str(odd)}),
        )

    def test_an_existing_address_is_left_untouched_even_with_syntax_characters(self):
        # The caller composed its own address, so it is passed through as it
        # stands: only the value this helper synthesizes gets encoded.
        self.assertEqual(
            {"XDG_RUNTIME_DIR": str(self.directory),
             "DBUS_SESSION_BUS_ADDRESS": "unix:path=/a,b=c"},
            session_bus.session_env(
                {"XDG_RUNTIME_DIR": str(self.directory),
                 "DBUS_SESSION_BUS_ADDRESS": "unix:path=/a,b=c"}
            ),
        )

    def test_an_absolute_runtime_dir_without_a_bus_socket_is_left_unchanged(self):
        # The runtime directory names a session only when its bus socket is
        # present; defaulting to a socket that is not there would send the
        # session tools at a path the bus never listens on.
        self.assertEqual(
            {"XDG_RUNTIME_DIR": str(self.directory)},
            session_bus.session_env({"XDG_RUNTIME_DIR": str(self.directory)}),
        )

    def test_a_relative_runtime_dir_is_left_unchanged(self):
        # A relative runtime dir cannot name the session's socket, so no
        # address is defaulted even when a sibling 'bus' path would resolve.
        (self.directory / "bus").write_text("", encoding="utf-8")
        runtime = os.path.relpath(self.directory)
        self.assertEqual(
            {"XDG_RUNTIME_DIR": runtime},
            session_bus.session_env({"XDG_RUNTIME_DIR": runtime}),
        )

    def test_an_empty_runtime_dir_is_left_unchanged(self):
        # An empty XDG_RUNTIME_DIR is not an absolute directory, so it cannot
        # name a bus socket; the address stays unset rather than becoming a
        # path relative to the current directory.
        self.assertEqual(
            {"XDG_RUNTIME_DIR": ""},
            session_bus.session_env({"XDG_RUNTIME_DIR": ""}),
        )

    def test_an_absent_runtime_dir_is_left_unchanged(self):
        # Neither variable may be carried, so the lookup must treat the
        # absent XDG_RUNTIME_DIR as "no runtime directory", not as a KeyError.
        self.assertEqual({}, session_bus.session_env({}))


if __name__ == "__main__":
    unittest.main()
