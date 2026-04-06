from __future__ import annotations

from dataclasses import dataclass

from dice.constants import MAX_DICE_COUNT, MAX_EXPLOSIONS, MAX_EXPRESSION_DEPTH


@dataclass
class ExecutionConfig:
    """Safety limits and execution options."""

    max_dice: int = MAX_DICE_COUNT
    max_depth: int = MAX_EXPRESSION_DEPTH
    max_explosions: int = MAX_EXPLOSIONS

    def __post_init__(self) -> None:
        if self.max_dice < 1:
            raise ValueError(f"max_dice must be >= 1, got {self.max_dice}")
        if self.max_depth < 1:
            raise ValueError(f"max_depth must be >= 1, got {self.max_depth}")
        if self.max_explosions < 1:
            raise ValueError(f"max_explosions must be >= 1, got {self.max_explosions}")
