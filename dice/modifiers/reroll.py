from __future__ import annotations

from dice.constants import MAX_EXPLOSIONS
from dice.errors import DiceExecutionError
from dice.modifiers.base import (
    DiceContext,
    ModifierFn,
    ModifierSpec,
    matches_compare_point,
)
from dice.rng import RNG
from dice.terms.die_result import DieResult


def _reroll(
    results: list[DieResult],
    spec: ModifierSpec,
    rng: RNG,
    ctx: DiceContext,
    max_explosions: int,
    *,
    once: bool,
) -> list[DieResult]:
    """Shared implementation for reroll and reroll-once."""
    if spec.compare_point is None:
        raise DiceExecutionError(
            code="MISSING_COMPARE_POINT",
            message=(
                f"Reroll modifier '{spec.key}' requires a "
                f"compare point (e.g. '{spec.key}<2')"
            ),
        )
    iterations = 0
    to_check = [
        r
        for r in results
        if matches_compare_point(r.value, spec.compare_point, ctx.max_value)
    ]
    while to_check:
        next_round: list[DieResult] = []
        for die in to_check:
            iterations += 1
            if iterations > max_explosions:
                raise DiceExecutionError(
                    code="MAX_REROLLS_EXCEEDED",
                    message=f"Exceeded maximum reroll count ({max_explosions})",
                )
            die.rerolled = True
            die.kept = False
            replacement = DieResult(value=ctx.roll_fn(rng))
            results.append(replacement)
            if not once and matches_compare_point(
                replacement.value,
                spec.compare_point,
                ctx.max_value,
            ):
                next_round.append(replacement)
        to_check = next_round
    return results


def reroll(
    results: list[DieResult],
    spec: ModifierSpec,
    rng: RNG,
    ctx: DiceContext,
    max_explosions: int = MAX_EXPLOSIONS,
) -> list[DieResult]:
    """Reroll dice matching the compare point until none match."""
    return _reroll(results, spec, rng, ctx, max_explosions, once=False)


def reroll_once(
    results: list[DieResult],
    spec: ModifierSpec,
    rng: RNG,
    ctx: DiceContext,
    max_explosions: int = MAX_EXPLOSIONS,
) -> list[DieResult]:
    """Reroll dice matching the compare point at most once."""
    return _reroll(results, spec, rng, ctx, max_explosions, once=True)


REROLL_MODIFIERS: dict[str, ModifierFn] = {
    "r": reroll,
    "ro": reroll_once,
}
