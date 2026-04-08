"""Tests that verify GroupTerm works correctly with evaluate_tree.

GroupTerm.children is list[list[RollTerm]] (nested lists), but
evaluate_tree uses getattr(root, "children", None) and iterates
assuming a flat list[RollTerm]. This causes an AttributeError when
evaluate_tree tries to call .evaluate() on a plain list.

GroupTerm is not currently produced by the parser, so this only
manifests when constructing GroupTerms programmatically and evaluating
them through the executor. These tests verify that evaluate_tree
handles GroupTerm correctly.
"""

from __future__ import annotations

from dice.errors import DiceExecutionError
from dice.execution.config import ExecutionConfig
from dice.execution.evaluator import _EvalContext, evaluate_tree
from dice.rng import SeededRNG
from dice.terms.dice_term import DiceTerm
from dice.terms.group_term import GroupTerm
from dice.terms.numeric_term import NumericTerm
from dice.terms.operator_term import OperatorTerm
from dice.terms.roll_expression import RollExpression


def test_evaluate_tree_with_group_term_does_not_crash():
    """evaluate_tree should handle GroupTerm without AttributeError."""
    expr1 = [DiceTerm(count=2, faces=6)]
    expr2 = [DiceTerm(count=3, faces=6)]
    group = GroupTerm(children=[expr1, expr2], modifier_strings=["kh1"])

    ctx = _EvalContext(rng=SeededRNG(42), config=ExecutionConfig())
    evaluate_tree(group, ctx)

    assert group._evaluated
    assert isinstance(group.total, (int, float))


def test_evaluate_tree_group_term_computes_total():
    """GroupTerm total should reflect the kept sub-expression."""
    # Use NumericTerms for deterministic totals
    expr1 = [NumericTerm(value=10)]
    expr2 = [NumericTerm(value=20)]
    group = GroupTerm(children=[expr1, expr2], modifier_strings=["kh1"])

    ctx = _EvalContext(rng=SeededRNG(0), config=ExecutionConfig())
    evaluate_tree(group, ctx)

    assert (
        group.total == 20
    ), f"Expected kh1 to keep the higher sub-expression (20), got {group.total}"


def test_evaluate_tree_group_term_nested_in_expression():
    """A GroupTerm nested inside a RollExpression should evaluate correctly."""
    expr1 = [NumericTerm(value=5)]
    expr2 = [NumericTerm(value=15)]
    group = GroupTerm(children=[expr1, expr2], modifier_strings=["kh1"])

    root = RollExpression(
        expression="{5, 15}kh1+2",
        children=[group, OperatorTerm(operator="+"), NumericTerm(value=2)],
    )

    ctx = _EvalContext(rng=SeededRNG(0), config=ExecutionConfig())
    evaluate_tree(root, ctx)

    assert root.total == 17, f"Expected {'{'}5, 15{'}'}kh1+2 = 17, got {root.total}"


def test_evaluate_tree_group_term_with_dice():
    """GroupTerm containing DiceTerms should roll and keep correctly."""
    expr1 = [DiceTerm(count=1, faces=6)]
    expr2 = [DiceTerm(count=1, faces=6)]
    group = GroupTerm(children=[expr1, expr2], modifier_strings=["kh1"])

    ctx = _EvalContext(rng=SeededRNG(42), config=ExecutionConfig())
    evaluate_tree(group, ctx)

    # One sub-expression should be kept, one dropped
    kept_count = sum(1 for k in group._kept if k)
    assert kept_count == 1, f"Expected 1 kept sub-expression, got {kept_count}"


# ---------------------------------------------------------------------------
# Safety gap: GroupTerm children bypass safety limits
#
# evaluate_tree iterates root.children expecting list[RollTerm], but
# GroupTerm.children is list[list[RollTerm]]. The inner lists fail the
# isinstance(child, RollTerm) check, so evaluate_tree never recurses
# into them. GroupTerm.evaluate() handles its own children directly,
# bypassing dice count tracking, depth limits, and max_explosions
# propagation.
# ---------------------------------------------------------------------------


