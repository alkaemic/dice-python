from typing import Any

from dice.evaluation import evaluate, register_evaluator


class CritCheckEvaluator:
    """Mock evaluator that checks for natural 20 on the first die."""

    def evaluate(
        self,
        execution_tree: dict[str, Any],
        template: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        total = execution_tree.get("total", 0)
        is_crit = False

        children = execution_tree.get("children", [])
        if children and children[0].get("kind") == "dice_term":
            dice = children[0].get("dice", [])
            kept_dice = [d for d in dice if d.get("kept")]
            if kept_dice and kept_dice[0]["value"] == 20:
                is_crit = True

        dc = (context or {}).get("target_dc")
        outcome = None
        if dc is not None:
            outcome = "success" if total >= dc else "failure"
        if is_crit:
            outcome = "critical_success"

        return {
            "primary_total": total,
            "outcome": outcome,
            "mechanic_critical_state": "natural_20" if is_crit else None,
            "template": template,
        }


def test_custom_evaluator_receives_all_args():
    register_evaluator("test_crit", CritCheckEvaluator())
    tree = {
        "kind": "roll_expression",
        "total": 25,
        "children": [
            {
                "kind": "dice_term",
                "dice": [{"value": 20, "kept": True}],
                "total": 20,
            },
            {"kind": "operator_term", "operator": "+"},
            {"kind": "numeric_term", "value": 5},
        ],
    }
    result = evaluate(
        tree,
        system="test_crit",
        template="attack",
        context={"target_dc": 15},
    )
    assert result["outcome"] == "critical_success"
    assert result["mechanic_critical_state"] == "natural_20"
    assert result["template"] == "attack"
    assert result["primary_total"] == 25


def test_custom_evaluator_no_crit():
    register_evaluator("test_crit2", CritCheckEvaluator())
    tree = {
        "kind": "roll_expression",
        "total": 12,
        "children": [
            {
                "kind": "dice_term",
                "dice": [{"value": 7, "kept": True}],
                "total": 7,
            },
            {"kind": "operator_term", "operator": "+"},
            {"kind": "numeric_term", "value": 5},
        ],
    }
    result = evaluate(tree, system="test_crit2", context={"target_dc": 15})
    assert result["outcome"] == "failure"
    assert result["mechanic_critical_state"] is None
