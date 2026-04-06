from __future__ import annotations

from dice.errors import DiceExecutionError
from dice.modifiers.base import ModifierFn, ModifierSpec
from dice.rng import RNG
from dice.terms.die_result import DieResult


def _critical_stub(
    results: list[DieResult], spec: ModifierSpec, rng: RNG, faces: int, max_explosions: int = 0
) -> list[DieResult]:
    """Critical success/failure marking (Tier 2 — not yet implemented)."""
    raise DiceExecutionError(
        code="MODIFIER_NOT_IMPLEMENTED",
        message=f"Critical modifier ({spec.key}) is not yet implemented",
    )


CRITICAL_MODIFIERS: dict[str, ModifierFn] = {
    "cs": _critical_stub,
    "cf": _critical_stub,
}