def test_group_term_children_dice_not_tracked_in_context():
    """Dice inside GroupTerm children should be counted in ctx.total_dice_rolled.

    evaluate_tree skips GroupTerm's nested children (list[list[RollTerm]]),
    so DiceTerms inside them are never counted against the dice limit.
    GroupTerm.evaluate() rolls them directly, bypassing the safety check.
    """
    # Set max_dice=5. Two children with 3 dice each = 6 total, should exceed.
    expr1 = [DiceTerm(count=3, faces=6)]
    expr2 = [DiceTerm(count=3, faces=6)]
    group = GroupTerm(children=[expr1, expr2])

    config = ExecutionConfig(max_dice=5)
    ctx = _EvalContext(rng=SeededRNG(42), config=config)

    # This SHOULD raise MAX_DICE_EXCEEDED because 6 > 5, but GroupTerm's
    # children are evaluated by GroupTerm.evaluate() directly, bypassing
    # the dice count tracking in evaluate_tree.
    raised = False
    try:
        evaluate_tree(group, ctx)
    except DiceExecutionError:
        raised = True

    assert raised, (
        f"Expected MAX_DICE_EXCEEDED error for 6 dice with max_dice=5, "
        f"but evaluation succeeded. ctx.total_dice_rolled={ctx.total_dice_rolled}. "
        f"GroupTerm children bypass dice count tracking in evaluate_tree."
    )


def test_group_term_children_dice_count_is_zero_in_context():
    """Demonstrate that dice rolled inside GroupTerm are invisible to the context.

    Even after evaluation, ctx.total_dice_rolled should reflect all dice
    rolled. When GroupTerm children bypass evaluate_tree, the count stays at 0.
    """
    expr1 = [DiceTerm(count=2, faces=6)]
    expr2 = [DiceTerm(count=3, faces=6)]
    group = GroupTerm(children=[expr1, expr2])

    ctx = _EvalContext(rng=SeededRNG(42), config=ExecutionConfig())
    evaluate_tree(group, ctx)

    # 5 dice were actually rolled, but the context doesn't know about them
    assert ctx.total_dice_rolled == 5, (
        f"Expected ctx.total_dice_rolled=5 after rolling 2d6 and 3d6 inside "
        f"GroupTerm, but got {ctx.total_dice_rolled}. GroupTerm children "
        f"bypass dice count tracking in evaluate_tree."
    )


def test_group_term_children_max_explosions_not_propagated():
    """max_explosions from config should be propagated to DiceTerms in GroupTerm.

    evaluate_tree sets root.max_explosions = ctx.config.max_explosions for
    DiceTerms it visits, but it never visits DiceTerms inside GroupTerm
    children. Those DiceTerms retain their default max_explosions value.
    """
    child_die = DiceTerm(count=1, faces=6)
    group = GroupTerm(children=[[child_die]])

    custom_max = 42
    config = ExecutionConfig(max_explosions=custom_max)
    ctx = _EvalContext(rng=SeededRNG(0), config=config)
    evaluate_tree(group, ctx)

    assert child_die.max_explosions == custom_max, (
        f"Expected child DiceTerm.max_explosions={custom_max} (from config), "
        f"but got {child_die.max_explosions}. evaluate_tree never visits "
        f"DiceTerms inside GroupTerm children, so max_explosions is not propagated."
    )


def test_group_term_children_depth_not_tracked():
    """Depth limits should apply to GroupTerm children.

    evaluate_tree increments ctx.current_depth for each level of recursion,
    but since it doesn't recurse into GroupTerm's nested children, those
    children are evaluated at an unknown/untracked depth.
    """
    # Build a GroupTerm containing DiceTerms with max_depth=2.
    # RollExpression (depth 1) -> GroupTerm (depth 2) -> children should be
    # depth 3, which exceeds max_depth=2.
    inner_die = DiceTerm(count=1, faces=6)
    group = GroupTerm(children=[[inner_die]])
    root = RollExpression(
        expression="{1d6}",
        children=[group],
    )

    config = ExecutionConfig(max_depth=2)
    ctx = _EvalContext(rng=SeededRNG(0), config=config)

    # If depth tracking worked for GroupTerm children, this would raise
    # MAX_DEPTH_EXCEEDED at depth 3 (expression -> group -> child die).
    # Instead, evaluate_tree only sees depth 2 (expression -> group),
    # and GroupTerm.evaluate() handles the children outside of depth tracking.
    raised = False
    try:
        evaluate_tree(root, ctx)
    except DiceExecutionError as e:
        if e.code == "MAX_DEPTH_EXCEEDED":
            raised = True

    assert raised, (
        "Expected MAX_DEPTH_EXCEEDED for a 3-level deep expression with "
        "max_depth=2, but evaluation succeeded. GroupTerm children are "
        "evaluated outside of evaluate_tree's depth tracking."
    )
