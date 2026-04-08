"""Tests for target modifier integration with DiceTerm.total.

When a target modifier is active, DiceTerm.total should count matched
(success) dice instead of summing their values.
"""

from dice import roll
from dice.rng import SeededRNG
from dice.terms.dice_term import DiceTerm
from dice.terms.die_result import DieResult


def test_target_total_counts_successes():
    """6d10>7 total should equal the count of dice that rolled > 7."""
    rng = SeededRNG(42)
    result = roll("6d10>7", rng=rng)
    dice_node = result.tree["children"][0]
    assert dice_node["kind"] == "dice_term"
    expected_successes = sum(1 for d in dice_node["dice"] if d.get("matched"))
    assert result.total == expected_successes
    # Sanity: total should never exceed the number of dice
    assert result.total <= len(dice_node["dice"])


def test_target_total_zero_successes():
    """If no dice match the target, total should be 0."""
    # 3d6>10 — impossible to roll > 10 on a d6
    rng = SeededRNG(0)
    result = roll("3d6>10", rng=rng)
    assert result.total == 0


def test_target_total_all_successes():
    """If all dice match, total should equal dice count."""
    # 3d6>0 — all d6 values are >= 1, so all > 0
    rng = SeededRNG(42)
    result = roll("3d6>0", rng=rng)
    assert result.total == 3


def test_dice_term_total_uses_matched_when_target_active():
    """DiceTerm.total should count matched dice when target modifier is active."""
    term = DiceTerm(count=3, faces=10)
    term._has_target = True
    term.results = [
        DieResult(value=8, matched=True),
        DieResult(value=3, matched=False),
        DieResult(value=10, matched=True),
    ]
    term._evaluated = True
    assert term.total == 2  # two matched


def test_dice_term_total_sums_values_without_target():
    """Without target modifiers, DiceTerm.total should sum kept values as usual."""
    term = DiceTerm(count=3, faces=6)
    term.results = [
        DieResult(value=4),
        DieResult(value=2),
        DieResult(value=5),
    ]
    term._evaluated = True
    assert term.total == 11  # 4 + 2 + 5


def test_target_and_failure_total():
    """Target + failure: total = successes - failures.

    DiceTerm with target active: matched dice are successes (+1 each),
    failure dice are failures (-1 each).
    """
    term = DiceTerm(count=5, faces=10)
    term._has_target = True
    term.results = [
        DieResult(value=8, matched=True),  # success
        DieResult(value=3, failure=True),  # failure
        DieResult(value=10, matched=True),  # success
        DieResult(value=5),  # neither
        DieResult(value=1, failure=True),  # failure
    ]
    term._evaluated = True
    assert term.total == 0  # 2 successes - 2 failures


def test_target_with_failure_via_roll():
    """Integration: 3d6>4f<2 — successes > 4, failures < 2.

    Uses only_failures don't overlap with successes.
    """
    rng = SeededRNG(42)
    result = roll("3d6>4f<2", rng=rng)
    dice_node = result.tree["children"][0]
    assert dice_node["kind"] == "dice_term"
    successes = sum(1 for d in dice_node["dice"] if d.get("matched"))
    failures = sum(1 for d in dice_node["dice"] if d.get("failure"))
    assert result.total == successes - failures
