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

    assert group.total == 20, (
        f"Expected kh1 to keep the higher sub-expression (20), got {group.total}"
    )


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

    assert root.total == 17, (
        f"Expected {'{'}5, 15{'}'}kh1+2 = 17, got {root.total}"
    )


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
