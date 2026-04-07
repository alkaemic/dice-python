from dice.modifiers.base import DiceContext, ModifierSpec
from dice.modifiers.reroll import reroll, reroll_once
from dice.rng import SeededRNG
from dice.terms.die_result import DieResult

_ctx = DiceContext.standard


def test_reroll_basic():
    """Reroll dice matching =1, replacement should not be 1 (with this seed)."""
    rng = SeededRNG(42)
    results = [DieResult(value=1), DieResult(value=5)]
    reroll(results, ModifierSpec(key="r", compare_point="=1"), rng, ctx=_ctx(6))
    # Original die is marked rerolled and not kept
    assert results[0].rerolled is True
    assert results[0].kept is False
    # Replacement was appended
    assert len(results) >= 3
    # The non-matching die is untouched
    assert results[1].rerolled is False
    assert results[1].kept is True


def test_reroll_no_match():
    """If nothing matches, results are unchanged."""
    rng = SeededRNG(0)
    results = [DieResult(value=3), DieResult(value=5)]
    reroll(results, ModifierSpec(key="r", compare_point="=1"), rng, ctx=_ctx(6))
    assert len(results) == 2
    assert not any(r.rerolled for r in results)


def test_reroll_once_stops_after_one():
    """ro rerolls at most once even if replacement matches."""
    rng = SeededRNG(0)
    # d2 with compare_point =1: high chance replacement also matches
    results = [DieResult(value=1)]
    reroll_once(results, ModifierSpec(key="ro", compare_point="=1"), rng, ctx=_ctx(2))
    # Original is rerolled
    assert results[0].rerolled is True
    # Exactly one replacement was added (even if it also equals 1)
    replacements = [r for r in results if not r.rerolled]
    assert len(replacements) == 1


def test_reroll_compare_point_less_than():
    """Reroll dice with value < 3."""
    rng = SeededRNG(42)
    results = [DieResult(value=2), DieResult(value=4)]
    reroll(results, ModifierSpec(key="r", compare_point="<3"), rng, ctx=_ctx(6))
    assert results[0].rerolled is True
    assert results[1].rerolled is False


def test_reroll_plus_keep_interaction():
    """Reroll + keep: rerolled dice should be excluded from keep selection."""
    from dice.modifiers.keep import keep_highest

    rng = SeededRNG(42)
    results = [DieResult(value=1), DieResult(value=5), DieResult(value=3)]
    reroll(results, ModifierSpec(key="r", compare_point="=1"), rng, ctx=_ctx(6))
    keep_highest(results, ModifierSpec(key="kh", argument=2), rng, ctx=_ctx(6))
    # Rerolled die stays not kept
    assert results[0].kept is False
    assert results[0].rerolled is True
    # Among active dice, only 2 are kept
    active_kept = [r for r in results if r.kept]
    assert len(active_kept) == 2
