# Dice Notation Reference

dice-python uses Roll20-compatible dice notation. This document is the complete reference for all supported syntax.

## Basic Dice

The fundamental unit is `NdS` — roll N dice with S sides.

| Expression | Meaning |
|---|---|
| `3d6` | Roll three six-sided dice |
| `1d20` | Roll one twenty-sided die |
| `d12` | Roll one twelve-sided die (implicit count of 1) |
| `10d10` | Roll ten ten-sided dice |

The count is optional and defaults to 1. The sides can be any positive integer.

### Special Dice

| Expression | Meaning |
|---|---|
| `d%` | Percentile die, equivalent to `1d100` |
| `dF` or `dFate` | Fate/Fudge die, produces -1, 0, or +1 |
| `4dF` | Roll four Fate dice |

Fate dice use face values `{-1, 0, 1}`. Modifiers (reroll, explode, etc.) produce correct fate values automatically.

## Arithmetic

Dice expressions support standard arithmetic with correct operator precedence.

| Operator | Precedence | Example | Meaning |
|---|---|---|---|
| `*` | Higher | `2d6*2` | Multiply result by 2 |
| `/` | Higher | `3d6/2` | Divide result by 2 |
| `+` | Lower | `1d20+5` | Add 5 to the roll |
| `-` | Lower | `2d8-1` | Subtract 1 from the roll |

Multiplication and division bind tighter than addition and subtraction, so `1d6+2*3` is parsed as `1d6+(2*3)`, not `(1d6+2)*3`.

### Numeric Literals

Both integers and floating-point numbers are supported as operands:

```
1d20+5       # integer modifier
2d6+1.5      # float modifier
```

## Parenthetical Expressions

Use parentheses to override precedence or group sub-expressions:

```
(2d6+3)*2     # roll 2d6+3, then double the result
(1d4+1)*(1d6) # multiply two independent rolls
```

Parentheses can be nested arbitrarily, up to the maximum expression depth (default 10).

## Math Functions

Four math functions are available, each wrapping a sub-expression:

| Function | Behavior | Example |
|---|---|---|
| `floor(expr)` | Round down | `floor(3d6/2)` |
| `ceil(expr)` | Round up | `ceil(3d6/2)` |
| `round(expr)` | Round to nearest | `round(3d6/2)` |
| `abs(expr)` | Absolute value | `abs(1d6-4)` |

Function names are case-insensitive (`FLOOR`, `Floor`, and `floor` all work).

## Flavor Text

Append a label in square brackets to annotate a roll. The label is preserved in the execution tree but does not affect the result:

```
1d20+5 [attack]
2d6+3 [fire damage]
```

Flavor text must appear at the end of the expression.

## Modifiers

Modifiers alter how dice are rolled or which dice count toward the total. They are appended directly after the dice sides, before any arithmetic.

### Compare Points

Several modifiers accept an optional **compare point** that controls which die values the modifier targets. The syntax is an operator followed by a number:

| Compare Point | Meaning |
|---|---|
| `=N` | Equal to N |
| `>N` | Greater than N |
| `<N` | Less than N |
| `>=N` | Greater than or equal to N |
| `<=N` | Less than or equal to N |
| _(omitted)_ | Defaults to the maximum face value |

### Modifier Execution Order

Modifiers are always applied in a fixed order, regardless of the order they appear in the notation. This means `4d6r<2kh3` and `4d6kh3r<2` produce identical results.

The execution order is:

1. Clamp (`min`, `max`)
2. Explode (`!`), Compound (`!!`), Penetrate (`!p`)
3. Reroll (`r`, `ro`)
4. Keep (`kh`, `kl`)
5. Drop (`dh`, `dl`)
6. Target / Success (`>`, `<`, `=`)
7. Failure (`f`)
8. Critical marking (`cs`, `cf`)
9. Sort (`s`, `sa`, `sd`)

Up to four modifiers can be combined on a single dice expression.

### Keep (Tier 1)

Keep the highest or lowest N dice. All other dice are excluded from the total.

| Notation | Meaning | Default N |
|---|---|---|
| `khN` | Keep highest N | 1 |
| `klN` | Keep lowest N | 1 |
| `kN` | Alias for `khN` | 1 |

