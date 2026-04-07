from dice.modifiers.base import ModifierSpec
from dice.modifiers.failure import FAILURE_MODIFIERS, failure
from dice.rng import SeededRNG
from dice.terms.die_result import DieResult


def test_failure_marks_matching_dice():
    """f<3 should mark dice with value < 3 as failures."""
    results = [
        DieResult(value=1), DieResult(value=5), DieResult(value=2),
    ]
    rng = SeededRNG(0)
    out = failure(results, ModifierSpec(key="f", compare_point="<3"), rng, faces=10)
    assert out[0].failure is True   # 1 < 3 => failure
    assert out[1].failure is False  # 5 not < 3
    assert out[2].failure is True   # 2 < 3 => failure


def test_failure_uses_failure_field():
    """Failure-marked dice should have failure=True on the DieResult."""
    results = [DieResult(value=1)]
    rng = SeededRNG(0)
    out = failure(results, ModifierSpec(key="f", compare_point="<3"), rng, faces=10)
    assert out[0].failure is True


def test_failure_no_matches():
    """If no dice match the failure condition, none should be marked."""
    results = [DieResult(value=8), DieResult(value=9)]
    rng = SeededRNG(0)
    out = failure(results, ModifierSpec(key="f", compare_point="<3"), rng, faces=10)
    assert all(not r.failure for r in out)


def test_failure_skips_unkept():
    """Unkept dice should not be marked as failures."""
    results = [DieResult(value=1, kept=False), DieResult(value=1, kept=True)]
    rng = SeededRNG(0)
    out = failure(results, ModifierSpec(key="f", compare_point="<3"), rng, faces=10)
    assert out[0].failure is False
    assert out[1].failure is True


def test_failure_preserves_existing_state():
    """Failure marking should not alter value, kept, or exploded flags."""
    results = [DieResult(value=1, exploded=True)]
    rng = SeededRNG(0)
    out = failure(results, ModifierSpec(key="f", compare_point="<3"), rng, faces=10)
    assert out[0].value == 1
    assert out[0].exploded is True
    assert out[0].kept is True
    assert out[0].failure is True


def test_failure_skips_already_matched_successes():
    """Dice already marked as matched (successes) should not be marked as failures."""
    results = [DieResult(value=1, matched=True)]
    rng = SeededRNG(0)
    out = failure(results, ModifierSpec(key="f", compare_point="<3"), rng, faces=10)
    assert out[0].failure is False
    assert out[0].matched is True


def test_failure_empty_list():
    """Failure on empty list should not crash."""
    rng = SeededRNG(0)
    out = failure([], ModifierSpec(key="f", compare_point="<3"), rng, faces=10)
    assert out == []


def test_failure_modifiers_registered():
    assert "f" in FAILURE_MODIFIERS
