"""Tests that verify dice are rolled exactly once per DiceTerm.

These tests detect the double-evaluation bug where evaluate_tree() recurses
into children AND container terms' evaluate() methods also recurse, causing
DiceTerm.evaluate() to be called multiple times.

Each test uses a CountingRNG wrapper that records every randint call. If dice
are rolled more than once, the call count will exceed the expected number.
"""

from __future__ import annotations

from dice.execution.config import ExecutionConfig
from dice.execution.evaluator import _EvalContext, evaluate_tree
from dice.grammar import parse
from dice.rng import RNG


class CountingRNG:
    """RNG wrapper that counts every randint call."""

    def __init__(self, rng: RNG) -> None:
        self._rng = rng
        self.call_count = 0

    def randint(self, a: int, b: int) -> int:
        self.call_count += 1
        return self._rng.randint(a, b)


class FixedRNG:
    """RNG that returns values from a predefined sequence, then raises."""

    def __init__(self, values: list[int]) -> None:
        self._values = list(values)
        self._index = 0
        self.call_count = 0

    def randint(self, a: int, b: int) -> int:
        self.call_count += 1
        if self._index >= len(self._values):
            raise AssertionError(
                f"FixedRNG exhausted after {self._index} calls — "
                f"more randint calls than expected (double evaluation?)"
            )
        val = self._values[self._index]
        self._index += 1
        return val


# ---------------------------------------------------------------------------
# Core double-evaluation detection
# ---------------------------------------------------------------------------


def test_flat_expression_rolls_dice_exactly_once():
    """2d6+3 should make exactly 2 randint calls (one per die)."""
    rng = CountingRNG(FixedRNG([3, 5]))
    parsed = parse("2d6+3")
    assert not parsed.errors

    ctx = _EvalContext(rng=rng, config=ExecutionConfig())
    evaluate_tree(parsed.ast, ctx)

    assert rng.call_count == 2, (
        f"Expected 2 randint calls for 2d6, got {rng.call_count}. "
        f"Dice are being rolled multiple times (double evaluation bug)."
    )


def test_parenthesized_expression_rolls_dice_exactly_once():
    """(2d6+3) should make exactly 2 randint calls despite nesting."""
    rng = CountingRNG(FixedRNG([3, 5]))
    parsed = parse("(2d6+3)")
    assert not parsed.errors

    ctx = _EvalContext(rng=rng, config=ExecutionConfig())
    evaluate_tree(parsed.ast, ctx)

    assert rng.call_count == 2, (
        f"Expected 2 randint calls for (2d6+3), got {rng.call_count}. "
        f"Nesting depth is causing extra evaluations."
    )


def test_deeply_nested_expression_rolls_dice_exactly_once():
    """((2d6+3)) should make exactly 2 randint calls despite double nesting."""
    rng = CountingRNG(FixedRNG([3, 5]))
    parsed = parse("((2d6+3))")
    assert not parsed.errors

    ctx = _EvalContext(rng=rng, config=ExecutionConfig())
    evaluate_tree(parsed.ast, ctx)

    assert rng.call_count == 2, (
        f"Expected 2 randint calls for ((2d6+3)), got {rng.call_count}. "
        f"Each level of nesting is multiplying evaluations."
    )


def test_multiple_dice_terms_each_rolled_once():
    """2d6+3d8 should make exactly 5 randint calls (2 + 3)."""
    rng = CountingRNG(FixedRNG([3, 5, 2, 7, 4]))
    parsed = parse("2d6+3d8")
    assert not parsed.errors

    ctx = _EvalContext(rng=rng, config=ExecutionConfig())
    evaluate_tree(parsed.ast, ctx)

    assert rng.call_count == 5, (
        f"Expected 5 randint calls for 2d6+3d8, got {rng.call_count}."
    )


def test_function_wrapping_does_not_cause_extra_rolls():
    """floor(2d6+1) should make exactly 2 randint calls."""
    rng = CountingRNG(FixedRNG([3, 5]))
    parsed = parse("floor(2d6+1)")
    assert not parsed.errors

    ctx = _EvalContext(rng=rng, config=ExecutionConfig())
    evaluate_tree(parsed.ast, ctx)

    assert rng.call_count == 2, (
        f"Expected 2 randint calls for floor(2d6+1), got {rng.call_count}."
    )


# ---------------------------------------------------------------------------
# Result correctness under single evaluation
# ---------------------------------------------------------------------------


def test_flat_expression_uses_first_roll_results():
    """Verify the final total reflects the intended roll, not a re-roll."""
    # With FixedRNG, the first 2 values are for 2d6. If double-evaluation
    # occurs, DiceTerm would consume values 3 and 4 instead (or exhaust
    # the sequence).
    rng = FixedRNG([3, 5])
    parsed = parse("2d6+3")
    assert not parsed.errors

    ctx = _EvalContext(rng=rng, config=ExecutionConfig())
    evaluate_tree(parsed.ast, ctx)

    # 3 + 5 + 3 = 11
    assert parsed.ast.total == 11, (
        f"Expected total 11 (dice 3+5, plus 3), got {parsed.ast.total}. "
        f"Results may reflect a re-roll rather than the first roll."
    )


def test_parenthesized_total_matches_flat():
    """(2d6)+3 and 2d6+3 should produce identical totals with the same RNG."""
    rng_flat = FixedRNG([3, 5])
    parsed_flat = parse("2d6+3")
    assert not parsed_flat.errors
    evaluate_tree(parsed_flat.ast, _EvalContext(rng=rng_flat, config=ExecutionConfig()))

    rng_nested = FixedRNG([3, 5])
    parsed_nested = parse("(2d6)+3")
    assert not parsed_nested.errors
    evaluate_tree(
        parsed_nested.ast, _EvalContext(rng=rng_nested, config=ExecutionConfig())
    )

    assert parsed_flat.ast.total == parsed_nested.ast.total, (
        f"Flat total {parsed_flat.ast.total} != nested total "
        f"{parsed_nested.ast.total}. Nesting changes results, indicating "
        f"extra RNG consumption from double evaluation."
    )


# ---------------------------------------------------------------------------
# FixedRNG exhaustion: detect unexpected extra rolls
# ---------------------------------------------------------------------------


def test_fixed_rng_exhaustion_detects_extra_rolls():
    """FixedRNG with exactly enough values should not raise.

    If double evaluation occurs, the extra rolls will exhaust the
    sequence and raise AssertionError.
    """
    rng = FixedRNG([4, 2, 6])
    parsed = parse("3d6")
    assert not parsed.errors

    ctx = _EvalContext(rng=rng, config=ExecutionConfig())
    evaluate_tree(parsed.ast, ctx)

    # Verify all values were consumed exactly once
    assert rng._index == 3, (
        f"Expected exactly 3 values consumed, got {rng._index}."
    )
    assert rng.call_count == 3, (
        f"Expected 3 randint calls, got {rng.call_count}."
    )


# ---------------------------------------------------------------------------
# Safety limits still enforced (regression guard)
# ---------------------------------------------------------------------------


def test_safety_limits_still_enforced_with_idempotent_evaluate():
    """MAX_DICE_EXCEEDED should still fire even with the idempotency guard."""
    config = ExecutionConfig(max_dice=2)
    rng = FixedRNG([1, 2, 3, 4, 5])
    parsed = parse("3d6")
    assert not parsed.errors

    ctx = _EvalContext(rng=rng, config=config)
    try:
        evaluate_tree(parsed.ast, ctx)
        assert False, "Expected DiceExecutionError for MAX_DICE_EXCEEDED"
    except Exception as exc:
        assert "MAX_DICE_EXCEEDED" in str(exc)
