from dice.modifiers.base import ModifierSpec
from dice.modifiers.sort import SORT_MODIFIERS, sort_ascending, sort_descending
from dice.rng import SeededRNG
from dice.terms.die_result import DieResult


def test_sort_ascending_basic():
    """sa should sort results by value ascending."""
    results = [DieResult(value=5), DieResult(value=1), DieResult(value=3)]
    rng = SeededRNG(0)
    out = sort_ascending(results, ModifierSpec(key="sa"), rng, faces=6)
    assert [r.value for r in out] == [1, 3, 5]


def test_sort_descending_basic():
    """sd should sort results by value descending."""
    results = [DieResult(value=1), DieResult(value=5), DieResult(value=3)]
    rng = SeededRNG(0)
    out = sort_descending(results, ModifierSpec(key="sd"), rng, faces=6)
    assert [r.value for r in out] == [5, 3, 1]


def test_sort_bare_s_defaults_to_ascending():
    """Bare 's' should be equivalent to 'sa' (ascending)."""
    results = [DieResult(value=4), DieResult(value=2), DieResult(value=6)]
    rng = SeededRNG(0)
    fn = SORT_MODIFIERS["s"]
    out = fn(results, ModifierSpec(key="s"), rng, faces=6)
    assert [r.value for r in out] == [2, 4, 6]


def test_sort_preserves_die_state():
    """Sorting should not alter kept/exploded/rerolled flags."""
    results = [
        DieResult(value=5, exploded=True),
        DieResult(value=1, kept=False, rerolled=True),
        DieResult(value=3),
    ]
    rng = SeededRNG(0)
    out = sort_ascending(results, ModifierSpec(key="sa"), rng, faces=6)
    # Sorted order: 1, 3, 5
    assert out[0].value == 1
    assert out[0].rerolled is True
    assert out[0].kept is False
    assert out[2].value == 5
    assert out[2].exploded is True


def test_sort_single_die():
    """Sorting a single die is a no-op."""
    results = [DieResult(value=4)]
    rng = SeededRNG(0)
    out = sort_ascending(results, ModifierSpec(key="sa"), rng, faces=6)
    assert [r.value for r in out] == [4]


def test_sort_empty_list():
    """Sorting an empty list should not crash."""
    results: list[DieResult] = []
    rng = SeededRNG(0)
    out = sort_ascending(results, ModifierSpec(key="sa"), rng, faces=6)
    assert out == []


def test_sort_stable_for_equal_values():
    """Equal values should maintain relative order (stable sort)."""
    r1 = DieResult(value=3, exploded=True)
    r2 = DieResult(value=3, exploded=False)
    r3 = DieResult(value=3, rerolled=True)
    results = [r1, r2, r3]
    rng = SeededRNG(0)
    out = sort_ascending(results, ModifierSpec(key="sa"), rng, faces=6)
    assert out[0] is r1
    assert out[1] is r2
    assert out[2] is r3


def test_sort_all_modifiers_registered():
    """All sort keys should be present in SORT_MODIFIERS."""
    assert "s" in SORT_MODIFIERS
    assert "sa" in SORT_MODIFIERS
    assert "sd" in SORT_MODIFIERS
