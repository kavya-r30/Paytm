"""Prefixed ULIDs: `bill_01JBQ…`. The prefix makes logs readable; the ULID sorts by creation time.

Ordering is millisecond-level: IDs created in different milliseconds sort chronologically,
but IDs created within the same millisecond have a random (unordered) suffix.
"""

from __future__ import annotations

import re

from ulid import ULID

_KIND_PATTERN = r"[a-z][a-z0-9]{1,9}"
# 26 Crockford base32 chars = 130 bits; a 128-bit ULID's first char is therefore 0-7.
_ULID_PATTERN = r"[0-7][0-9A-HJKMNP-TV-Z]{25}"
_KIND = re.compile(_KIND_PATTERN)
_ID = re.compile(rf"({_KIND_PATTERN})_({_ULID_PATTERN})")


class IdError(ValueError):
    """An ID or ID kind is malformed."""


def new_id(kind: str) -> str:
    """Return a fresh ID `<kind>_<ULID>`.

    `kind` must be 2-10 chars of lowercase letters/digits starting with a letter.
    Raises IdError otherwise (including trailing newlines). Sorting is ms-level monotonic.
    """
    if not _KIND.fullmatch(kind):
        raise IdError(f"bad id kind {kind!r}: use 2–10 lowercase letters/digits starting with a letter")
    return f"{kind}_{ULID()}"


def parse_id(value: str) -> tuple[str, str]:
    """Split an ID into `(kind, ulid)`. Raises IdError unless it is exactly `<kind>_<26-char ULID>`."""
    match = _ID.fullmatch(value)
    if not match:
        raise IdError(f"bad id {value!r}")
    return match.group(1), match.group(2)


def kind_of(value: str) -> str:
    """Return the kind prefix of a valid ID. Raises IdError if the ID is malformed."""
    return parse_id(value)[0]
