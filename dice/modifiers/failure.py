from __future__ import annotations

from dice.errors import DiceExecutionError
from dice.modifiers.base import ModifierFn, ModifierSpec
from dice.rng import RNG
from dice.terms.die_result import DieResult


def failure(
    results: list[DieResult], spec: ModifierSpec, rng: RNG, faces: int, max_explosions: int = 0
) -> list[DieResult]:
    """Failure counting (Tier 2 — not yet implemented)."""
    raise DiceExecutionError(
        code="MODIFIER_NOT_IMPLEMENTED",
        message="Failure modifier (f) is not yet implemented",
    )


FAILURE_MODIFIERS: dict[str, ModifierFn] = {
    "f": failure,
}
