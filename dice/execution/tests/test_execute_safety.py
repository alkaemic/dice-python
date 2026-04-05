import pytest

from dice.errors import DiceExecutionError
from dice.execution import ExecutionConfig, execute
from dice.grammar import parse
from dice.rng import SeededRNG


def test_max_dice_exceeded():
    config = ExecutionConfig(max_dice=3)
    parsed = parse("4d6")
    assert not parsed.errors
    with pytest.raises(DiceExecutionError, match="MAX_DICE_EXCEEDED"):
        execute(parsed.ast, rng=SeededRNG(42), config=config)


def test_max_dice_across_terms():
    config = ExecutionConfig(max_dice=5)
    parsed = parse("3d6+3d6")
    assert not parsed.errors
    with pytest.raises(DiceExecutionError, match="MAX_DICE_EXCEEDED"):
        execute(parsed.ast, rng=SeededRNG(42), config=config)


def test_max_depth_exceeded():
    config = ExecutionConfig(max_depth=1)
    parsed = parse("(1d6+3)*2")
    assert not parsed.errors
    with pytest.raises(DiceExecutionError, match="MAX_DEPTH_EXCEEDED"):
        execute(parsed.ast, rng=SeededRNG(42), config=config)


def test_max_explosions_exceeded():
    # d1 with explode: every roll is a 1 (max value), so it always explodes
    parsed = parse("1d1!")
    assert not parsed.errors
    with pytest.raises(DiceExecutionError, match="MAX_EXPLOSIONS_EXCEEDED"):
        execute(parsed.ast, rng=SeededRNG(42))


def test_division_by_zero_raises():
    parsed = parse("1d6/0")
    assert not parsed.errors
    with pytest.raises(DiceExecutionError, match="DIVISION_BY_ZERO"):
        execute(parsed.ast, rng=SeededRNG(42))


def test_zero_sided_die_raises():
    parsed = parse("d0")
    assert not parsed.errors
    with pytest.raises(Exception):
        execute(parsed.ast, rng=SeededRNG(42))


def test_within_limits_succeeds():
    config = ExecutionConfig(max_dice=10, max_depth=5)
    parsed = parse("2d6+3")
    assert not parsed.errors
    result = execute(parsed.ast, rng=SeededRNG(42), config=config)
    assert result.total is not None
