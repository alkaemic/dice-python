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


def explode(
    results: list[DieResult],
    spec: ModifierSpec,
    rng: RNG,
    ctx: DiceContext,
    max_explosions: int = MAX_EXPLOSIONS,
) -> list[DieResult]:
    """Exploding dice: reroll any die meeting the compare point and add it.

    Repeats until no new die meets the condition or *max_explosions* is hit.
    Default compare point: ``= max_value`` (i.e. max face value).
    """
    explosions = 0
    new_dice = [
        r
        for r in results
        if matches_compare_point(r.value, spec.compare_point, ctx.max_value)
    ]
    while new_dice:
        next_round: list[DieResult] = []
        for _ in new_dice:
            explosions += 1
            if explosions > max_explosions:
                raise DiceExecutionError(
                    code="MAX_EXPLOSIONS_EXCEEDED",
                    message=f"Exceeded maximum explosion count ({max_explosions})",
                )
            value = ctx.roll_fn(rng)
            dr = DieResult(value=value, exploded=True)
            results.append(dr)
            if matches_compare_point(value, spec.compare_point, ctx.max_value):
                next_round.append(dr)
        new_dice = next_round
    return results


EXPLODE_MODIFIERS: dict[str, ModifierFn] = {
    "!": explode,
}
