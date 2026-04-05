from dice.modifiers.base import ModifierSpec
from dice.modifiers.keep import keep_highest, keep_lowest
from dice.rng import SeededRNG
from dice.terms.die_result import DieResult


def _results(*values: int) -> list[DieResult]:
    return [DieResult(value=v) for v in values]


def _rng() -> SeededRNG:
    return SeededRNG(0)


def test_keep_highest_basic():
    results = _results(3, 5, 1, 6)
    keep_highest(results, ModifierSpec(key="kh", argument=2), _rng(), 6)
    kept = [r for r in results if r.kept]
    assert len(kept) == 2
    assert {r.value for r in kept} == {5, 6}


def test_keep_highest_default_1():
    results = _results(3, 5, 1, 6)
    keep_highest(results, ModifierSpec(key="kh"), _rng(), 6)
    kept = [r for r in results if r.kept]
    assert len(kept) == 1
    assert kept[0].value == 6


def test_keep_highest_all():
    results = _results(3, 5, 1)
    keep_highest(results, ModifierSpec(key="kh", argument=10), _rng(), 6)
    assert all(r.kept for r in results)


def test_keep_highest_ties():
    results = _results(5, 5, 5, 1)
    keep_highest(results, ModifierSpec(key="kh", argument=2), _rng(), 6)
    kept = [r for r in results if r.kept]
    assert len(kept) == 2
    assert all(r.value == 5 for r in kept)


def test_keep_lowest_basic():
    results = _results(3, 5, 1, 6)
    keep_lowest(results, ModifierSpec(key="kl", argument=2), _rng(), 6)
    kept = [r for r in results if r.kept]
    assert len(kept) == 2
    assert {r.value for r in kept} == {1, 3}


def test_keep_lowest_default_1():
    results = _results(3, 5, 1, 6)
    keep_lowest(results, ModifierSpec(key="kl"), _rng(), 6)
    kept = [r for r in results if r.kept]
    assert len(kept) == 1
    assert kept[0].value == 1


def test_keep_highest_zero_keeps_nothing():
    results = _results(3, 5, 1, 6)
    keep_highest(results, ModifierSpec(key="kh", argument=0), _rng(), 6)
    assert all(not r.kept for r in results)


def test_keep_lowest_zero_keeps_nothing():
    results = _results(3, 5, 1, 6)
    keep_lowest(results, ModifierSpec(key="kl", argument=0), _rng(), 6)
    assert all(not r.kept for r in results)


def test_keep_highest_more_than_available():
    results = _results(3, 5)
    keep_highest(results, ModifierSpec(key="kh", argument=10), _rng(), 6)
    assert all(r.kept for r in results)


def test_keep_skips_rerolled_dice():
    results = _results(3, 5, 1, 6)
    results[1].rerolled = True
    results[1].kept = False
    keep_highest(results, ModifierSpec(key="kh", argument=2), _rng(), 6)
    # The rerolled die (5) should remain rerolled/not kept
    assert results[1].kept is False
    assert results[1].rerolled is True
    # Among active dice [3, 1, 6], keep highest 2 → 3 and 6
    active_kept = [r for r in results if r.kept]
    assert len(active_kept) == 2
