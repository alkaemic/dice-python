from dice import roll
from dice.rng import SeededRNG


def test_total_matches_tree():
    result = roll("2d6+3", rng=SeededRNG(42))
    assert result.total == result.tree["total"]


def test_total_addition():
    result = roll("1d6+5", rng=SeededRNG(42))
    dice_total = result.tree["children"][0]["total"]
    assert result.total == dice_total + 5


def test_total_subtraction():
    result = roll("1d20-3", rng=SeededRNG(42))
    dice_total = result.tree["children"][0]["total"]
    assert result.total == dice_total - 3


def test_total_multiplication():
    result = roll("1d6*2", rng=SeededRNG(42))
    # Mul/div is now wrapped in a ParentheticalTerm for precedence
    mul_group = result.tree["children"][0]
    assert mul_group["kind"] == "parenthetical_term"
    dice_total = mul_group["children"][0]["total"]
    assert result.total == dice_total * 2


def test_total_with_modifiers():
    result = roll("4d6kh3", rng=SeededRNG(42))
    dice_node = result.tree["children"][0]
    kept_sum = sum(d["value"] for d in dice_node["dice"] if d["kept"])
    assert result.total == kept_sum


def test_total_complex():
    result = roll("2d6+1d4+5", rng=SeededRNG(42))
    assert result.total == result.tree["total"]
