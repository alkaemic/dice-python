from __future__ import annotations

from dice.errors import DiceExecutionError
from dice.modifiers.base import ModifierFn, ModifierSpec
from dice.rng import RNG
from dice.terms.die_result import DieResult


def _sort_stub(
    results: list[DieResult], spec: ModifierSpec, rng: RNG, faces: int, max_explosions: int = 0
) -> list[DieResult]:
    """Sort results (Tier 2 — not yet implemented)."""
    raise DiceExecutionError(
        code="MODIFIER_NOT_IMPLEMENTED",
        message=f"Sort modifier ({spec.key}) is not yet implemented",
    )


SORT_MODIFIERS: dict[str, ModifierFn] = {
    "s": _sort_stub,
    "sa": _sort_stub,
    "sd": _sort_stub,
}
