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


@dataclass
class DiceContext:
    """Describes how to produce and interpret values for a specific die type.

    Passed to every modifier so that modifiers can create new dice and resolve
    defaults without knowing the specific die type (standard, fate, etc.).
    """

    max_value: int
    """Highest possible face value. Used as the default compare-point target
    (e.g. explode defaults to ``= max_value``) and as the default clamp ceiling."""

    min_value: int
    """Lowest possible face value. Used as the default clamp floor and
    the default critical-failure target."""

    roll_fn: Callable[[RNG], int]
    """Produce a single die value using the given RNG. Modifiers call this
    instead of ``roll_die`` directly so that non-standard face mappings
    (e.g. fate dice ``{-1, 0, 1}``) are honored automatically."""

    @classmethod
    def standard(cls, faces: int) -> DiceContext:
        """Create a context for standard dice with values in ``[1, faces]``."""
        from dice.rng import roll_die

        return cls(
            max_value=faces,
            min_value=1,
            roll_fn=lambda rng: roll_die(faces, rng),
        )


# Type alias for modifier functions.
# Takes: results list, modifier spec, rng, dice context, max explosions
# Returns: mutated results list
ModifierFn = Callable[
    [list[DieResult], ModifierSpec, RNG, DiceContext, int], list[DieResult]
]

_COMPARE_RE = re.compile(r"^(>=|<=|>|<|=)(-?\d+)$")


def matches_compare_point(
    value: int, compare_point: str | None, max_value: int
) -> bool:
    """Check whether a die value satisfies a compare point expression.

    If *compare_point* is ``None``, defaults to ``value == max_value``
    (used by explode).
    """
    if compare_point is None:
        return value == max_value
    m = _COMPARE_RE.match(compare_point)
    if m is None:
        raise ValueError(f"Invalid compare point: {compare_point!r}")
    op, threshold = m.group(1), int(m.group(2))
    if op == "=":
        return value == threshold
    if op == ">":
        return value > threshold
    if op == "<":
        return value < threshold
    if op == ">=":
        return value >= threshold
    if op == "<=":
        return value <= threshold
    return False  # pragma: no cover