```
2d20kh1      # roll 2d20, keep the highest (advantage)
2d20kl1      # roll 2d20, keep the lowest (disadvantage)
4d6kh3       # roll 4d6, keep the highest 3 (ability score generation)
```

Dice excluded by keep have their `kept` flag set to `false` in the execution tree.

### Drop (Tier 1)

Drop the highest or lowest N dice. The inverse of keep.

| Notation | Meaning | Default N |
|---|---|---|
| `dhN` | Drop highest N | 1 |
| `dlN` | Drop lowest N | 1 |

```
4d6dl1       # roll 4d6, drop the lowest (same as 4d6kh3)
2d20dh1      # roll 2d20, drop the highest (same as 2d20kl1)
```

### Explode (Tier 1)

When a die meets the compare point, roll an additional die and add it to the pool. If the new die also meets the condition, it explodes again, and so on.

| Notation | Meaning |
|---|---|
| `!` | Explode on maximum value |
| `!>N` | Explode when greater than N |
| `!=N` | Explode when equal to N |
| `!<N` | Explode when less than N |

```
2d6!         # explode on 6
1d20!>18     # explode on 19 or 20
8d6!=6       # explode on 6 (same as 8d6!)
```

New dice created by explosions have the `exploded` flag set to `true` in the execution tree. Explosions are capped at 100 by default to prevent infinite loops (configurable via `ExecutionConfig`).

### Reroll (Tier 1)

Replace dice that meet the compare point with new rolls.

| Notation | Meaning |
|---|---|
| `r` | Reroll matching dice (repeat until none match) |
| `ro` | Reroll matching dice once (do not re-check) |

```
4d6r<2       # reroll any die less than 2, keep rerolling if needed
4d6ro<2      # reroll any die less than 2, but only once per die
2d6r=1       # reroll 1s until no 1s remain
```

Rerolled dice remain in the execution tree with `rerolled: true` and `kept: false`. The replacement die takes their place. Unlimited rerolls (`r`) are capped at 100 iterations as a safety measure.

### Tier 2+ Modifiers (Planned)

The following modifiers are parsed by the grammar and registered in the modifier pipeline, but are not yet implemented. Using them will raise an error:

| Notation | Name | Description |
|---|---|---|
| `!!` | Compound | Like explode, but adds to a single die instead of creating new dice |
| `!p` | Penetrate | Like explode, but each new die subtracts 1 from its value |
| `>N`, `<N`, `=N` | Target/Success | Count dice meeting the condition instead of summing values |
| `f` | Failure | Count failures (subtract from success count) |
| `cs`, `cf` | Critical | Mark dice as critical successes or failures |
| `s`, `sa`, `sd` | Sort | Sort the dice pool ascending or descending |
| `min`, `max` | Clamp | Clamp individual die values to a minimum or maximum |

## Complete Examples

| Expression | Description |
|---|---|
| `1d20` | Simple d20 roll |
| `2d20kh1+7` | Advantage + modifier (D&D 5e attack) |
| `4d6dl1` | Ability score generation (drop lowest) |
| `2d6!` | Fireball-style with exploding dice |
| `8d6` | High-level spell damage |
| `d%` | Percentile roll |
| `4dF+3` | Fate roll with skill bonus |
| `(2d6+3)*2` | Critical hit (double the damage) |
| `1d8+2d6+5` | Sneak attack damage |
| `4d6r<2kh3` | Generous ability score generation (reroll 1s, keep best 3) |
| `floor(3d6/2)` | Halved damage, rounded down |
| `1d20+5 [attack]` | Labeled attack roll |

## Safety Limits

To prevent resource exhaustion from adversarial or accidental input, the following limits are enforced:

| Limit | Default | Description |
|---|---|---|
| Max dice count | 1,000 | Maximum number of dice in a single expression |
| Max explosions | 100 | Maximum explosion chain length per die |
| Max expression depth | 10 | Maximum nesting depth for parentheses/functions |
| Max expression length | 500 | Maximum character length of the input expression |

All limits are configurable via `ExecutionConfig`:

```python
from dice import roll, ExecutionConfig

config = ExecutionConfig(max_dice=100, max_depth=5, max_explosions=50)
result = roll("10d6!", config=config)
```
