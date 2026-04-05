# Execution Tree

Every roll in dice-python produces a structured **execution tree** — a JSON-serializable dictionary that captures exactly what happened during the roll. This is the primary output format, designed for inspection, logging, replay, and game-system evaluation.

## RollResult

The `roll()` function returns a `RollResult`, which wraps the execution tree and an optional evaluation dict:

```python
from dice import roll

# Without evaluation — result.evaluation is None
result = roll("2d6+3")
print(result.total)       # numeric total from the execution tree
print(result.tree)        # the execution tree dict
print(result.evaluation)  # None

# With evaluation — result.evaluation is a dict
result = roll("1d20+5", system="dnd5e", context={"dc": 15})
print(result.evaluation)  # {"primary_total": 22, "outcome": "success", ...}
```

| Field | Type | Description |
|---|---|---|
| `result.tree` | dict | The execution tree (documented below) |
| `result.total` | number | Shorthand for `result.tree["total"]` |
| `result.expression` | string | The original input expression |
| `result.evaluation` | dict or None | Output from the evaluator, if one was invoked |

The evaluation dict is produced by a pluggable evaluator and is **not** part of the execution tree itself — it sits alongside it on the `RollResult`. See [Evaluators](evaluators.md) for details on writing and registering custom evaluators.

## Structure

The tree is a nested hierarchy of nodes. Every node has:

- **`id`** — a unique UUID for the node
- **`kind`** — a type discriminator string for safe pattern matching

### Root Node: `roll_expression`

The root of every tree is a `roll_expression`:

```json
{
  "id": "a1b2c3...",
  "kind": "roll_expression",
  "expression": "2d6+3",
  "children": [...],
  "total": 10
}
```

| Field | Type | Description |
|---|---|---|
| `id` | string | Unique identifier |
| `kind` | string | Always `"roll_expression"` |
| `expression` | string | The original input expression |
| `label` | string or null | Flavor text, if provided (e.g. `"attack"`) |
| `children` | array | The term nodes that make up the expression |
| `total` | number | The computed total |

### Dice Node: `dice_term`

Represents a dice roll like `2d6kh1`:

```json
{
  "id": "d4e5f6...",
  "kind": "dice_term",
  "notation": "2d6kh1",
  "dice": [
    {"value": 5, "kept": true},
    {"value": 2, "kept": false}
  ],
  "total": 5
}
```

| Field | Type | Description |
|---|---|---|
| `kind` | string | `"dice_term"` |
| `notation` | string | The canonical notation for this dice group |
| `dice` | array | Individual die results (see below) |
| `total` | number | Sum of kept dice |

### Die Result Objects

Each element in the `dice` array represents a single die:

```json
{
  "value": 6,
  "kept": true,
  "exploded": true,
  "rerolled": false
}
```

| Field | Type | Description |
|---|---|---|
| `value` | number | The face value rolled |
| `kept` | boolean | Whether this die counts toward the total |
| `exploded` | boolean | Whether this die was created by an explosion (only present if `true`) |
| `rerolled` | boolean | Whether this die was replaced by a reroll (only present if `true`) |
| `critical` | string or null | Critical status, if set (only present if not null) |

Fields with default/falsy values are omitted from serialization to keep the output compact.

### Numeric Node: `numeric_term`

A literal number in the expression:

```json
{
  "id": "...",
  "kind": "numeric_term",
  "value": 5,
  "total": 5
}
```

### Operator Node: `operator_term`

An arithmetic operator connecting terms:

```json
{
  "id": "...",
  "kind": "operator_term",
  "operator": "+"
}
```

Operators appear between operand nodes in the `children` array, forming an infix sequence.

### Parenthetical Node: `parenthetical_term`

A parenthesized sub-expression:

```json
{
  "id": "...",
  "kind": "parenthetical_term",
  "children": [...],
  "total": 9
}
```

### Function Node: `function_term`

A math function wrapping a sub-expression:

```json
{
  "id": "...",
  "kind": "function_term",
  "function": "floor",
  "children": [...],
  "total": 4
}
```

### Group Node: `group_term`

Multiple sub-expressions grouped together (used by group-level modifiers):

```json
{
  "id": "...",
  "kind": "group_term",
  "children": [...],
  "total": 12
}
```

## Reading the Tree

The `children` array of any container node uses **infix ordering**: operands and operators alternate. For example, `1d8+2d6+5` produces:

```
children: [
  {kind: "dice_term", notation: "1d8", ...},
  {kind: "operator_term", operator: "+"},
  {kind: "dice_term", notation: "2d6", ...},
  {kind: "operator_term", operator: "+"},
  {kind: "numeric_term", value: 5, ...}
]
```

The `total` at each level is computed by evaluating the infix sequence. Operator precedence is already resolved by the tree structure — multiplication nodes are nested inside addition nodes, not the other way around.

## Accessing the Tree

```python
from dice import roll, SeededRNG

result = roll("4d6dl1", rng=SeededRNG(42))

# Top-level access
print(result.total)       # the final number
print(result.expression)  # "4d6dl1"
print(result.tree)        # the full dict

# Inspecting individual dice
dice_node = result.tree["children"][0]
for die in dice_node["dice"]:
    status = "kept" if die["kept"] else "dropped"
    print(f"  rolled {die['value']} ({status})")
```

## JSON Serialization

The tree is a plain dict of primitives — it serializes directly with `json.dumps`:

```python
import json
from dice import roll

result = roll("2d20kh1+5")
payload = json.dumps(result.tree, indent=2)
```

This makes it straightforward to store rolls in a database, send them over an API, or log them for audit purposes.
