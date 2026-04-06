from __future__ import annotations

from dice.errors import DiceExecutionError
from dice.modifiers.base import ModifierFn, ModifierSpec
from dice.rng import RNG
from dice.terms.die_result import DieResult


def _clamp_stub(
    results: list[DieResult], spec: ModifierSpec, rng: RNG, faces: int, max_explosions: int = 0
) -> list[DieResult]:
    """Min/max clamping (Tier 3 — not yet implemented)."""
    raise DiceExecutionError(
        code="MODIFIER_NOT_IMPLEMENTED",
        message=f"Clamp modifier ({spec.key}) is not yet implemented",
    )


CLAMP_MODIFIERS: dict[str, ModifierFn] = {
    "min": _clamp_stub,
    "max": _clamp_stub,
}
