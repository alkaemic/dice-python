from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass

from dice.rng import RNG
from dice.terms.die_result import DieResult


@dataclass
class ModifierSpec:
    """A parsed modifier with its key and arguments."""

    key: str  # e.g. "kh", "dl", "!", "r"
    argument: int | None = None  # e.g. 3 in "kh3"
    compare_point: str | None = None  # e.g. "<2" in "r<2"


# Type alias for modifier functions.
# Takes: results list, modifier spec, rng, faces count, max explosions
# Returns: mutated results list
ModifierFn = Callable[[list[DieResult], ModifierSpec, RNG, int, int], list[DieResult]]

_COMPARE_RE = re.compile(r"^(>=|<=|>|<|=)(\d+)$")


def matches_compare_point(
    value: int, compare_point: str | None, faces: int
) -> bool:
    """Check whether a die value satisfies a compare point expression.

    If *compare_point* is ``None``, defaults to ``value == faces``
    (used by explode).
    """
    if compare_point is None:
        return value == faces
    m = _COMPARE_RE.match(compare_point)
    if m is None:
        raise ValueError(f"Invalid compare point: {compare_point!r}")
    op, threshold_str = m.group(1), int(m.group(2))
    if op == "=":
        return value == threshold_str
    if op == ">":
        return value > threshold_str
    if op == "<":
        return value < threshold_str
    if op == ">=":
        return value >= threshold_str
    if op == "<=":
        return value <= threshold_str
    return False  # pragma: no cover
