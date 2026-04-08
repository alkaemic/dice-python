from dice.modifiers.base import DiceContext, ModifierSpec
from dice.modifiers.critical import (
    CRITICAL_MODIFIERS,
    critical_failure,
    critical_success,
)
from dice.rng import SeededRNG
from dice.terms.die_result import DieResult

_ctx = DiceContext.standard

# --- critical success ---


def test_cs_default_marks_max_value():
    """cs without compare point marks dice equal to faces as critical success."""
    results = [DieResult(value=20), DieResult(value=15), DieResult(value=1)]
    rng = SeededRNG(0)
    out = critical_success(results, ModifierSpec(key="cs"), rng, ctx=_ctx(20))
    assert out[0].critical == "success"
    assert out[1].critical is None
    assert out[2].critical is None


def test_cs_with_compare_point():
    """cs>=18 marks dice >= 18 as critical success."""
    results = [DieResult(value=20), DieResult(value=18), DieResult(value=10)]
    rng = SeededRNG(0)
    out = critical_success(
        results, ModifierSpec(key="cs", compare_point=">=18"), rng, ctx=_ctx(20)
    )
    assert out[0].critical == "success"
    assert out[1].critical == "success"
    assert out[2].critical is None


def test_cs_no_matches():
    """cs should not mark anything when no dice match."""
    results = [DieResult(value=5), DieResult(value=10)]
    rng = SeededRNG(0)
    out = critical_success(results, ModifierSpec(key="cs"), rng, ctx=_ctx(20))
    assert all(r.critical is None for r in out)


# --- critical failure ---


def test_cf_default_marks_value_1():
    """cf without compare point marks dice equal to 1 as critical failure."""
    results = [DieResult(value=1), DieResult(value=10), DieResult(value=20)]
    rng = SeededRNG(0)
    out = critical_failure(results, ModifierSpec(key="cf"), rng, ctx=_ctx(20))
    assert out[0].critical == "failure"
    assert out[1].critical is None
    assert out[2].critical is None


def test_cf_with_compare_point():
    """cf<=3 marks dice <= 3 as critical failure."""
    results = [DieResult(value=1), DieResult(value=3), DieResult(value=4)]
    rng = SeededRNG(0)
    out = critical_failure(
        results, ModifierSpec(key="cf", compare_point="<=3"), rng, ctx=_ctx(20)
    )
    assert out[0].critical == "failure"
    assert out[1].critical == "failure"
    assert out[2].critical is None


def test_cf_no_matches():
    """cf should not mark anything when no dice match."""
    results = [DieResult(value=10), DieResult(value=15)]
    rng = SeededRNG(0)
    out = critical_failure(results, ModifierSpec(key="cf"), rng, ctx=_ctx(20))
    assert all(r.critical is None for r in out)


# --- edge cases ---


def test_cs_and_cf_together():
    """cs and cf can both apply to a single roll without conflict."""
    results = [DieResult(value=20), DieResult(value=1), DieResult(value=10)]
    rng = SeededRNG(0)
    out = critical_success(results, ModifierSpec(key="cs"), rng, ctx=_ctx(20))
    out = critical_failure(out, ModifierSpec(key="cf"), rng, ctx=_ctx(20))
    assert out[0].critical == "success"
    assert out[1].critical == "failure"
    assert out[2].critical is None


def test_cs_does_not_affect_total():
    """Critical marking should not change die values or kept status."""
    results = [DieResult(value=20), DieResult(value=5)]
    rng = SeededRNG(0)
    out = critical_success(results, ModifierSpec(key="cs"), rng, ctx=_ctx(20))
    assert out[0].value == 20
    assert out[0].kept is True
    assert out[1].value == 5
    assert out[1].kept is True


def test_critical_empty_list():
    """Critical on empty list should not crash."""
    rng = SeededRNG(0)
    out = critical_success([], ModifierSpec(key="cs"), rng, ctx=_ctx(20))
    assert out == []


def test_critical_modifiers_registered():
    assert "cs" in CRITICAL_MODIFIERS
    assert "cf" in CRITICAL_MODIFIERS
