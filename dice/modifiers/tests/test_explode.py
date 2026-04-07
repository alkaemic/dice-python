import pytest

from dice.errors import DiceExecutionError
from dice.modifiers.base import DiceContext, ModifierSpec
from dice.modifiers.explode import explode
from dice.rng import SeededRNG
from dice.terms.die_result import DieResult

_ctx = DiceContext.standard


def test_explode_no_match():
    """No die equals faces, so nothing explodes."""
    results = [DieResult(value=3), DieResult(value=4)]
    rng = SeededRNG(0)
    explode(results, ModifierSpec(key="!"), rng, ctx=_ctx(6))
    assert len(results) == 2
    assert not any(r.exploded for r in results)


def test_explode_single():
    """One die matches, at least one explosion occurs."""
    rng = SeededRNG(42)
    results = [DieResult(value=6)]
    explode(results, ModifierSpec(key="!"), rng, ctx=_ctx(6))
    assert len(results) >= 2
    assert all(r.exploded for r in results[1:])
    assert all(1 <= r.value <= 6 for r in results[1:])


def test_explode_chain():
    """Set up a seed that causes chained explosions on a small die."""
    rng = SeededRNG(0)
    # d2: faces=2, start with a max roll
    results = [DieResult(value=2)]
    explode(results, ModifierSpec(key="!"), rng, ctx=_ctx(2))
    # At least one explosion happened
    assert len(results) >= 2
    assert results[1].exploded is True


def test_explode_custom_compare_point():
    """Explode on values >= 5 for a d6."""
    rng = SeededRNG(42)
    results = [DieResult(value=5), DieResult(value=3)]
    explode(results, ModifierSpec(key="!", compare_point=">=5"), rng, ctx=_ctx(6))
    # The 5 should have triggered an explosion, the 3 should not
    assert len(results) >= 3
    assert results[-1].exploded is True


def test_explode_max_explosions_exceeded():
    """Ensure MAX_EXPLOSIONS is enforced."""
    # Use a d1 so every roll matches
    rng = SeededRNG(0)
    results = [DieResult(value=1)]
    with pytest.raises(DiceExecutionError, match="MAX_EXPLOSIONS_EXCEEDED"):
        explode(results, ModifierSpec(key="!"), rng, ctx=_ctx(1))


def test_explode_marks_only_new_dice():
    """Original dice are not marked as exploded."""
    rng = SeededRNG(42)
    results = [DieResult(value=6), DieResult(value=2)]
    explode(results, ModifierSpec(key="!"), rng, ctx=_ctx(6))
    assert results[0].exploded is False
    assert results[1].exploded is False
