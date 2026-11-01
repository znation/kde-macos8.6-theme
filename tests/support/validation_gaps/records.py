"""The shared record types of the validation-gap ledgers.

The reader builds :class:`Gap` records from the archived bug files; the
per-tag ledger modules build :class:`Reproduction` entries for them. Both live
here so the reader, the ledgers and the five tag modules share one definition
instead of re-declaring the fields.
"""

from __future__ import annotations

from collections import namedtuple

# One parsed validation-gap record. ``subject`` is the bug's heading for the
# prose form and the bullet's own text for the older one-line form.
Gap = namedtuple("Gap", "tag source line subject")

# One mechanism's offline reproduction: the record markers that identify it
# and the test reference that confirms the failure without a real run.
Reproduction = namedtuple("Reproduction", "name markers reference")
