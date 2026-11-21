"""Shared assertion helpers for GTK 3 OSD selector inventories."""


class OsdSelectorAssertions:
    def assert_osd_selector_count(self, expected, count):
        """Check the flattened selector inventory for an OSD rule family."""
        enumerated = {
            selector for _, selectors in expected for selector in selectors
        }
        self.assertEqual(len(enumerated), count, enumerated)
        return enumerated
