from __future__ import annotations

import re

from dice.modifiers.base import ModifierSpec

# Ordered longest-first so greedy matching works correctly.
# Keys that are prefixes of longer keys must come after them.
_MODIFIER_KEYS = [
    "min",
    "max",
    "!!",
    "!p",
    "!",
    "ro",
    "r",
    "kh",
    "kl",
    "k",
    "dh",
    "dl",
    ">=",
    "<=",
    ">",
    "<",
    "=",
    "cs",
    "cf",
    "sa",
    "sd",
    "s",
    "f",
]

# Build a single regex: (key)(compare_point_or_number)?
# compare_point: (>=|<=|>|<|=)\d+
# number: \d+
_KEY_PATTERN = "|".join(re.escape(k) for k in _MODIFIER_KEYS)
_TOKEN_RE = re.compile(
    rf"({_KEY_PATTERN})"  # group 1: modifier key
    rf"((?:>=|<=|>|<|=)\d+)?"  # group 2: optional compare point
    rf"(\d+)?"  # group 3: optional bare number argument
)


def parse_modifier_string(text: str) -> list[ModifierSpec]:
    """Parse a modifier suffix string into a list of ModifierSpec objects.

    Examples::

        >>> parse_modifier_string("kh3")
        [ModifierSpec(key='kh', argument=3)]
        >>> parse_modifier_string("r<2!")
        [ModifierSpec(key='r', compare_point='<2'), ModifierSpec(key='!')]
        >>> parse_modifier_string("kh3r=1!")  # doctest: +SKIP
        [ModifierSpec(key='kh', argument=3), ...]
    """
    specs: list[ModifierSpec] = []
    pos = 0
    while pos < len(text):
        m = _TOKEN_RE.match(text, pos)
        if m is None:
            raise ValueError(
                f"Unrecognized modifier notation at position {pos}: {text[pos:]!r}"
            )
        key = m.group(1)
        compare_point = m.group(2)  # e.g. "<2", ">=5"
        bare_number = m.group(3)  # e.g. "3"

        argument: int | None = None
        cp: str | None = compare_point

        if bare_number is not None and compare_point is None:
            argument = int(bare_number)

        specs.append(ModifierSpec(key=key, argument=argument, compare_point=cp))
        pos = m.end()
    return specs
