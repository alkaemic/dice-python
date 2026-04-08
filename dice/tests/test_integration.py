"""End-to-end integration tests for the full dice pipeline."""

import json

from dice import RollResult, SeededRNG, roll


def _assert_valid_tree(tree: dict) -> None:
    """Verify a tree node has id, kind, and round-trips through JSON."""
    assert "id" in tree
    assert "kind" in tree
    serialized = json.dumps(tree)
    assert json.loads(serialized) == tree


def test_simple_1d20():
    result = roll("1d20", rng=SeededRNG(42))
    assert isinstance(result, RollResult)
    assert 1 <= result.total <= 20
    _assert_valid_tree(result.tree)


def test_advantage_plus_modifier():
    result = roll("2d20kh1+7", rng=SeededRNG(42))
    tree = result.tree
    _assert_valid_tree(tree)
    dice_node = tree["children"][0]
    assert dice_node["kind"] == "dice_term"
    assert len(dice_node["dice"]) == 2
    kept = [d for d in dice_node["dice"] if d["kept"]]
    assert len(kept) == 1
    assert result.total == kept[0]["value"] + 7


def test_ability_score_generation():
    result = roll("4d6dl1", rng=SeededRNG(42))
    tree = result.tree
    _assert_valid_tree(tree)
    dice_node = tree["children"][0]
    assert len(dice_node["dice"]) == 4
    kept = [d for d in dice_node["dice"] if d["kept"]]
    assert len(kept) == 3
    assert result.total == sum(d["value"] for d in kept)


def test_exploding_dice():
    result = roll("2d6!", rng=SeededRNG(42))
    tree = result.tree
    _assert_valid_tree(tree)
    dice_node = tree["children"][0]
    assert len(dice_node["dice"]) >= 2


def test_flavor_text():
    result = roll("1d20+5 [attack]", rng=SeededRNG(42))
    _assert_valid_tree(result.tree)
    assert result.tree.get("label") == "attack"


def test_fate_dice():
    result = roll("4dF+3", rng=SeededRNG(42))
    _assert_valid_tree(result.tree)
    dice_node = result.tree["children"][0]
    for d in dice_node["dice"]:
        assert d["value"] in {-1, 0, 1}


def test_percentile():
    result = roll("d%", rng=SeededRNG(42))
    _assert_valid_tree(result.tree)
    assert 1 <= result.total <= 100


def test_parenthetical():
    result = roll("(2d6+3)*2", rng=SeededRNG(42))
    _assert_valid_tree(result.tree)
    mul_group = result.tree["children"][0]
    assert mul_group["kind"] == "grouping_term"


def test_multi_term():
    result = roll("1d8+2d6+5", rng=SeededRNG(42))
    _assert_valid_tree(result.tree)
    children = result.tree["children"]
    assert children[0]["kind"] == "dice_term"
    assert children[2]["kind"] == "dice_term"
    assert children[4]["kind"] == "numeric_term"
    assert children[4]["value"] == 5


def test_reroll_plus_keep_ordering():
    r1 = roll("4d6r<2kh3", rng=SeededRNG(42))
    r2 = roll("4d6kh3r<2", rng=SeededRNG(42))
    _assert_valid_tree(r1.tree)
    _assert_valid_tree(r2.tree)
    # Same seed + fixed modifier order = same totals
    assert r1.total == r2.total


def test_all_results_are_roll_result():
    expressions = [
        "1d20",
        "2d20kh1+7",
        "4d6dl1",
        "2d6!",
        "1d20+5 [attack]",
        "4dF+3",
        "d%",
        "(2d6+3)*2",
        "1d8+2d6+5",
        "4d6r<2kh3",
    ]
    for expr in expressions:
        result = roll(expr, rng=SeededRNG(42))
        assert isinstance(result, RollResult), f"Failed for {expr}"
        assert isinstance(result.total, (int, float)), f"Failed for {expr}"
        _assert_valid_tree(result.tree)
