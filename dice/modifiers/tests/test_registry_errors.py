"""Tests for error handling in the modifier registry."""

import pytest

from dice.errors import DiceError, DiceExecutionError
from dice.modifiers.base import DiceContext, ModifierSpec
from dice.modifiers.registry import apply_modifiers
from dice.rng import SeededRNG
from dice.terms.die_result import DieResult


def test_unregistered_modifier_raises_dice_execution_error():
    """apply_modifiers should raise DiceExecutionError for unknown keys."""
    results = [DieResult(value=4)]
    specs = [ModifierSpec(key="zzz")]
    ctx = DiceContext.standard(6)

    with pytest.raises(DiceExecutionError, match="zzz"):
        apply_modifiers(results, specs, SeededRNG(0), ctx)


def test_unregistered_modifier_error_code():
    """The error should use the UNKNOWN_MODIFIER code."""
    results = [DieResult(value=4)]
    specs = [ModifierSpec(key="zzz")]
    ctx = DiceContext.standard(6)

    with pytest.raises(DiceExecutionError) as exc_info:
        apply_modifiers(results, specs, SeededRNG(0), ctx)
    assert exc_info.value.code == "UNKNOWN_MODIFIER"


def test_unregistered_modifier_is_catchable_as_dice_error():
    """Consumers catching DiceError should catch unregistered modifiers."""
    results = [DieResult(value=4)]
    specs = [ModifierSpec(key="zzz")]
    ctx = DiceContext.standard(6)

    with pytest.raises(DiceError):
        apply_modifiers(results, specs, SeededRNG(0), ctx)
