"""Tests that verify ExecutionConfig.max_explosions is respected.

Both explode() and _reroll() import MAX_EXPLOSIONS from constants and
use it directly, ignoring the user-provided ExecutionConfig.max_explosions.
These tests verify that a custom max_explosions config value should
control the explosion/reroll safety limit.
"""

from __future__ import annotations

import pytest

from dice import roll
from dice.constants import MAX_EXPLOSIONS
from dice.errors import DiceExecutionError
from dice.execution import ExecutionConfig


class AlwaysMaxRNG:
    """RNG that always returns the maximum value, forcing every die to explode."""

    def randint(self, a: int, b: int) -> int:
        return b


class AlwaysMinRNG:
    """RNG that always returns the minimum value, forcing reroll on =1."""

    def randint(self, a: int, b: int) -> int:
        return a


# ---------------------------------------------------------------------------
# Explode: config.max_explosions should be respected
# ---------------------------------------------------------------------------


def test_explode_respects_config_max_explosions():
    """Exploding dice should stop at config.max_explosions, not the constant."""
    config = ExecutionConfig(max_explosions=3)
    with pytest.raises(DiceExecutionError, match="MAX_EXPLOSIONS_EXCEEDED") as exc_info:
        roll("1d2!", rng=AlwaysMaxRNG(), config=config)

    # The error message should reference the config value (3), not the constant (100)
    assert "3" in exc_info.value.message, (
        f"Expected error to reference config limit 3, got: {exc_info.value.message}. "
        f"explode() is using the hardcoded constant ({MAX_EXPLOSIONS}) instead of config."
    )


def test_explode_with_higher_config_allows_more_explosions():
    """A higher max_explosions config should allow more explosions before failing."""
    config_low = ExecutionConfig(max_explosions=5)
    config_high = ExecutionConfig(max_explosions=10)

    # Both should fail with AlwaysMaxRNG, but with different limits
    with pytest.raises(DiceExecutionError) as exc_low:
        roll("1d2!", rng=AlwaysMaxRNG(), config=config_low)

    with pytest.raises(DiceExecutionError) as exc_high:
        roll("1d2!", rng=AlwaysMaxRNG(), config=config_high)

    assert "5" in exc_low.value.message, (
        f"Low config (5) not reflected in error: {exc_low.value.message}"
    )
    assert "10" in exc_high.value.message, (
        f"High config (10) not reflected in error: {exc_high.value.message}"
    )


def test_explode_within_custom_limit_succeeds():
    """Explosions within the custom limit should succeed, not use the constant."""
    # Use a sequence RNG: first roll is max (triggers explode), second is not
    class ExplodeOnceRNG:
        def __init__(self) -> None:
            self._calls = 0

        def randint(self, a: int, b: int) -> int:
            self._calls += 1
            # First call: initial die roll (max, triggers explode)
            # Second call: explosion roll (not max, stops)
            return b if self._calls <= 1 else a

    config = ExecutionConfig(max_explosions=5)
    result = roll("1d6!", rng=ExplodeOnceRNG(), config=config)
    dice = result.tree["children"][0]["dice"]
    assert len(dice) == 2  # original + 1 explosion


# ---------------------------------------------------------------------------
# Reroll: config.max_explosions should be respected
# ---------------------------------------------------------------------------


def test_reroll_respects_config_max_explosions():
    """Reroll safety limit should use config.max_explosions, not the constant.

    With AlwaysMinRNG, 'r=1' will reroll forever since every replacement
    is also 1. The safety limit should kick in at the config value.
    """
    config = ExecutionConfig(max_explosions=5)

    # Reroll currently uses MAX_EXPLOSIONS as a silent safety valve (breaks
    # out of the loop) rather than raising. Either behavior is acceptable,
    # but it should respect the config value, not the constant.
    result = roll("1d6r=1", rng=AlwaysMinRNG(), config=config)
    dice = result.tree["children"][0]["dice"]
    rerolled_count = sum(1 for d in dice if d.get("rerolled"))

    assert rerolled_count <= config.max_explosions, (
        f"Expected at most {config.max_explosions} rerolls from config, "
        f"got {rerolled_count}. _reroll() is using the hardcoded constant "
        f"({MAX_EXPLOSIONS}) instead of config."
    )
