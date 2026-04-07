from __future__ import annotations

from dice.modifiers.base import ModifierFn, ModifierSpec
from dice.rng import RNG
from dice.terms.die_result import DieResult


def clamp_min(
    results: list[DieResult],
    spec: ModifierSpec,
    rng: RNG,
    faces: int,
    max_explosions: int = 0,
) -> list[DieResult]:
    """Clamp each die's value to a minimum floor.

    Usage: ``2d6min2`` — any die below 2 is raised to 2.
    """
    floor = spec.argument if spec.argument is not None else 1
    for r in results:
        if r.value < floor:
            r.value = floor
    return results


def clamp_max(
    results: list[DieResult],
    spec: ModifierSpec,
    rng: RNG,
    faces: int,
    max_explosions: int = 0,
) -> list[DieResult]:
    """Clamp each die's value to a maximum ceiling.

    Usage: ``2d6max4`` — any die above 4 is lowered to 4.
    """
    ceiling = spec.argument if spec.argument is not None else faces
    for r in results:
        if r.value > ceiling:
            r.value = ceiling
    return results


CLAMP_MODIFIERS: dict[str, ModifierFn] = {
    "min": clamp_min,
    "max": clamp_max,
}
