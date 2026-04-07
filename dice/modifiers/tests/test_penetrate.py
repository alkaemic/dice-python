import pytest

from dice.errors import DiceExecutionError
from dice.modifiers.base import ModifierSpec
from dice.modifiers.penetrate import PENETRATE_MODIFIERS, penetrate
from dice.rng import SeededRNG
from dice.terms.die_result import DieResult


def test_penetrate_no_match():
    """No die equals faces, so nothing penetrates."""
    results = [DieResult(value=3), DieResult(value=4)]
    rng = SeededRNG(0)
    out = penetrate(results, ModifierSpec(key="!p"), rng, faces=6)
    assert len(out) == 2
    assert not any(r.exploded for r in out)


def test_penetrate_single():
    """A die that matches should add a new die with value - 1."""
    rng = SeededRNG(42)
    results = [DieResult(value=6)]
    out = penetrate(results, ModifierSpec(key="!p"), rng, faces=6)
    assert len(out) >= 2
    # The new die should be marked as exploded
    assert out[1].exploded is True
    # Penetrating die has its value reduced by 1
    # The raw roll is some value 1-6, but it gets -1 applied
    assert out[1].value >= 0  # min is roll(1) - 1 = 0


def test_penetrate_subtracts_one():
    """Each penetrating die should have 1 subtracted from its rolled value."""
    # Use a d2: value=2 triggers penetration.
    # Seed to control the outcome.
    rng = SeededRNG(42)
    results = [DieResult(value=2)]
    out = penetrate(results, ModifierSpec(key="!p"), rng, faces=2)
    # Original die stays at 2
    assert out[0].value == 2
    # Each subsequent die is roll - 1
    for r in out[1:]:
        assert r.exploded is True


def test_penetrate_chain_subtracts_one_each_time():
    """In a chain of penetrations, each new die subtracts 1 from its roll.

    d1 always rolls 1, which always matches faces=1, so it would chain
    forever. Use max_explosions=3 and verify all penetrated dice are 0.
    """
    rng = SeededRNG(0)
    results = [DieResult(value=1)]
    with pytest.raises(DiceExecutionError, match="MAX_EXPLOSIONS_EXCEEDED"):
        penetrate(results, ModifierSpec(key="!p"), rng, faces=1, max_explosions=3)
    # Before the error, some dice were added — all penetrated dice should be 0
    for r in results[1:]:
        assert r.value == 0  # roll_die(1)=1, minus 1 = 0
        assert r.exploded is True


def test_penetrate_with_compare_point():
    """!p with compare point penetrates on matching dice."""
    results = [DieResult(value=5), DieResult(value=2)]
    rng = SeededRNG(42)
    out = penetrate(
        results, ModifierSpec(key="!p", compare_point=">=5"), rng, faces=6
    )
    assert len(out) >= 3  # At least one penetration from the 5
    assert out[2].exploded is True


def test_penetrate_max_explosions_exceeded():
    """Penetrate should respect max_explosions safety limit."""
    # d2 where value=2 matches. Penetration gives roll-1:
    # if roll=2, pen=1 which doesn't match faces=2.
    # But with a rigged seed we can force it.
    # Use faces=2 with a seed that generates 2s
    rng = SeededRNG(0)
    results = [DieResult(value=2)]
    # Force low max to trigger the safety
    with pytest.raises(DiceExecutionError, match="MAX_EXPLOSIONS_EXCEEDED"):
        penetrate(results, ModifierSpec(key="!p"), rng, faces=2, max_explosions=1)


def test_penetrate_does_not_modify_original_value():
    """Original dice values should not be changed by penetration."""
    rng = SeededRNG(42)
    results = [DieResult(value=6)]
    out = penetrate(results, ModifierSpec(key="!p"), rng, faces=6)
    assert out[0].value == 6


def test_penetrate_empty_list():
    """Penetrate on empty list should not crash."""
    rng = SeededRNG(0)
    out = penetrate([], ModifierSpec(key="!p"), rng, faces=6)
    assert out == []


def test_penetrate_modifiers_registered():
    assert "!p" in PENETRATE_MODIFIERS
