from dice.modifiers.base import DiceContext, ModifierSpec
from dice.modifiers.target import TARGET_MODIFIERS, target
from dice.rng import SeededRNG
from dice.terms.die_result import DieResult

_ctx = DiceContext.standard

# --- basic target matching ---


def test_target_greater_than():
    """>7 should mark dice with value > 7 as matched."""
    results = [DieResult(value=8), DieResult(value=7), DieResult(value=10)]
    rng = SeededRNG(0)
    out = target(results, ModifierSpec(key=">", compare_point=">7"), rng, ctx=_ctx(10))
    assert out[0].matched is True  # 8 > 7
    assert out[1].matched is False  # 7 is not > 7
    assert out[2].matched is True  # 10 > 7


def test_target_less_than():
    """<3 should mark dice with value < 3 as matched."""
    results = [DieResult(value=1), DieResult(value=3), DieResult(value=2)]
    rng = SeededRNG(0)
    out = target(results, ModifierSpec(key="<", compare_point="<3"), rng, ctx=_ctx(6))
    assert out[0].matched is True  # 1 < 3
    assert out[1].matched is False  # 3 is not < 3
    assert out[2].matched is True  # 2 < 3


def test_target_equal():
    """=5 should mark dice with value == 5 as matched."""
    results = [DieResult(value=5), DieResult(value=4), DieResult(value=5)]
    rng = SeededRNG(0)
    out = target(results, ModifierSpec(key="=", compare_point="=5"), rng, ctx=_ctx(6))
    assert out[0].matched is True
    assert out[1].matched is False
    assert out[2].matched is True


def test_target_no_matches():
    """When no dice match, none should be marked."""
    results = [DieResult(value=3), DieResult(value=4)]
    rng = SeededRNG(0)
    out = target(results, ModifierSpec(key=">", compare_point=">10"), rng, ctx=_ctx(10))
    assert all(not r.matched for r in out)


def test_target_all_match():
    """When all dice match, all should be marked."""
    results = [DieResult(value=8), DieResult(value=9), DieResult(value=10)]
    rng = SeededRNG(0)
    out = target(results, ModifierSpec(key=">", compare_point=">7"), rng, ctx=_ctx(10))
    assert all(r.matched for r in out)


# --- edge cases ---


def test_target_skips_unkept_dice():
    """Unkept dice (e.g., dropped) should not be marked as matched."""
    results = [DieResult(value=10, kept=False), DieResult(value=10, kept=True)]
    rng = SeededRNG(0)
    out = target(results, ModifierSpec(key=">", compare_point=">7"), rng, ctx=_ctx(10))
    assert out[0].matched is False  # unkept
    assert out[1].matched is True  # kept


def test_target_preserves_other_flags():
    """Target should not alter value, kept, exploded, or rerolled flags."""
    results = [DieResult(value=8, exploded=True)]
    rng = SeededRNG(0)
    out = target(results, ModifierSpec(key=">", compare_point=">7"), rng, ctx=_ctx(10))
    assert out[0].value == 8
    assert out[0].exploded is True
    assert out[0].kept is True
    assert out[0].matched is True


def test_target_empty_list():
    """Target on empty list should not crash."""
    rng = SeededRNG(0)
    out = target([], ModifierSpec(key=">", compare_point=">7"), rng, ctx=_ctx(10))
    assert out == []


def test_target_modifiers_registered():
    assert ">" in TARGET_MODIFIERS
    assert "<" in TARGET_MODIFIERS
    assert "=" in TARGET_MODIFIERS


def test_target_greater_equal_via_compare_point():
    """>=7 should mark dice with value >= 7."""
    results = [DieResult(value=7), DieResult(value=6), DieResult(value=10)]
    rng = SeededRNG(0)
    out = target(results, ModifierSpec(key=">", compare_point=">=7"), rng, ctx=_ctx(10))
    assert out[0].matched is True
    assert out[1].matched is False
    assert out[2].matched is True
