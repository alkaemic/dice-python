"""Tests verifying that parser.py handles exceptions correctly.

The parser should only catch pyparsing's own exceptions as parse errors.
Other exception types (TypeError, AttributeError, etc.) indicate bugs
and must propagate to the caller. RecursionError gets a distinct
EXPRESSION_TOO_COMPLEX error code.
"""

from __future__ import annotations

from unittest.mock import patch

import pytest
from pyparsing import ParseBaseException, ParseException

from dice.grammar import parse


def test_type_error_propagates():
    """A TypeError from a bug in parse_notation should propagate to the caller."""
    with patch(
        "dice.grammar.notation.parse_notation",
        side_effect=TypeError("unsupported operand type(s) for +: 'NoneType' and 'int'"),
    ):
        with pytest.raises(TypeError, match="NoneType"):
            parse("1d6")


def test_attribute_error_propagates():
    """An AttributeError from a bug should propagate to the caller."""
    with patch(
        "dice.grammar.notation.parse_notation",
        side_effect=AttributeError("'NoneType' object has no attribute 'append'"),
    ):
        with pytest.raises(AttributeError, match="NoneType"):
            parse("2d20+5")


def test_key_error_propagates():
    """A KeyError from a missing registry entry should propagate."""
    with patch(
        "dice.grammar.notation.parse_notation",
        side_effect=KeyError("missing_modifier"),
    ):
        with pytest.raises(KeyError, match="missing_modifier"):
            parse("1d6")


def test_value_error_propagates():
    """A ValueError from internal logic should propagate to the caller."""
    with patch(
        "dice.grammar.notation.parse_notation",
        side_effect=ValueError("invalid literal for int() with base 10: 'abc'"),
    ):
        with pytest.raises(ValueError, match="invalid literal"):
            parse("1d6")


def test_recursion_error_produces_expression_too_complex():
    """RecursionError should produce EXPRESSION_TOO_COMPLEX, not generic PARSE_ERROR."""
    with patch(
        "dice.grammar.notation.parse_notation",
        side_effect=RecursionError("maximum recursion depth exceeded"),
    ):
        result = parse("1d6")

    assert len(result.errors) == 1
    assert result.errors[0].code == "EXPRESSION_TOO_COMPLEX"
    assert "deeply nested" in result.errors[0].message


def test_parse_exception_still_caught_as_parse_error():
    """pyparsing's ParseException should still become a PARSE_ERROR result."""
    with patch(
        "dice.grammar.notation.parse_notation",
        side_effect=ParseException("Expected end of text", loc=0),
    ):
        result = parse("1d6")

    assert len(result.errors) == 1
    assert result.errors[0].code == "PARSE_ERROR"


def test_parse_base_exception_still_caught_as_parse_error():
    """pyparsing's ParseBaseException should still become a PARSE_ERROR result."""
    with patch(
        "dice.grammar.notation.parse_notation",
        side_effect=ParseBaseException("parse failed", loc=0),
    ):
        result = parse("1d6")

    assert len(result.errors) == 1
    assert result.errors[0].code == "PARSE_ERROR"


def test_invalid_syntax_still_produces_parse_error():
    """Real invalid syntax should still produce PARSE_ERROR (no mocking)."""
    result = parse("xyz")
    assert len(result.errors) == 1
    assert result.errors[0].code == "PARSE_ERROR"
