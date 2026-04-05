from dice.modifiers.base import ModifierSpec
from dice.modifiers.drop import drop_highest, drop_lowest
from dice.rng import SeededRNG
from dice.terms.die_result import DieResult


def _results(*values: int) -> list[DieResult]:
    return [DieResult(value=v) for v in values]


def _rng() -> SeededRNG:
    return SeededRNG(0)


def test_drop_highest_basic():
    results = _results(3, 5, 1, 6)
    drop_highest(results, ModifierSpec(key="dh", argument=1), _rng(), 6)
    kept = [r for r in results if r.kept]
    assert len(kept) == 3
    assert all(r.value != 6 for r in kept)


def test_drop_highest_default_1():
    results = _results(3, 5, 1, 6)
    drop_highest(results, ModifierSpec(key="dh"), _rng(), 6)
    kept = [r for r in results if r.kept]
    assert len(kept) == 3


def test_drop_lowest_basic():
    results = _results(3, 5, 1, 6)
    drop_lowest(results, ModifierSpec(key="dl", argument=1), _rng(), 6)
    kept = [r for r in results if r.kept]
    assert len(kept) == 3
    assert all(r.value != 1 for r in kept)


def test_drop_lowest_default_1():
    results = _results(3, 5, 1, 6)
    drop_lowest(results, ModifierSpec(key="dl"), _rng(), 6)
    kept = [r for r in results if r.kept]
    assert len(kept) == 3


def test_drop_lowest_multiple():
    results = _results(3, 5, 1, 6, 2)
    drop_lowest(results, ModifierSpec(key="dl", argument=2), _rng(), 6)
    kept = [r for r in results if r.kept]
    assert len(kept) == 3
    assert {r.value for r in kept} == {3, 5, 6}


def test_drop_highest_zero_drops_nothing():
    results = _results(3, 5, 1, 6)
    drop_highest(results, ModifierSpec(key="dh", argument=0), _rng(), 6)
    assert all(r.kept for r in results)


def test_drop_lowest_zero_drops_nothing():
    results = _results(3, 5, 1, 6)
    drop_lowest(results, ModifierSpec(key="dl", argument=0), _rng(), 6)
    assert all(r.kept for r in results)


def test_drop_all_dice():
    results = _results(3, 5)
    drop_highest(results, ModifierSpec(key="dh", argument=2), _rng(), 6)
    assert all(not r.kept for r in results)


def test_drop_skips_rerolled_dice():
    results = _results(3, 5, 1, 6)
    results[2].rerolled = True
    results[2].kept = False
    drop_lowest(results, ModifierSpec(key="dl", argument=1), _rng(), 6)
    # Rerolled die stays untouched
    assert results[2].rerolled is True
    assert results[2].kept is False
    # Among active [3, 5, 6], drop lowest 1 → drop 3
    active_kept = [r for r in results if r.kept]
    assert len(active_kept) == 2
    assert {r.value for r in active_kept} == {5, 6}
