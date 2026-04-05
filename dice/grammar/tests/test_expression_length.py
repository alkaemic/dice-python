"""Tests that verify MAX_EXPRESSION_LENGTH is enforced during parsing.

The constant MAX_EXPRESSION_LENGTH = 500 is defined in dice/constants.py
but parse() never checks it. These tests assert the expected behavior:
expressions exceeding the limit should return a DiceParseError, not parse
successfully.
"""

from __future__ import annotations

from dice.constants import MAX_EXPRESSION_LENGTH
from dice.errors import DiceParseError
from dice.grammar.parser import parse


def test_expression_at_limit_parses_successfully():
    """An expression exactly at the length limit should parse without errors."""
    # Build an expression of exactly MAX_EXPRESSION_LENGTH characters.
    # "1+1+1+..." → n terms with (n-1) separators = 2n - 1 chars.
    # For an even limit like 500, we can't hit it exactly with single-digit
    # terms and single-char operators (always odd). Use a 2-digit number to
    # pad: "10+1+1+..." where "10" is 2 chars → total = 2 + (n-1)*2 = 2n.
    # Solve: 2n = 500 → n = 250.
    n = MAX_EXPRESSION_LENGTH // 2
    expr = "10" + "+1" * (n - 1)
    assert len(expr) == MAX_EXPRESSION_LENGTH, (
        f"Test setup: expected {MAX_EXPRESSION_LENGTH} chars, got {len(expr)}"
    )

    result = parse(expr)
    assert not result.errors, (
        f"Expression of exactly {MAX_EXPRESSION_LENGTH} chars should parse, "
        f"but got errors: {result.errors}"
    )


def test_expression_exceeding_limit_returns_error():
    """An expression exceeding MAX_EXPRESSION_LENGTH should return an error."""
    n = (MAX_EXPRESSION_LENGTH + 1) // 2 + 1  # one term beyond the limit
    expr = "+".join(["1"] * n)
    assert len(expr) > MAX_EXPRESSION_LENGTH

    result = parse(expr)
    assert len(result.errors) > 0, (
        f"Expression of {len(expr)} chars (limit is {MAX_EXPRESSION_LENGTH}) "
        f"parsed successfully — MAX_EXPRESSION_LENGTH is not enforced."
    )


def test_expression_exceeding_limit_error_type():
    """The error returned for a too-long expression should be a DiceParseError."""
    expr = "1+" * MAX_EXPRESSION_LENGTH + "1"  # well over the limit
    assert len(expr) > MAX_EXPRESSION_LENGTH

    result = parse(expr)
    assert len(result.errors) > 0, (
        "Expected an error for over-length expression, got none."
    )
    assert isinstance(result.errors[0], DiceParseError)


def test_expression_exceeding_limit_error_code():
    """The error code should clearly indicate the expression was too long."""
    expr = "1+" * MAX_EXPRESSION_LENGTH + "1"
    result = parse(expr)
    assert len(result.errors) > 0, (
        "Expected an error for over-length expression, got none."
    )
    assert result.errors[0].code == "EXPRESSION_TOO_LONG", (
        f"Expected error code 'EXPRESSION_TOO_LONG', "
        f"got {result.errors[0].code!r}"
    )


def test_expression_exceeding_limit_preserves_original_expression():
    """The error and ParseResult should carry the original expression."""
    expr = "+".join(["1"] * 400)
    assert len(expr) > MAX_EXPRESSION_LENGTH

    result = parse(expr)
    assert len(result.errors) > 0, (
        "Expected an error for over-length expression, got none."
    )
    assert result.expression == expr


def test_very_long_expression_does_not_parse():
    """A pathologically long expression should be rejected, not fed to pyparsing."""
    expr = "+".join(["1"] * 5000)  # 9999 chars
    assert len(expr) > MAX_EXPRESSION_LENGTH

    result = parse(expr)
    assert len(result.errors) > 0, (
        f"A {len(expr)}-char expression parsed without error — "
        f"MAX_EXPRESSION_LENGTH ({MAX_EXPRESSION_LENGTH}) is not enforced."
    )
