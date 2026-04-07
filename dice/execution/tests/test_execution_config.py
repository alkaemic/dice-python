"""Tests that verify ExecutionConfig rejects nonsensical safety limits.

ExecutionConfig is a dataclass with no validation. A caller can pass
zero or negative values that make safety checks behave nonsensically:
max_dice=0 blocks all dice, max_depth=-1 blocks all expressions, etc.

These tests assert that invalid config values should be rejected at
construction time rather than producing confusing runtime errors.
"""

from __future__ import annotations

import pytest

from dice.execution.config import ExecutionConfig

# ---------------------------------------------------------------------------
# Zero values — should be rejected
# ---------------------------------------------------------------------------


def test_max_dice_zero_rejected():
    """max_dice=0 would block all dice rolls — should be rejected."""
    with pytest.raises(ValueError, match="max_dice"):
        ExecutionConfig(max_dice=0)


def test_max_depth_zero_rejected():
    """max_depth=0 would block all expressions — should be rejected."""
    with pytest.raises(ValueError, match="max_depth"):
        ExecutionConfig(max_depth=0)


def test_max_explosions_zero_rejected():
    """max_explosions=0 would block all explosions — should be rejected."""
    with pytest.raises(ValueError, match="max_explosions"):
        ExecutionConfig(max_explosions=0)


# ---------------------------------------------------------------------------
# Negative values — should be rejected
# ---------------------------------------------------------------------------


def test_max_dice_negative_rejected():
    """Negative max_dice is nonsensical — should be rejected."""
    with pytest.raises(ValueError, match="max_dice"):
        ExecutionConfig(max_dice=-1)


def test_max_depth_negative_rejected():
    """Negative max_depth is nonsensical — should be rejected."""
    with pytest.raises(ValueError, match="max_depth"):
        ExecutionConfig(max_depth=-1)


def test_max_explosions_negative_rejected():
    """Negative max_explosions is nonsensical — should be rejected."""
    with pytest.raises(ValueError, match="max_explosions"):
        ExecutionConfig(max_explosions=-5)


# ---------------------------------------------------------------------------
# Valid values — should be accepted
# ---------------------------------------------------------------------------


def test_default_config_valid():
    """Default values should construct without error."""
    config = ExecutionConfig()
    assert config.max_dice > 0
    assert config.max_depth > 0
    assert config.max_explosions > 0


def test_min_valid_config():
    """The smallest valid config (all 1s) should be accepted."""
    config = ExecutionConfig(max_dice=1, max_depth=1, max_explosions=1)
    assert config.max_dice == 1
    assert config.max_depth == 1
    assert config.max_explosions == 1


def test_custom_valid_config():
    """Reasonable custom limits should be accepted."""
    config = ExecutionConfig(max_dice=50, max_depth=5, max_explosions=20)
    assert config.max_dice == 50
