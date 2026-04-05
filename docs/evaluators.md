# Evaluators

The **evaluator** is an optional post-processing phase that runs after execution. It takes the execution tree and applies game-system-specific logic — interpreting a roll as a hit or miss, computing degrees of success, applying system rules, etc.

## Pipeline

The full dice pipeline is:

```
Parse → Execute → (Evaluate)
```

Evaluation is skipped unless you pass `system`, `template`, or `context` to `roll()`.

## Default Evaluator

When no evaluator is registered for the requested system, the `DefaultEvaluator` is used. It performs a simple pass-through:

```python
from dice import roll

result = roll("1d20+5", system="unknown")
print(result.evaluation)
# {"primary_total": 18, "outcome": None}
```

The default evaluator extracts `primary_total` from the execution tree and sets `outcome` to `None`.

## Writing a Custom Evaluator

An evaluator is any object that implements the `Evaluator` protocol:

```python
from dice.evaluation import Evaluator

class MyEvaluator:
    def evaluate(
        self,
        execution_tree: dict,
        template: str | None = None,
        context: dict | None = None,
    ) -> dict:
        """Return a dict with at minimum 'primary_total' and 'outcome'."""
        ...
```

The return value must be a dict. By convention it includes `primary_total` (the numeric result) and `outcome` (a string or None), but you can add any additional fields your system needs.

## Registering an Evaluator

Register your evaluator for a system identifier:

```python
from dice import register_evaluator

class DnD5eEvaluator:
    def evaluate(self, execution_tree, template=None, context=None):
        total = execution_tree.get("total", 0)
        dc = (context or {}).get("dc", 10)
        return {
            "primary_total": total,
            "outcome": "success" if total >= dc else "failure",
            "margin": total - dc,
        }

register_evaluator("dnd5e", DnD5eEvaluator())
```

Then use it:

```python
from dice import roll

result = roll("1d20+5", system="dnd5e", context={"dc": 15})
print(result.evaluation)
# {"primary_total": 22, "outcome": "success", "margin": 7}
```

## Parameters

The `roll()` function passes three evaluation parameters:

| Parameter | Type | Purpose |
|---|---|---|
| `system` | `str` or `None` | Selects which evaluator to use (e.g. `"dnd5e"`, `"pbta"`) |
| `template` | `str` or `None` | Identifies the roll type within the system (e.g. `"attack"`, `"save"`) |
| `context` | `dict` or `None` | Arbitrary data for the evaluator (e.g. `{"dc": 15, "advantage": True}`) |

Evaluation only runs if at least one of these is provided. If `system` is `None` or unregistered, the `DefaultEvaluator` is used.

## Accessing Results

```python
result = roll("2d6+3", system="my_system")

# Execution is always available
print(result.total)        # numeric total
print(result.tree)         # full execution tree

# Evaluation is available when requested
print(result.evaluation)   # dict from the evaluator, or None
```

## Example: Powered by the Apocalypse

```python
from dice import register_evaluator, roll

class PbtAEvaluator:
    def evaluate(self, execution_tree, template=None, context=None):
        total = execution_tree.get("total", 0)
        if total >= 10:
            outcome = "strong_hit"
        elif total >= 7:
            outcome = "weak_hit"
        else:
            outcome = "miss"
        return {
            "primary_total": total,
            "outcome": outcome,
        }

register_evaluator("pbta", PbtAEvaluator())

result = roll("2d6+1", system="pbta")
print(result.evaluation["outcome"])  # "strong_hit", "weak_hit", or "miss"
```
