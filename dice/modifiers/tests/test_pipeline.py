from dice.modifiers.base import DiceContext, ModifierSpec
from dice.modifiers.parser import parse_modifier_string
from dice.modifiers.registry import apply_modifiers
from dice.rng import SeededRNG
from dice.terms import DiceTerm
from dice.terms.die_result import DieResult

_ctx = DiceContext.standard


def test_order_independence_kh_r():
    """4d6r=1kh3 and 4d6kh3r=1 must produce identical results."""
    dt1 = DiceTerm(count=4, faces=6, modifier_strings=["r=1", "kh3"])
    dt2 = DiceTerm(count=4, faces=6, modifier_strings=["kh3", "r=1"])
    dt1.evaluate(SeededRNG(42))
    dt2.evaluate(SeededRNG(42))
    assert [r.value for r in dt1.results] == [r.value for r in dt2.results]
    assert [r.kept for r in dt1.results] == [r.kept for r in dt2.results]
    assert dt1.total == dt2.total


def test_order_independence_explode_kh():
    """2d6!kh1 and 2d6kh1! must produce identical results."""
    dt1 = DiceTerm(count=2, faces=6, modifier_strings=["!", "kh1"])
    dt2 = DiceTerm(count=2, faces=6, modifier_strings=["kh1", "!"])
    dt1.evaluate(SeededRNG(99))
    dt2.evaluate(SeededRNG(99))
    assert [r.value for r in dt1.results] == [r.value for r in dt2.results]
    assert dt1.total == dt2.total


def test_apply_modifiers_sorts_by_order():
    """Verify that apply_modifiers applies reroll before keep."""
    rng = SeededRNG(42)
    results = [
        DieResult(value=1),
        DieResult(value=5),
        DieResult(value=3),
        DieResult(value=6),
    ]
    specs = [
        ModifierSpec(key="kh", argument=3),
        ModifierSpec(key="r", compare_point="=1"),
    ]
    # Even though kh comes first in the list, reroll runs first (position 4 < 5)
    results = apply_modifiers(results, specs, rng, ctx=_ctx(6))
    rerolled = [r for r in results if r.rerolled]
    assert len(rerolled) >= 1
    kept = [r for r in results if r.kept]
    assert len(kept) == 3


def test_explode_then_keep():
    """Exploded dice participate in keep selection."""
    rng = SeededRNG(42)
    results = [DieResult(value=6), DieResult(value=2)]
    specs = parse_modifier_string("!kh1")
    results = apply_modifiers(results, specs, rng, ctx=_ctx(6))
    kept = [r for r in results if r.kept]
    assert len(kept) == 1
    # The kept die should be the highest among all (including exploded)
    all_values = [r.value for r in results]
    assert kept[0].value == max(all_values)
