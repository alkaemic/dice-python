"""Tests that verify ParentheticalTerm.expression reflects actual content.

make_parenthetical in parse_actions.py produces lossy expression text
like "(...+...+...)" regardless of actual content. This makes the
expression field in serialized execution trees useless for debugging
or display — every parenthetical looks identical.

These tests assert that the expression field should contain meaningful
text that reflects the actual parenthesized sub-expression.
"""

from __future__ import annotations

from dice.grammar.parser import parse


def _get_parenthetical_expression(notation: str) -> str:
    """Parse a notation string and return the first ParentheticalTerm's expression."""
    result = parse(notation)
    assert not result.errors, f"Parse failed: {result.errors}"
    for child in result.ast.children:
        if child.kind == "parenthetical_term":
            return child.expression
    raise AssertionError(f"No parenthetical term found in {notation!r}")


def test_parenthetical_expression_not_placeholder():
    """The expression field should not be a placeholder like '(...+...)'."""
    expr = _get_parenthetical_expression("(2d6+3)")
    assert "..." not in expr, (
        f"ParentheticalTerm.expression is a placeholder: {expr!r}. "
        f"Expected meaningful text reflecting the actual sub-expression."
    )


def test_parenthetical_expression_contains_dice():
    """The expression field for (2d6+3) should reference '2d6'."""
    expr = _get_parenthetical_expression("(2d6+3)")
    assert "2d6" in expr, f"Expected '2d6' in expression, got {expr!r}."


def test_parenthetical_expression_contains_operator():
    """The expression field for (2d6+3) should contain the '+' operator."""
    expr = _get_parenthetical_expression("(2d6+3)")
    assert "+" in expr, f"Expected '+' in expression, got {expr!r}."


def test_different_parentheticals_have_different_expressions():
    """Two different parentheticals should not produce identical expression text."""
    expr_a = _get_parenthetical_expression("(2d6+3)")
    expr_b = _get_parenthetical_expression("(1d20*2)")
    assert expr_a != expr_b, (
        f"Different sub-expressions produced identical expression text: "
        f"{expr_a!r}. The expression field is lossy."
    )
