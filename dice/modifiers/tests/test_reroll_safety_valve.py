"""Tests verifying that all modifier safety valves raise DiceExecutionError
when their iteration budget is exhausted.

Explode, compound, penetrate, and reroll all raise consistently so that
consumers always get an explicit error rather than a silently truncated
result.

See CODE_REVIEW_3.md issue #3.
"""

import pytest

from dice import roll
from dice.errors import DiceExecutionError
from dice.execution import ExecutionConfig
from dice.modifiers.base import DiceContext, ModifierSpec
from dice.modifiers.compound import compound
from dice.modifiers.explode import explode
from dice.modifiers.penetrate import penetrate
from dice.modifiers.reroll import reroll
from dice.rng import SeededRNG
from dice.terms.die_result import DieResult


_ctx = DiceContext.standard(6)


# ---- All four modifiers raise on budget exhaustion ----


def test_explode_raises_on_max_explosions():
    """explode raises DiceExecutionError when the budget is exhausted."""
    results = [DieResult(value=6)]
    spec = ModifierSpec(key="!", compare_point=">=1")
    with pytest.raises(DiceExecutionError, match="MAX_EXPLOSIONS_EXCEEDED"):
        explode(results, spec, SeededRNG(42), _ctx, max_explosions=3)


def test_compound_raises_on_max_explosions():
    """compound raises DiceExecutionError when the budget is exhausted."""
    results = [DieResult(value=6)]
    spec = ModifierSpec(key="!!", compare_point=">=1")
    with pytest.raises(DiceExecutionError, match="MAX_EXPLOSIONS_EXCEEDED"):
        compound(results, spec, SeededRNG(42), _ctx, max_explosions=3)


def test_penetrate_raises_on_max_explosions():
    """penetrate raises DiceExecutionError when the budget is exhausted."""
    results = [DieResult(value=6)]
    spec = ModifierSpec(key="!p", compare_point=">=1")
    with pytest.raises(DiceExecutionError, match="MAX_EXPLOSIONS_EXCEEDED"):
        penetrate(results, spec, SeededRNG(42), _ctx, max_explosions=3)


def test_reroll_raises_on_max_rerolls():
    """reroll raises DiceExecutionError when the budget is exhausted."""
    results = [DieResult(value=3)]
    spec = ModifierSpec(key="r", compare_point="<7")
    with pytest.raises(DiceExecutionError, match="MAX_REROLLS_EXCEEDED"):
        reroll(results, spec, SeededRNG(42), _ctx, max_explosions=3)


def test_reroll_error_code():
    """reroll uses a distinct MAX_REROLLS_EXCEEDED error code."""
    results = [DieResult(value=3)]
    spec = ModifierSpec(key="r", compare_point="<7")
    with pytest.raises(DiceExecutionError) as exc_info:
        reroll(results, spec, SeededRNG(42), _ctx, max_explosions=3)
    assert exc_info.value.code == "MAX_REROLLS_EXCEEDED"


# ---- End-to-end: both raise through roll() ----


def test_roll_explode_raises_via_api():
    """roll() surfaces DiceExecutionError for runaway explosions."""
    config = ExecutionConfig(max_explosions=5)
    with pytest.raises(DiceExecutionError):
        roll("1d6!>=1", rng=SeededRNG(42), config=config)


def test_roll_reroll_raises_via_api():
    """roll() surfaces DiceExecutionError for runaway rerolls."""
    config = ExecutionConfig(max_explosions=5)
    with pytest.raises(DiceExecutionError):
        roll("1d6r<7", rng=SeededRNG(42), config=config)


# ---- Reroll within budget still works normally ----


def test_reroll_within_budget_works_normally():
    """When the condition resolves within the budget, reroll works correctly."""
    results = [DieResult(value=1)]
    spec = ModifierSpec(key="r", compare_point="=1")
    out = reroll(results, spec, SeededRNG(42), _ctx, max_explosions=100)

    kept = [r for r in out if r.kept]
    assert len(kept) == 1
    assert kept[0].value != 1
