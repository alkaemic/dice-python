"""Tests that verify the grammar handles an arbitrary number of modifiers.

The grammar currently uses nested Optional() to capture modifiers, which
caps the count at 4 per die term. A 5th modifier causes a parse error
even though it is valid notation. These tests verify that the grammar
should accept any number of modifiers without an arbitrary limit.
"""

from __future__ import annotations

from dice.grammar.parser import parse


def test_one_modifier_parses():
    result = parse("4d6kh3")
    assert not result.errors
    assert result.ast.children[0].modifier_strings == ["kh3"]


def test_two_modifiers_parse():
    result = parse("4d6r=1kh3")
    assert not result.errors
    assert result.ast.children[0].modifier_strings == ["r=1", "kh3"]


def test_three_modifiers_parse():
    result = parse("4d6r=1kh3!")
    assert not result.errors
    assert result.ast.children[0].modifier_strings == ["r=1", "kh3", "!"]


def test_four_modifiers_parse():
    """Four modifiers is the current hard limit — this should pass."""
    result = parse("4d6r=1kh3!dh1")
    assert not result.errors
    assert result.ast.children[0].modifier_strings == ["r=1", "kh3", "!", "dh1"]


def test_five_modifiers_parse():
    """Five modifiers should parse — the grammar should not impose a cap."""
    result = parse("4d6r=1kh3!dh1dl1")
    assert not result.errors, (
        f"5 modifiers caused a parse error: {result.errors[0]}. "
        f"The grammar caps modifiers at 4 due to nested Optional()."
    )
    assert result.ast.children[0].modifier_strings == ["r=1", "kh3", "!", "dh1", "dl1"]


def test_six_modifiers_parse():
    """Six modifiers should parse without error."""
    result = parse("8d6ro=1r<2kh4!dh1dl1")
    assert not result.errors, (
        f"6 modifiers caused a parse error: {result.errors[0]}. "
        f"The grammar caps modifiers at 4 due to nested Optional()."
    )
    assert len(result.ast.children[0].modifier_strings) == 6


def test_modifier_limit_does_not_silently_truncate():
    """If more than 4 modifiers are given, none should be silently lost."""
    result = parse("4d6r=1kh3!dh1dl1")
    if not result.errors:
        mods = result.ast.children[0].modifier_strings
        assert "dl1" in mods, (
            f"The 5th modifier 'dl1' was silently dropped. "
            f"Captured modifiers: {mods}"
        )
