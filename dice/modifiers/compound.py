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


def compound(
    results: list[DieResult],
    spec: ModifierSpec,
    rng: RNG,
    ctx: DiceContext,
    max_explosions: int = MAX_EXPLOSIONS,
) -> list[DieResult]:
    """Compound exploding dice: reroll matching dice and accumulate into one value.

    Unlike regular explode which adds new dice, compound adds subsequent
    rolls to the original die's value. Used in Shadowrun, L5R, etc.

    Default compare point: ``= max_value`` (i.e. max face value).
    """
    explosions = 0
    for r in results:
        if not matches_compare_point(r.value, spec.compare_point, ctx.max_value):
            continue
        r.exploded = True
        while True:
            explosions += 1
            if explosions > max_explosions:
                raise DiceExecutionError(
                    code="MAX_EXPLOSIONS_EXCEEDED",
                    message=f"Exceeded maximum explosion count ({max_explosions})",
                )
            roll = ctx.roll_fn(rng)
            r.value += roll
            if not matches_compare_point(roll, spec.compare_point, ctx.max_value):
                break
    return results


COMPOUND_MODIFIERS: dict[str, ModifierFn] = {
    "!!": compound,
}
