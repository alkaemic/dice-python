"""Tests proving operator precedence is broken (CODE_REVIEW.md #1).

The _flatten_infix parse action destroys pyparsing's infixNotation nesting.
Both make_mul_div and make_add_sub return flat lists, so when pyparsing
splices the mul/div result back into the add/sub level, all operators are
evaluated strictly left-to-right, ignoring precedence.

Expected: 1d20+3*2 => 1d20 + (3*2)
Actual:   1d20+3*2 => (1d20 + 3) * 2
"""

from dice import roll
from dice.grammar import parse
from dice.rng import SeededRNG


def test_precedence_tree_structure():
    """The parse tree for '1d20+3*2' should have 3 top-level children,
    with children[2] being a grouped term (not a flat numeric_term)."""
    r = parse("1d20+3*2")
    assert len(r.errors) == 0
    children = r.ast.children

    # If precedence is correct, the top level should be:
    #   [dice_term(1d20), operator_term(+), <grouped 3*2>]
    # i.e. exactly 3 children.
    #
    # BUG: _flatten_infix destroys the grouping, producing 5 flat children:
    #   [dice_term, op(+), numeric(3), op(*), numeric(2)]
    assert len(children) == 3, (
        f"Expected 3 top-level children (dice, +, grouped_mul), "
        f"got {len(children)}: {[c.kind for c in children]}"
    )


def test_precedence_total_add_then_mul():
    """1d20+3*2 should compute 1d20 + (3*2), not (1d20+3)*2."""
    result = roll("1d20+3*2", rng=SeededRNG(42))
    tree = result.tree
    d20_total = tree["children"][0]["total"]

    correct = d20_total + 3 * 2
    wrong = (d20_total + 3) * 2

    assert result.total == correct, (
        f"Precedence broken: d20={d20_total}, "
        f"expected d20+3*2={correct}, got {result.total} "
        f"(matches (d20+3)*2={wrong})"
    )


def test_precedence_total_sub_then_mul():
    """1d20-1*3 should compute 1d20 - (1*3), not (1d20-1)*3."""
    result = roll("1d20-1*3", rng=SeededRNG(99))
    tree = result.tree
    d20_total = tree["children"][0]["total"]

    correct = d20_total - 1 * 3
    assert result.total == correct, (
        f"Precedence broken: d20={d20_total}, "
        f"expected d20-1*3={correct}, got {result.total}"
    )


def test_precedence_total_mul_then_add():
    """2*3+4 should be (2*3)+4=10, not 2*(3+4)=14."""
    result = roll("2*3+4")
    assert result.total == 10, (
        f"Expected 2*3+4=10, got {result.total}"
    )


def test_precedence_total_division():
    """10+6/2 should be 10+(6/2)=13, not (10+6)/2=8."""
    result = roll("10+6/2")
    assert result.total == 13, (
        f"Expected 10+6/2=13, got {result.total}"
    )


def test_precedence_mixed_mul_div_with_dice():
    """1d6+2*3-4/2 should be 1d6 + (2*3) - (4/2) = 1d6 + 6 - 2 = 1d6+4."""
    result = roll("1d6+2*3-4/2", rng=SeededRNG(7))
    tree = result.tree
    d6_total = tree["children"][0]["total"]

    correct = d6_total + 2 * 3 - 4 / 2
    assert result.total == correct, (
        f"Precedence broken: d6={d6_total}, "
        f"expected d6+2*3-4/2={correct}, got {result.total}"
    )


def test_precedence_pure_arithmetic():
    """Pure arithmetic: 2+3*4-1 should be 2+(3*4)-1=13."""
    result = roll("2+3*4-1")
    assert result.total == 13, (
        f"Expected 2+3*4-1=13, got {result.total}"
    )


def test_explicit_parens_still_work():
    """Explicit parentheses should override natural precedence.
    (1d20+3)*2 should compute (1d20+3)*2."""
    result = roll("(1d20+3)*2", rng=SeededRNG(42))

    # The top-level is a mul/div ParentheticalTerm wrapping
    # [(1d20+3), *, 2]. Find the d20 inside the explicit parens.
    tree = result.tree
    # Navigate to the inner parenthetical that contains the d20
    mul_group = tree["children"][0]
    assert mul_group["kind"] == "parenthetical_term"
    explicit_paren = mul_group["children"][0]
    assert explicit_paren["kind"] == "parenthetical_term"
    d20_total = explicit_paren["children"][0]["total"]

    correct = (d20_total + 3) * 2
    assert result.total == correct, (
        f"Explicit parens broken: d20={d20_total}, "
        f"expected (d20+3)*2={correct}, got {result.total}"
    )
