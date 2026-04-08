from dice.modifiers.base import DiceContext, ModifierSpec
from dice.modifiers.clamp import CLAMP_MODIFIERS, clamp_max, clamp_min
from dice.rng import SeededRNG
from dice.terms.die_result import DieResult

_ctx = DiceContext.standard

# --- min ---


def test_clamp_min_raises_low_values():
    """min2 should raise any value below 2 up to 2."""
    results = [DieResult(value=1), DieResult(value=3), DieResult(value=2)]
    rng = SeededRNG(0)
    out = clamp_min(results, ModifierSpec(key="min", argument=2), rng, ctx=_ctx(6))
    assert [r.value for r in out] == [2, 3, 2]


def test_clamp_min_no_effect_when_all_above():
    """min2 should not change dice that are already >= 2."""
    results = [DieResult(value=4), DieResult(value=5)]
    rng = SeededRNG(0)
    out = clamp_min(results, ModifierSpec(key="min", argument=2), rng, ctx=_ctx(6))
    assert [r.value for r in out] == [4, 5]


def test_clamp_min_equal_to_threshold():
    """A value exactly at the min should not change."""
    results = [DieResult(value=3)]
    rng = SeededRNG(0)
    out = clamp_min(results, ModifierSpec(key="min", argument=3), rng, ctx=_ctx(6))
    assert out[0].value == 3


def test_clamp_min_all_ones():
    """All 1s with min2 should all become 2."""
    results = [DieResult(value=1), DieResult(value=1), DieResult(value=1)]
    rng = SeededRNG(0)
    out = clamp_min(results, ModifierSpec(key="min", argument=2), rng, ctx=_ctx(6))
    assert all(r.value == 2 for r in out)


# --- max ---


def test_clamp_max_lowers_high_values():
    """max4 should lower any value above 4 down to 4."""
    results = [DieResult(value=6), DieResult(value=3), DieResult(value=5)]
    rng = SeededRNG(0)
    out = clamp_max(results, ModifierSpec(key="max", argument=4), rng, ctx=_ctx(6))
    assert [r.value for r in out] == [4, 3, 4]


def test_clamp_max_no_effect_when_all_below():
    """max5 should not change dice that are already <= 5."""
    results = [DieResult(value=2), DieResult(value=4)]
    rng = SeededRNG(0)
    out = clamp_max(results, ModifierSpec(key="max", argument=5), rng, ctx=_ctx(6))
    assert [r.value for r in out] == [2, 4]


def test_clamp_max_equal_to_threshold():
    """A value exactly at the max should not change."""
    results = [DieResult(value=4)]
    rng = SeededRNG(0)
    out = clamp_max(results, ModifierSpec(key="max", argument=4), rng, ctx=_ctx(6))
    assert out[0].value == 4


# --- edge cases ---


def test_clamp_preserves_die_flags():
    """Clamping should not alter kept/exploded/rerolled flags."""
    results = [DieResult(value=1, exploded=True, kept=False)]
    rng = SeededRNG(0)
    out = clamp_min(results, ModifierSpec(key="min", argument=3), rng, ctx=_ctx(6))
    assert out[0].value == 3
    assert out[0].exploded is True
    assert out[0].kept is False


def test_clamp_skips_unkept_dice():
    """Clamping should still apply to unkept dice (value changes regardless)."""
    results = [DieResult(value=1, kept=False)]
    rng = SeededRNG(0)
    out = clamp_min(results, ModifierSpec(key="min", argument=2), rng, ctx=_ctx(6))
    assert out[0].value == 2


def test_clamp_empty_list():
    """Clamping an empty list should not crash."""
    rng = SeededRNG(0)
    out = clamp_min([], ModifierSpec(key="min", argument=2), rng, ctx=_ctx(6))
    assert out == []


def test_clamp_modifiers_registered():
    """Both min and max should be in CLAMP_MODIFIERS."""
    assert "min" in CLAMP_MODIFIERS
    assert "max" in CLAMP_MODIFIERS
