"""Tests that verify bare 'r' (reroll with no compare point) is rejected.

matches_compare_point defaults to value == faces when compare_point is
None. This makes sense for '!' (explode on max) but causes bare 'r' to
mean "reroll max-value dice" — counterintuitive and not what users
expect. Roll20 treats bare 'r' without a compare point as a syntax
error.

These tests assert that bare 'r' should either be rejected at parse
time or at execution time, rather than silently defaulting to rerolling
the maximum face value.
"""

from __future__ import annotations

import pytest

from dice import roll
from dice.errors import DiceExecutionError
from dice.grammar.parser import parse
from dice.rng import SeededRNG


def test_bare_r_rejected():
    """Bare 'r' should be rejected — it requires a compare point."""
    result = parse("4d6r")
    if result.errors:
        return

    with pytest.raises(DiceExecutionError, match="MISSING_COMPARE_POINT"):
        roll("4d6r", rng=SeededRNG(42))


def test_bare_r_rejected_at_parse_or_execution():
    """Bare 'r' should produce an error at parse time or execution time.

    Roll20 requires a compare point for the reroll modifier. Accepting
    bare 'r' and silently defaulting to 'reroll max face' is a footgun.
    """
    result = parse("2d20r")
    if result.errors:
        # Rejected at parse time — correct
        return

    # If it parses, execution should reject it
    try:
        roll("2d20r", rng=SeededRNG(42))
    except Exception:
        # Rejected at execution time — acceptable
        return

    # If we get here, bare 'r' was accepted and executed silently
    assert False, (
        "Bare 'r' was accepted without error. It should either be rejected "
        "or require an explicit compare point (e.g. 'r<2', 'r=1')."
    )


def test_bare_ro_rejected():
    """Bare 'ro' should be rejected — it requires a compare point."""
    result = parse("4d6ro")
    if result.errors:
        return

    with pytest.raises(DiceExecutionError, match="MISSING_COMPARE_POINT"):
        roll("4d6ro", rng=SeededRNG(42))


def test_reroll_with_compare_point_still_works():
    """'r' with an explicit compare point should continue to work normally."""
    r = roll("4d6r=1", rng=SeededRNG(42))
    dice = r.tree["children"][0]["dice"]
    rerolled = [d for d in dice if d.get("rerolled")]
    if rerolled:
        # Rerolled dice should have had value 1 (the compare point)
        assert all(d["value"] == 1 for d in rerolled)
