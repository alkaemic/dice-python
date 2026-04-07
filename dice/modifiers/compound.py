from __future__ import annotations

from dice.constants import MAX_EXPLOSIONS
from dice.errors import DiceExecutionError
from dice.modifiers.base import ModifierFn, ModifierSpec, matches_compare_point
from dice.rng import RNG, roll_die
from dice.terms.die_result import DieResult


def compound(
    results: list[DieResult],
    spec: ModifierSpec,
    rng: RNG,
    faces: int,
    max_explosions: int = MAX_EXPLOSIONS,
) -> list[DieResult]:
    """Compound exploding dice: reroll matching dice and accumulate into one value.

    Unlike regular explode which adds new dice, compound adds subsequent
    rolls to the original die's value. Used in Shadowrun, L5R, etc.

    Default compare point: ``= faces`` (i.e. max value).
    """
    explosions = 0
    for r in results:
        if not matches_compare_point(r.value, spec.compare_point, faces):
            continue
        r.exploded = True
        while True:
            explosions += 1
            if explosions > max_explosions:
                raise DiceExecutionError(
                    code="MAX_EXPLOSIONS_EXCEEDED",
                    message=f"Exceeded maximum explosion count ({max_explosions})",
                )
            roll = roll_die(faces, rng)
            r.value += roll
            if not matches_compare_point(roll, spec.compare_point, faces):
                break
    return results


COMPOUND_MODIFIERS: dict[str, ModifierFn] = {
    "!!": compound,
}
