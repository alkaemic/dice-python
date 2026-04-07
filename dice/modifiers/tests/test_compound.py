import pytest

from dice.errors import DiceExecutionError
from dice.modifiers.base import ModifierSpec
from dice.modifiers.compound import COMPOUND_MODIFIERS, compound
from dice.rng import SeededRNG
from dice.terms.die_result import DieResult


def test_compound_no_match():
    """No die equals faces, so nothing compounds."""
    results = [DieResult(value=3), DieResult(value=4)]
    rng = SeededRNG(0)
    out = compound(results, ModifierSpec(key="!!"), rng, faces=6)
    assert len(out) == 2
    assert [r.value for r in out] == [3, 4]


def test_compound_single_explosion():
    """A die that matches faces should accumulate the reroll into the same result."""
    # Use d2 to make it likely the die compounds at least once.
    # Seed 0 on d2: first reroll should give us something.
    rng = SeededRNG(42)
    results = [DieResult(value=2)]
    out = compound(results, ModifierSpec(key="!!"), rng, faces=2)
    # The result list should still have 1 die (compound accumulates, not adds)
    assert len(out) == 1
    # The accumulated value should be > 2 (original 2 + at least one reroll)
    assert out[0].value > 2
    assert out[0].exploded is True


def test_compound_accumulates_all_rerolls():
    """Compound should keep adding to the same die until the roll doesn't match."""
    # d2 with value=2 will keep compounding. With a controlled seed,
    # we can verify accumulation.
    rng = SeededRNG(0)
    results = [DieResult(value=2)]
    out = compound(results, ModifierSpec(key="!!"), rng, faces=2)
    assert len(out) == 1
    # Value should be original 2 + all subsequent rolls
    assert out[0].value >= 3  # at least one reroll happened


def test_compound_does_not_affect_nonmatching():
    """Dice that don't match should remain unchanged."""
    results = [DieResult(value=3), DieResult(value=6)]
    rng = SeededRNG(42)
    out = compound(results, ModifierSpec(key="!!"), rng, faces=6)
    assert out[0].value == 3
    assert out[0].exploded is False


def test_compound_with_compare_point():
    """!! with compare point should compound on matching dice."""
    results = [DieResult(value=5), DieResult(value=2)]
    rng = SeededRNG(42)
    out = compound(
        results, ModifierSpec(key="!!", compare_point=">=5"), rng, faces=6
    )
    # The 5 should have compounded, the 2 should not
    assert out[0].value >= 5
    assert out[0].exploded is True
    assert out[1].value == 2
    assert out[1].exploded is False


def test_compound_max_explosions_exceeded():
    """Compound should respect max_explosions safety limit."""
    # d1 always matches, so it will compound forever
    rng = SeededRNG(0)
    results = [DieResult(value=1)]
    with pytest.raises(DiceExecutionError, match="MAX_EXPLOSIONS_EXCEEDED"):
        compound(results, ModifierSpec(key="!!"), rng, faces=1)


def test_compound_multiple_dice():
    """Each die that matches should compound independently."""
    rng = SeededRNG(42)
    results = [DieResult(value=6), DieResult(value=6)]
    out = compound(results, ModifierSpec(key="!!"), rng, faces=6)
    assert len(out) == 2
    # Both should have compounded
    assert all(r.exploded for r in out)
    assert all(r.value >= 6 for r in out)


def test_compound_preserves_kept_flag():
    """Compound should not change the kept status of dice."""
    results = [DieResult(value=6, kept=False)]
    rng = SeededRNG(42)
    out = compound(results, ModifierSpec(key="!!"), rng, faces=6)
    assert out[0].kept is False


def test_compound_empty_list():
    """Compound on empty list should not crash."""
    rng = SeededRNG(0)
    out = compound([], ModifierSpec(key="!!"), rng, faces=6)
    assert out == []


def test_compound_modifiers_registered():
    assert "!!" in COMPOUND_MODIFIERS
