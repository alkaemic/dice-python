from __future__ import annotations

import threading

from dice.constants import MAX_EXPLOSIONS
from dice.modifiers.base import ModifierFn, ModifierSpec
from dice.rng import RNG
from dice.terms.die_result import DieResult

# Fixed execution order — modifiers are applied in this order regardless
# of the order they appear in the notation.
MODIFIER_ORDER: list[str] = [
    "min", "max",           # 1-2: clamp
    "!", "!!", "!p",        # 3: explode/compound/penetrate
    "r", "ro",              # 4: reroll
    "k", "kh", "kl",        # 5: keep
    "dh", "dl",             # 6: drop
    ">", "<", "=",          # 7: target/success
    "f",                    # 8: failure
    "cs", "cf",             # 9: critical marking
    "s", "sa", "sd",        # 10: sort
]

_MODIFIER_REGISTRY: dict[str, ModifierFn] = {}
_MODIFIER_LOCK = threading.Lock()


def register_modifier(key: str, fn: ModifierFn) -> None:
    """Register a modifier function for a given key."""
    with _MODIFIER_LOCK:
        _MODIFIER_REGISTRY[key] = fn


def get_modifier(key: str) -> ModifierFn | None:
    """Look up a registered modifier by key."""
    with _MODIFIER_LOCK:
        return _MODIFIER_REGISTRY.get(key)


def _order_key(spec: ModifierSpec) -> int:
    """Return the execution-order index for a modifier spec."""
    try:
        return MODIFIER_ORDER.index(spec.key)
    except ValueError:
        # Unknown modifiers run last
        return len(MODIFIER_ORDER)


def apply_modifiers(
    results: list[DieResult],
    modifier_specs: list[ModifierSpec],
    rng: RNG,
    faces: int,
    max_explosions: int = MAX_EXPLOSIONS,
) -> list[DieResult]:
    """Apply modifiers in the fixed execution order.

    The *modifier_specs* are sorted by ``MODIFIER_ORDER`` position before
    execution, so ``4d6r1kh3`` and ``4d6kh3r1`` produce identical results.
    """
    sorted_specs = sorted(modifier_specs, key=_order_key)
    with _MODIFIER_LOCK:
        fns = {spec.key: _MODIFIER_REGISTRY.get(spec.key) for spec in sorted_specs}
    for spec in sorted_specs:
        fn = fns[spec.key]
        if fn is None:
            raise ValueError(f"No modifier registered for key: {spec.key!r}")
        results = fn(results, spec, rng, faces, max_explosions)
    return results


def _register_all_builtins() -> None:
    """Register all built-in modifier functions."""
    from dice.modifiers.clamp import CLAMP_MODIFIERS
    from dice.modifiers.compound import COMPOUND_MODIFIERS
    from dice.modifiers.critical import CRITICAL_MODIFIERS
    from dice.modifiers.drop import DROP_MODIFIERS
    from dice.modifiers.explode import EXPLODE_MODIFIERS
    from dice.modifiers.failure import FAILURE_MODIFIERS
    from dice.modifiers.keep import KEEP_MODIFIERS
    from dice.modifiers.penetrate import PENETRATE_MODIFIERS
    from dice.modifiers.reroll import REROLL_MODIFIERS
    from dice.modifiers.sort import SORT_MODIFIERS
    from dice.modifiers.target import TARGET_MODIFIERS

    for group in (
        CLAMP_MODIFIERS,
        COMPOUND_MODIFIERS,
        CRITICAL_MODIFIERS,
        DROP_MODIFIERS,
        EXPLODE_MODIFIERS,
        FAILURE_MODIFIERS,
        KEEP_MODIFIERS,
        PENETRATE_MODIFIERS,
        REROLL_MODIFIERS,
        SORT_MODIFIERS,
        TARGET_MODIFIERS,
    ):
        for key, fn in group.items():
            register_modifier(key, fn)


_register_all_builtins()
