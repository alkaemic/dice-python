"""Tests that verify bare 'k' modifier works end-to-end.

The grammar accepts 'k' as a keep shorthand (e.g. 2d20k1), which is
common Roll20 syntax meaning "keep highest 1". However, the modifier
parser's _MODIFIER_KEYS list does not include 'k', so execution fails
with ValueError even though parsing succeeds.

These tests verify that:
1. The grammar accepts bare 'k' (this already works)
2. The modifier parser can tokenize 'k' notation (currently fails)
3. Bare 'k' behaves identically to 'kh' at execution time (currently fails)
"""

from __future__ import annotations

import pytest

from dice import roll
from dice.grammar.parser import parse
from dice.modifiers.parser import parse_modifier_string
from dice.rng import SeededRNG


# ---------------------------------------------------------------------------
# Grammar level — these pass (grammar already accepts 'k')
# ---------------------------------------------------------------------------


def test_grammar_accepts_bare_k():
    """The grammar should accept 2d20k1 without parse errors."""
    result = parse("2d20k1")
    assert not result.errors
    dt = result.ast.children[0]
    assert dt.modifier_strings == ["k1"]


def test_grammar_accepts_bare_k_no_argument():
    """The grammar should accept 2d20k (keep highest 1, implicit)."""
    result = parse("2d20k")
    assert not result.errors
    dt = result.ast.children[0]
    assert dt.modifier_strings == ["k"]


# ---------------------------------------------------------------------------
# Modifier parser level — these fail (k not in _MODIFIER_KEYS)
# ---------------------------------------------------------------------------


def test_modifier_parser_recognizes_bare_k():
    """parse_modifier_string should recognize 'k1' as a valid modifier."""
    specs = parse_modifier_string("k1")
    assert len(specs) == 1
    assert specs[0].key == "k"
    assert specs[0].argument == 1


def test_modifier_parser_recognizes_bare_k_no_argument():
    """parse_modifier_string should recognize 'k' without an argument."""
    specs = parse_modifier_string("k")
    assert len(specs) == 1
    assert specs[0].key == "k"
    assert specs[0].argument is None


# ---------------------------------------------------------------------------
# Execution level — these fail (no modifier registered for 'k')
# ---------------------------------------------------------------------------


def test_bare_k_executes_without_error():
    """roll('2d20k1') should not raise — 'k' should be a valid modifier."""
    result = roll("2d20k1", rng=SeededRNG(42))
    assert isinstance(result.total, (int, float))


def test_bare_k_is_alias_for_kh():
    """2d20k1 should produce the same result as 2d20kh1."""
    result_k = roll("2d20k1", rng=SeededRNG(42))
    result_kh = roll("2d20kh1", rng=SeededRNG(42))
    assert result_k.total == result_kh.total, (
        f"2d20k1 gave {result_k.total} but 2d20kh1 gave {result_kh.total}. "
        f"Bare 'k' should be an alias for 'kh' (keep highest)."
    )


def test_bare_k_keeps_correct_number():
    """4d6k3 should keep 3 dice (same as 4d6kh3)."""
    result = roll("4d6k3", rng=SeededRNG(42))
    dice = result.tree["children"][0]["dice"]
    kept = [d for d in dice if d["kept"]]
    assert len(kept) == 3, (
        f"Expected 3 kept dice for 4d6k3, got {len(kept)}."
    )


def test_bare_k_default_keeps_one():
    """2d20k (no argument) should keep 1 die (same as 2d20kh1)."""
    result_k = roll("2d20k", rng=SeededRNG(42))
    result_kh1 = roll("2d20kh1", rng=SeededRNG(42))
    assert result_k.total == result_kh1.total, (
        f"2d20k gave {result_k.total} but 2d20kh1 gave {result_kh1.total}. "
        f"Bare 'k' with no argument should default to keep highest 1."
    )
