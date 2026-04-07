"""Depth-first AST evaluator with safety limit enforcement."""

from __future__ import annotations

from dice.errors import DiceExecutionError
from dice.execution.config import ExecutionConfig
from dice.rng import RNG
from dice.terms.base import RollTerm
from dice.terms.dice_term import DiceTerm


class _EvalContext:
    """Mutable state tracked across the recursive evaluation walk."""

    def __init__(self, rng: RNG, config: ExecutionConfig) -> None:
        self.rng = rng
        self.config = config
        self.total_dice_rolled = 0
        self.current_depth = 0


def evaluate_tree(root: RollTerm, ctx: _EvalContext) -> None:
    """Recursively evaluate *root* and all its children, enforcing limits."""
    ctx.current_depth += 1
    if ctx.current_depth > ctx.config.max_depth:
        raise DiceExecutionError(
            code="MAX_DEPTH_EXCEEDED",
            message=(
                f"Expression depth ({ctx.current_depth}) "
                f"exceeds maximum ({ctx.config.max_depth})"
            ),
        )

    try:
        # If this node has children, evaluate them first (depth-first).
        # Most terms have children: list[RollTerm], but GroupTerm has
        # children: list[list[RollTerm]], so we recurse into nested lists.
        children: list[RollTerm] | None = getattr(root, "children", None)
        if children is not None:
            for child in children:
                if isinstance(child, RollTerm):
                    evaluate_tree(child, ctx)
                elif isinstance(child, list):
                    for sub_child in child:
                        if isinstance(sub_child, RollTerm):
                            evaluate_tree(sub_child, ctx)

        # For dice terms, enforce dice count limit before rolling
        # and propagate max_explosions from config
        if isinstance(root, DiceTerm) and not root._evaluated:
            root.max_explosions = ctx.config.max_explosions
            ctx.total_dice_rolled += root.count
            if ctx.total_dice_rolled > ctx.config.max_dice:
                raise DiceExecutionError(
                    code="MAX_DICE_EXCEEDED",
                    message=(
                        f"Total dice rolled ({ctx.total_dice_rolled}) "
                        f"exceeds maximum ({ctx.config.max_dice})"
                    ),
                )

        # Evaluate the node itself
        root.evaluate(ctx.rng)
    finally:
        ctx.current_depth -= 1
