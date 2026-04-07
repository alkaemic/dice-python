from __future__ import annotations

from dice.modifiers.base import (
    DiceContext,
    ModifierFn,
    ModifierSpec,
    matches_compare_point,
)
from dice.rng import RNG
from dice.terms.die_result import DieResult


def critical_success(
    results: list[DieResult],
    spec: ModifierSpec,
    rng: RNG,
    ctx: DiceContext,
    max_explosions: int = 0,
) -> list[DieResult]:
    """Mark dice matching the compare point as critical successes.

    Default compare point: ``= max_value`` (i.e. max value, natural 20 on a d20).
    """
    for r in results:
        if matches_compare_point(r.value, spec.compare_point, ctx.max_value):
            r.critical = "success"
    return results


def critical_failure(
    results: list[DieResult],
    spec: ModifierSpec,
    rng: RNG,
    ctx: DiceContext,
    max_explosions: int = 0,
) -> list[DieResult]:
    """Mark dice matching the compare point as critical failures.

    Default compare point: ``= min_value`` (natural 1 on standard dice, -1 on fate).
    """
    cp = spec.compare_point if spec.compare_point is not None else f"={ctx.min_value}"
    for r in results:
        if matches_compare_point(r.value, cp, ctx.max_value):
            r.critical = "failure"
    return results


CRITICAL_MODIFIERS: dict[str, ModifierFn] = {
    "cs": critical_success,
    "cf": critical_failure,
}
