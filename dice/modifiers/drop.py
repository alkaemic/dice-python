from __future__ import annotations

from dice.modifiers.base import ModifierFn, ModifierSpec
from dice.rng import RNG
from dice.terms.die_result import DieResult


def drop_highest(
    results: list[DieResult], spec: ModifierSpec, rng: RNG, faces: int, max_explosions: int = 0
) -> list[DieResult]:
    """Drop the highest *n* dice (default 1)."""
    n = spec.argument if spec.argument is not None else 1
    active = [(i, r) for i, r in enumerate(results) if not r.rerolled]
    ranked = sorted(active, key=lambda pair: pair[1].value)
    drop_indices = {i for i, _ in ranked[-n:]} if n > 0 else set()
    for i, r in active:
        r.kept = i not in drop_indices
    return results


def drop_lowest(
    results: list[DieResult], spec: ModifierSpec, rng: RNG, faces: int, max_explosions: int = 0
) -> list[DieResult]:
    """Drop the lowest *n* dice (default 1)."""
    n = spec.argument if spec.argument is not None else 1
    active = [(i, r) for i, r in enumerate(results) if not r.rerolled]
    ranked = sorted(active, key=lambda pair: pair[1].value)
    drop_indices = {i for i, _ in ranked[:n]} if n > 0 else set()
    for i, r in active:
        r.kept = i not in drop_indices
    return results


DROP_MODIFIERS: dict[str, ModifierFn] = {
    "dh": drop_highest,
    "dl": drop_lowest,
}
