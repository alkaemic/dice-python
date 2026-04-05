# dice-python

A Python dice rolling library with Roll20-compatible notation, typed execution trees, and pluggable evaluation.

## Quick Start

```bash
pip install dice
```

```python
from dice import roll

result = roll("2d20kh1+7")
print(result.total)       # e.g. 23
print(result.expression)  # "2d20kh1+7"
print(result.tree)        # full execution tree as a dict
```

## Supported Notation

dice-python supports Roll20-compatible dice notation:

| Notation | Description | Example |
|---|---|---|
| `NdS` | Roll N dice with S sides | `3d6` |
| `dS` | Roll 1 die (implicit count) | `d20` |
| `d%` | Percentile die (d100) | `d%` |
| `dF` | Fate/Fudge dice (-1, 0, +1) | `4dF` |
| `kh` / `kl` | Keep highest / lowest | `2d20kh1` |
| `dh` / `dl` | Drop highest / lowest | `4d6dl1` |
| `!` | Exploding dice | `2d6!` |
| `r` / `ro` | Reroll (unlimited / once) | `4d6r<2` |
| `+` `-` `*` `/` | Arithmetic operators | `1d8+5` |
| `(expr)` | Parenthetical grouping | `(2d6+3)*2` |
| `[text]` | Flavor text / labels | `1d20+5 [attack]` |
| `floor()` `ceil()` `round()` `abs()` | Math functions | `floor(3d6/2)` |

### Compare Points

Modifiers that accept a compare point use the syntax `<N`, `>N`, `=N`, `<=N`, or `>=N`:

```python
roll("4d6r<2")    # reroll any die less than 2
roll("2d6!>5")    # explode on rolls greater than 5
```

### Combined Modifiers

Modifiers can be combined freely. They execute in a fixed order regardless of notation position:

```python
roll("4d6r<2kh3")   # reroll 1s, then keep highest 3
```

## Execution Tree

Every roll produces a structured execution tree, making it easy to inspect what happened:

```python
from dice import roll, SeededRNG

result = roll("2d6+3", rng=SeededRNG(42))
print(result.tree)
# {
#   "id": "...",
#   "kind": "roll_expression",
#   "expression": "2d6+3",
#   "children": [...],
#   "total": 10
# }
```

The tree is JSON-serializable and every node carries a `kind` discriminator for type-safe processing.

## Deterministic Testing

Inject a seeded RNG for reproducible results in tests:

```python
from dice import roll, SeededRNG

rng = SeededRNG(42)
result = roll("4d6dl1", rng=rng)
# Same seed always produces the same rolls
```

## Pluggable Evaluators

The evaluation phase is optional and extensible. Register custom evaluators to add game-system-specific logic:

```python
from dice import roll, register_evaluator, Evaluator

class DnDEvaluator:
    def evaluate(self, execution_tree, template=None, context=None):
        total = execution_tree.get("total", 0)
        dc = (context or {}).get("target_dc", 10)
        return {
            "primary_total": total,
            "outcome": "success" if total >= dc else "failure",
        }

register_evaluator("dnd5e", DnDEvaluator())

result = roll("1d20+5", system="dnd5e", context={"target_dc": 15})
print(result.evaluation)  # {"primary_total": 18, "outcome": "success"}
```

## Safety Limits

Built-in limits prevent runaway expressions:

```python
from dice import roll, ExecutionConfig

config = ExecutionConfig(max_dice=100, max_depth=5, max_explosions=50)
result = roll("10d6!", config=config)
```

Default limits: 1000 dice, depth 10, 100 explosions.

## API Reference

### Core Functions

- **`roll(expression, *, rng=None, config=None, system=None, template=None, context=None)`** — Parse, execute, and optionally evaluate a dice expression. Returns `RollResult`.
- **`parse(expression)`** — Parse an expression into an AST. Returns `ParseResult`.
- **`validate(expression)`** — Check if an expression is valid without executing. Returns a list of errors.
- **`execute(ast, *, rng=None, config=None)`** — Execute a parsed AST. Returns `ExecutionResult`.
- **`evaluate(tree, system=None, template=None, context=None)`** — Run an evaluator on an execution tree.

### Types

- **`RollResult`** — Top-level result with `.total`, `.tree`, `.expression`, `.evaluation`.
- **`ParseResult`** — Parser output with `.ast`, `.expression`, `.errors`.
- **`ExecutionResult`** — Execution output with `.tree`, `.total`, `.expression`.
- **`ExecutionConfig`** — Safety limit configuration.
- **`RNG`** / **`DefaultRNG`** / **`SeededRNG`** — RNG protocol and implementations.
- **`DiceError`** / **`DiceParseError`** / **`DiceExecutionError`** — Structured error types.

### Term Types

`RollTerm`, `RollExpression`, `DiceTerm`, `FateDiceTerm`, `NumericTerm`, `OperatorTerm`, `ParentheticalTerm`, `GroupTerm`, `FunctionTerm`, `DieResult`

## Requirements

- Python 3.11+
- pyparsing >= 3.1.0
