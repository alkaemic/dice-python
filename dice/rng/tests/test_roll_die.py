import pytest

from dice.errors import DiceValidationError
from dice.rng import SeededRNG, roll_die


def test_roll_die_within_bounds():
    rng = SeededRNG(42)
    for _ in range(100):
        result = roll_die(6, rng=rng)
        assert 1 <= result <= 6


def test_roll_die_deterministic_with_seeded_rng():
    rng1 = SeededRNG(99)
    rng2 = SeededRNG(99)
    results1 = [roll_die(20, rng=rng1) for _ in range(10)]
    results2 = [roll_die(20, rng=rng2) for _ in range(10)]
    assert results1 == results2


def test_roll_die_without_rng_returns_valid_result():
    result = roll_die(6)
    assert 1 <= result <= 6


def test_roll_die_single_sided():
    rng = SeededRNG(0)
    result = roll_die(1, rng=rng)
    assert result == 1


def test_roll_die_zero_sides_raises():
    with pytest.raises(DiceValidationError, match="INVALID_DIE_SIDES"):
        roll_die(0, rng=SeededRNG(0))


def test_roll_die_negative_sides_raises():
    with pytest.raises(DiceValidationError, match="INVALID_DIE_SIDES"):
        roll_die(-1, rng=SeededRNG(0))
