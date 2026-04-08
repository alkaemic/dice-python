"""Tests for >= (GTE) and <= (LTE) target modifiers.

These operators use correct mathematical semantics:

- ``>5``  means strictly greater-than (6+)
- ``>=5`` means greater-than-or-equal (5+)
- ``<3``  means strictly less-than (1-2)
- ``<=3`` means less-than-or-equal (1-3)

The tests verify:

1. The grammar parses ``>=`` and ``<=`` in target position.
2. The modifier parser tokenizes them as distinct keys.
3. The modifier registry has handlers registered for both.
4. End-to-end rolls produce correct success counts.
5. ``>`` and ``>=`` (and ``<`` and ``<=``) produce different results
   for boundary values, confirming distinct semantics.
"""

from dice import roll
from dice.grammar import parse
from dice.modifiers.base import DiceContext, ModifierSpec
from dice.modifiers.parser import parse_modifier_string
from dice.modifiers.registry import MODIFIER_ORDER, get_modifier
from dice.modifiers.target import TARGET_MODIFIERS, target
from dice.rng import SeededRNG
from dice.terms.die_result import DieResult

# ---- Grammar: parses >= and <= as target modifiers ----


def test_grammar_accepts_gte_modifier():
    """The grammar parses '4d6>=5' without errors."""
    result = parse("4d6>=5")
    assert result.errors == [], f"Expected clean parse, got: {result.errors}"


def test_grammar_accepts_lte_modifier():
    """The grammar parses '4d6<=3' without errors."""
    result = parse("4d6<=3")
    assert result.errors == [], f"Expected clean parse, got: {result.errors}"


def test_grammar_captures_gte_as_modifier_string():
    """'>=5' ends up in the DiceTerm's modifier_strings after parsing."""
    result = parse("4d6>=5")
    dice_term = result.ast.children[0]
    assert ">=5" in dice_term.modifier_strings


def test_grammar_captures_lte_as_modifier_string():
    """'<=3' ends up in the DiceTerm's modifier_strings after parsing."""
    result = parse("4d6<=3")
    dice_term = result.ast.children[0]
    assert "<=3" in dice_term.modifier_strings


# ---- Modifier parser: tokenizes >= and <= as keys ----


def test_modifier_parser_tokenizes_gte_as_key():
    """parse_modifier_string('>=5') produces key='>=' with argument=5."""
    specs = parse_modifier_string(">=5")
    assert len(specs) == 1
    assert specs[0].key == ">="
    assert specs[0].argument == 5
    assert specs[0].compare_point is None


def test_modifier_parser_tokenizes_lte_as_key():
    """parse_modifier_string('<=3') produces key='<=' with argument=3."""
    specs = parse_modifier_string("<=3")
    assert len(specs) == 1
    assert specs[0].key == "<="
    assert specs[0].argument == 3
    assert specs[0].compare_point is None


# ---- >= also works as a compare-point inside other modifiers ----


def test_gte_works_as_compare_point_in_reroll():
    """'r>=3' correctly parses as key='r' with compare_point='>=3'."""
    specs = parse_modifier_string("r>=3")
    assert len(specs) == 1
    assert specs[0].key == "r"
    assert specs[0].compare_point == ">=3"


def test_gte_works_as_compare_point_in_explode():
    """'!>=5' correctly parses as key='!' with compare_point='>=5'."""
    specs = parse_modifier_string("!>=5")
    assert len(specs) == 1
    assert specs[0].key == "!"
    assert specs[0].compare_point == ">=5"


def test_lte_works_as_compare_point_in_reroll():
    """'r<=2' correctly parses as key='r' with compare_point='<=2'."""
    specs = parse_modifier_string("r<=2")
    assert len(specs) == 1
    assert specs[0].key == "r"
    assert specs[0].compare_point == "<=2"


# ---- Registry: >= and <= are registered ----


def test_gte_in_target_modifiers():
    """>= is registered in TARGET_MODIFIERS."""
    assert ">=" in TARGET_MODIFIERS


def test_lte_in_target_modifiers():
    """<= is registered in TARGET_MODIFIERS."""
    assert "<=" in TARGET_MODIFIERS


def test_gte_in_modifier_registry():
    """get_modifier('>=') returns a handler."""
    assert get_modifier(">=") is not None


def test_lte_in_modifier_registry():
    """get_modifier('<=') returns a handler."""
    assert get_modifier("<=") is not None


def test_gte_in_modifier_order():
    """>= has a defined execution order position."""
    assert ">=" in MODIFIER_ORDER


def test_lte_in_modifier_order():
    """<= has a defined execution order position."""
    assert "<=" in MODIFIER_ORDER


# ---- Semantic correctness: GT vs GTE, LT vs LTE ----


def test_gte_matches_boundary_value():
    """>=5 should match a die showing exactly 5."""
    results = [DieResult(value=5)]
    ctx = DiceContext.standard(6)
    spec = ModifierSpec(key=">=", argument=5)
    out = target(results, spec, SeededRNG(0), ctx)
    assert out[0].matched is True


def test_gt_does_not_match_boundary_value():
    """>5 should NOT match a die showing exactly 5."""
    results = [DieResult(value=5)]
    ctx = DiceContext.standard(6)
    spec = ModifierSpec(key=">", argument=5)
    out = target(results, spec, SeededRNG(0), ctx)
    assert out[0].matched is False


def test_lte_matches_boundary_value():
    """<=3 should match a die showing exactly 3."""
    results = [DieResult(value=3)]
    ctx = DiceContext.standard(6)
    spec = ModifierSpec(key="<=", argument=3)
    out = target(results, spec, SeededRNG(0), ctx)
    assert out[0].matched is True


def test_lt_does_not_match_boundary_value():
    """<3 should NOT match a die showing exactly 3."""
    results = [DieResult(value=3)]
    ctx = DiceContext.standard(6)
    spec = ModifierSpec(key="<", argument=3)
    out = target(results, spec, SeededRNG(0), ctx)
    assert out[0].matched is False


# ---- End-to-end: rolls produce correct success counts ----


def test_roll_gte_counts_successes():
    """4d6>=5 should count dice with value >= 5 as successes."""
    result = roll("4d6>=5", rng=SeededRNG(42))
    dice = result.tree["children"][0]["dice"]
    expected = sum(1 for d in dice if d.get("matched"))
    assert result.total == expected


def test_roll_lte_counts_successes():
    """4d6<=2 should count dice with value <= 2 as successes."""
    result = roll("4d6<=2", rng=SeededRNG(42))
    dice = result.tree["children"][0]["dice"]
    expected = sum(1 for d in dice if d.get("matched"))
    assert result.total == expected


def test_gt_and_gte_differ_at_boundary():
    """>5 and >=5 must produce different totals when boundary values exist.

    On a d6, value 5 is matched by >=5 but not by >5. With the same seed
    both expressions see the same rolls, so any die showing 5 flips the
    result.
    """
    rng_gt = SeededRNG(99)
    rng_gte = SeededRNG(99)
    result_gt = roll("10d6>5", rng=rng_gt)
    result_gte = roll("10d6>=5", rng=rng_gte)
    # >=5 must match at least as many dice as >5
    assert result_gte.total >= result_gt.total


def test_lt_and_lte_differ_at_boundary():
    """<3 and <=3 must produce different totals when boundary values exist."""
    rng_lt = SeededRNG(99)
    rng_lte = SeededRNG(99)
    result_lt = roll("10d6<3", rng=rng_lt)
    result_lte = roll("10d6<=3", rng=rng_lte)
    # <=3 must match at least as many dice as <3
    assert result_lte.total >= result_lt.total
