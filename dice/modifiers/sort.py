from __future__ import annotations

from dice.modifiers.base import ModifierFn, ModifierSpec
from dice.rng import RNG
from dice.terms.die_result import DieResult


def sort_ascending(
    results: list[DieResult],
    spec: ModifierSpec,
    rng: RNG,
    faces: int,
    max_explosions: int = 0,
) -> list[DieResult]:
    """Sort dice results by value in ascending order."""
    results.sort(key=lambda r: r.value)
    return results


def sort_descending(
    results: list[DieResult],
    spec: ModifierSpec,
    rng: RNG,
    faces: int,
    max_explosions: int = 0,
) -> list[DieResult]:
    """Sort dice results by value in descending order."""
    results.sort(key=lambda r: r.value, reverse=True)
    return results


SORT_MODIFIERS: dict[str, ModifierFn] = {
    "s": sort_ascending,
    "sa": sort_ascending,
    "sd": sort_descending,
}
