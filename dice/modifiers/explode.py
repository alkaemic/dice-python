from __future__ import annotations

from dice.constants import MAX_EXPLOSIONS
from dice.errors import DiceExecutionError
from dice.modifiers.base import ModifierFn, ModifierSpec, matches_compare_point
from dice.rng import RNG, roll_die
from dice.terms.die_result import DieResult


def explode(
    results: list[DieResult],
    spec: ModifierSpec,
    rng: RNG,
    faces: int,
    max_explosions: int = MAX_EXPLOSIONS,
) -> list[DieResult]:
    """Exploding dice: reroll any die meeting the compare point and add it.

    Repeats until no new die meets the condition or *max_explosions* is hit.
    Default compare point: ``= faces`` (i.e. max value).
    """
    explosions = 0
    new_dice = [
        r for r in results
        if matches_compare_point(r.value, spec.compare_point, faces)
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
            value = roll_die(faces, rng)
            dr = DieResult(value=value, exploded=True)
            results.append(dr)
            if matches_compare_point(value, spec.compare_point, faces):
                next_round.append(dr)
        new_dice = next_round
    return results


EXPLODE_MODIFIERS: dict[str, ModifierFn] = {
    "!": explode,
}
