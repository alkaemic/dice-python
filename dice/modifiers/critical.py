from __future__ import annotations

from dice.modifiers.base import ModifierFn, ModifierSpec, matches_compare_point
from dice.rng import RNG
from dice.terms.die_result import DieResult


def critical_success(
    results: list[DieResult],
    spec: ModifierSpec,
    rng: RNG,
    faces: int,
    max_explosions: int = 0,
) -> list[DieResult]:
    """Mark dice matching the compare point as critical successes.

    Default compare point: ``= faces`` (i.e. max value, natural 20 on a d20).
    """
    for r in results:
        if matches_compare_point(r.value, spec.compare_point, faces):
            r.critical = "success"
    return results


def critical_failure(
    results: list[DieResult],
    spec: ModifierSpec,
    rng: RNG,
    faces: int,
    max_explosions: int = 0,
) -> list[DieResult]:
    """Mark dice matching the compare point as critical failures.

    Default compare point: ``= 1`` (natural 1).
    """
    cp = spec.compare_point if spec.compare_point is not None else "=1"
    for r in results:
        if matches_compare_point(r.value, cp, faces):
            r.critical = "failure"
    return results


CRITICAL_MODIFIERS: dict[str, ModifierFn] = {
    "cs": critical_success,
    "cf": critical_failure,
}
