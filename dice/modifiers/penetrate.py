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


def penetrate(
    results: list[DieResult],
    spec: ModifierSpec,
    rng: RNG,
    ctx: DiceContext,
    max_explosions: int = MAX_EXPLOSIONS,
) -> list[DieResult]:
    """Penetrating explode: like explode but each new die subtracts 1.

    Used in Hackmaster. Each penetrating die has 1 subtracted from its
    rolled value. The subtracted value is still checked against the
    compare point (using the raw roll) to determine if penetration continues.

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
            raw_roll = ctx.roll_fn(rng)
            dr = DieResult(value=raw_roll - 1, exploded=True)
            results.append(dr)
            if matches_compare_point(raw_roll, spec.compare_point, ctx.max_value):
                next_round.append(dr)
        new_dice = next_round
    return results


PENETRATE_MODIFIERS: dict[str, ModifierFn] = {
    "!p": penetrate,
}
