from __future__ import annotations

from dice.modifiers.base import ModifierFn, ModifierSpec
from dice.rng import RNG
from dice.terms.die_result import DieResult


def keep_highest(
    results: list[DieResult], spec: ModifierSpec, rng: RNG, faces: int
) -> list[DieResult]:
    """Keep the highest *n* dice (default 1)."""
    n = spec.argument if spec.argument is not None else 1
    active = [(i, r) for i, r in enumerate(results) if not r.rerolled]
    ranked = sorted(active, key=lambda pair: pair[1].value)
    keep_indices = {i for i, _ in ranked[-n:]} if n > 0 else set()
    for i, r in active:
        r.kept = i in keep_indices
    return results


def keep_lowest(
    results: list[DieResult], spec: ModifierSpec, rng: RNG, faces: int
) -> list[DieResult]:
    """Keep the lowest *n* dice (default 1)."""
    n = spec.argument if spec.argument is not None else 1
    active = [(i, r) for i, r in enumerate(results) if not r.rerolled]
    ranked = sorted(active, key=lambda pair: pair[1].value)
    keep_indices = {i for i, _ in ranked[:n]} if n > 0 else set()
    for i, r in active:
        r.kept = i in keep_indices
    return results


KEEP_MODIFIERS: dict[str, ModifierFn] = {
    "kh": keep_highest,
    "kl": keep_lowest,
}
