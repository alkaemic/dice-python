from dice import roll
from dice.rng import SeededRNG


def test_execute_parenthetical():
    result = roll("(2d6+3)*2", rng=SeededRNG(42))
    tree = result.tree
    assert tree["kind"] == "roll_expression"
    # The mul/div level wraps into a GroupingTerm for precedence
    mul_group = tree["children"][0]
    assert mul_group["kind"] == "grouping_term"
    # Inside: [(2d6+3), *, 2]
    assert mul_group["children"][0]["kind"] == "parenthetical_term"
    assert mul_group["children"][1]["kind"] == "operator_term"
    assert mul_group["children"][2]["kind"] == "numeric_term"


def test_execute_complex_expression():
    result = roll("4d6dl1+2d4+5", rng=SeededRNG(42))
    tree = result.tree
    assert tree["kind"] == "roll_expression"
    # First child is dice with drop modifier
    assert tree["children"][0]["kind"] == "dice_term"
    assert tree["total"] == result.total


def test_execute_nested_parenthetical():
    result = roll("1d20+(2d4+1)", rng=SeededRNG(42))
    tree = result.tree
    assert tree["children"][2]["kind"] == "parenthetical_term"
    inner = tree["children"][2]
    assert len(inner["children"]) == 3


def test_execute_function():
    result = roll("abs(1d6-4)", rng=SeededRNG(42))
    tree = result.tree
    fn = tree["children"][0]
    assert fn["kind"] == "function_term"
    assert fn["function"] == "abs"
    assert result.total >= 0
