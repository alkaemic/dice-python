from __future__ import annotations

from dice.modifiers.base import (
    DiceContext,
    ModifierFn,
    ModifierSpec,
    matches_compare_point,
)
from dice.rng import RNG
from dice.terms.die_result import DieResult


def _resolve_compare_point(spec: ModifierSpec) -> str:
    """Build a compare point string from the spec.

    The modifier parser yields ``key='>', argument=7, compare_point=None``
    for ``>7``.  We reconstruct ``'>7'`` so ``matches_compare_point`` works.
    """
    if spec.compare_point is not None:
        return spec.compare_point
    if spec.argument is not None:
        return f"{spec.key}{spec.argument}"
    return f"{spec.key}0"


def target(
    results: list[DieResult],
    spec: ModifierSpec,
    rng: RNG,
    ctx: DiceContext,
    max_explosions: int = 0,
) -> list[DieResult]:
    """Mark dice that meet the target as successes (matched=True).

    Used in World of Darkness, Shadowrun, Burning Wheel, etc.
    Only kept dice are eligible for matching.
    """
    cp = _resolve_compare_point(spec)
    for r in results:
        if r.kept and matches_compare_point(r.value, cp, ctx.max_value):
            r.matched = True
    return results


TARGET_MODIFIERS: dict[str, ModifierFn] = {
    ">": target,
    "<": target,
    "=": target,
}
