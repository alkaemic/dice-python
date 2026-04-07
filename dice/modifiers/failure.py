from __future__ import annotations

from dice.modifiers.base import (
    DiceContext,
    ModifierFn,
    ModifierSpec,
    matches_compare_point,
)
from dice.rng import RNG
from dice.terms.die_result import DieResult


def failure(
    results: list[DieResult],
    spec: ModifierSpec,
    rng: RNG,
    ctx: DiceContext,
    max_explosions: int = 0,
) -> list[DieResult]:
    """Mark dice matching the compare point as failures.

    Failures subtract from the success count in target pools.
    Used in World of Darkness: ``6d10>7f<3`` — successes > 7, failures < 3.
    Only kept, non-matched dice are eligible for failure marking.
    """
    for r in results:
        if not r.kept or r.matched:
            continue
        if matches_compare_point(r.value, spec.compare_point, ctx.max_value):
            r.failure = True
    return results


FAILURE_MODIFIERS: dict[str, ModifierFn] = {
    "f": failure,
}
