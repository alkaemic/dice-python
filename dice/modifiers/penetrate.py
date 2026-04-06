from __future__ import annotations

from dice.errors import DiceExecutionError
from dice.modifiers.base import ModifierFn, ModifierSpec
from dice.rng import RNG
from dice.terms.die_result import DieResult


def penetrate(
    results: list[DieResult], spec: ModifierSpec, rng: RNG, faces: int, max_explosions: int = 0
) -> list[DieResult]:
    """Penetrating explode (Tier 2 — not yet implemented)."""
    raise DiceExecutionError(
        code="MODIFIER_NOT_IMPLEMENTED",
        message="Penetrating explode (!p) is not yet implemented",
    )


PENETRATE_MODIFIERS: dict[str, ModifierFn] = {
    "!p": penetrate,
}
