"""Tests for GroupingTerm — the synthetic precedence-grouping node.

GroupingTerm is created by the parser to preserve operator precedence
(e.g. the ``2*3`` in ``1d6+2*3``). Unlike ParentheticalTerm, it has
no ``expression`` field and serializes with ``kind: "grouping_term"``.
"""

from dice import roll
from dice.grammar import parse
from dice.rng import SeededRNG
from dice.terms.grouping_term import GroupingTerm
from dice.terms.numeric_term import NumericTerm
from dice.terms.operator_term import OperatorTerm

# ---- Unit tests ----


def test_grouping_term_kind():
    term = GroupingTerm(children=[])
    assert term.kind == "grouping_term"


def test_grouping_term_evaluate():
    children = [
        NumericTerm(value=3),
        OperatorTerm(operator="*"),
        NumericTerm(value=4),
    ]
    term = GroupingTerm(children=children)
    term.evaluate(SeededRNG(0))
    assert term.total == 12


def test_grouping_term_to_dict_has_no_expression():
    """GroupingTerm serialization must not include an expression field."""
    children = [NumericTerm(value=2)]
    term = GroupingTerm(children=children)
    term.evaluate(SeededRNG(0))
    d = term.to_dict()
    assert d["kind"] == "grouping_term"
    assert "expression" not in d


def test_grouping_term_to_dict_structure():
    children = [
        NumericTerm(value=3),
        OperatorTerm(operator="*"),
        NumericTerm(value=4),
    ]
    term = GroupingTerm(children=children)
    term.evaluate(SeededRNG(0))
    d = term.to_dict()
    assert d["kind"] == "grouping_term"
    assert d["total"] == 12
    assert len(d["children"]) == 3


def test_grouping_term_double_evaluate_is_safe():
    children = [NumericTerm(value=5)]
    term = GroupingTerm(children=children)
    term.evaluate(SeededRNG(0))
    term.evaluate(SeededRNG(99))
    assert term.total == 5


# ---- Parser integration: GroupingTerm vs ParentheticalTerm ----


def test_implicit_grouping_produces_grouping_term():
    """1d6+2*3 — the 2*3 is an implicit precedence group."""
    r = parse("1d6+2*3")
    assert r.ast.children[2].kind == "grouping_term"


def test_explicit_parens_produce_parenthetical_term():
    """1d6+(2*3) — the (2*3) is user-written parentheses."""
    r = parse("1d6+(2*3)")
    assert r.ast.children[2].kind == "parenthetical_term"


def test_mixed_grouping_and_parenthetical():
    """(1d6+3)*2 — outer is GroupingTerm, inner (1d6+3) is ParentheticalTerm."""
    r = parse("(1d6+3)*2")
    mul_group = r.ast.children[0]
    assert mul_group.kind == "grouping_term"
    assert mul_group.children[0].kind == "parenthetical_term"


# ---- End-to-end tree output ----


def test_tree_distinguishes_grouping_from_parenthetical():
    """The execution tree uses distinct kind values for implicit grouping
    vs explicit parentheses, so consumers can tell them apart."""
    result = roll("(1d6+3)*2", rng=SeededRNG(42))
    tree = result.tree

    mul_group = tree["children"][0]
    assert mul_group["kind"] == "grouping_term"
    assert "expression" not in mul_group

    explicit_paren = mul_group["children"][0]
    assert explicit_paren["kind"] == "parenthetical_term"
    assert "expression" in explicit_paren


def test_pure_multiplication_produces_grouping_term():
    """1d6*2 — a single mul/div expression wraps in GroupingTerm."""
    result = roll("1d6*2", rng=SeededRNG(42))
    tree = result.tree
    assert tree["children"][0]["kind"] == "grouping_term"


def test_addition_only_has_no_grouping():
    """1d6+2 — no multiplication, so no GroupingTerm in the tree."""
    result = roll("1d6+2", rng=SeededRNG(42))
    tree = result.tree
    kinds = [c["kind"] for c in tree["children"]]
    assert "grouping_term" not in kinds
