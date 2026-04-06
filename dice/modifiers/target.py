from __future__ import annotations

from dice.errors import DiceExecutionError
from dice.modifiers.base import ModifierFn, ModifierSpec
from dice.rng import RNG
from dice.terms.die_result import DieResult


def _target_stub(
    results: list[DieResult], spec: ModifierSpec, rng: RNG, faces: int, max_explosions: int = 0
) -> list[DieResult]:
    """Success counting / target (Tier 2 — not yet implemented)."""
    raise DiceExecutionError(
        code="MODIFIER_NOT_IMPLEMENTED",
        message=f"Target modifier ({spec.key}) is not yet implemented",
    )


TARGET_MODIFIERS: dict[str, ModifierFn] = {
    ">": _target_stub,
    "<": _target_stub,
    "=": _target_stub,
}
