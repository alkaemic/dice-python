"""Roll20-compatible dice notation grammar using pyparsing.

Produces a typed AST of RollTerm objects.
"""

from __future__ import annotations

from pyparsing import (
    CaselessKeyword,
    CaselessLiteral,
    Combine,
    Forward,
    Group,
    Literal,
    Optional,
    Regex,
    Suppress,
    Word,
    infix_notation,
    nums,
    opAssoc,
)

from dice.grammar.parse_actions import (
    make_add_sub,
    make_dice_term,
    make_float,
    make_function,
    make_integer,
    make_mul_div,
    make_parenthetical,
)

# ---------------------------------------------------------------------------
# Primitives
# ---------------------------------------------------------------------------

_integer = Word(nums).set_parse_action(make_integer).set_name("integer")

_float_num = Regex(r"\d+\.\d+").set_parse_action(make_float).set_name("float")

_number = (_float_num | _integer).set_name("number")

# ---------------------------------------------------------------------------
# Compare points  (used inside modifiers, not standalone)
# ---------------------------------------------------------------------------

_compare_op = Regex(r">=|<=|>|<|=")
_compare_point = Combine(_compare_op + Word(nums)).set_name("compare_point")

# ---------------------------------------------------------------------------
# Modifier suffixes — captured as raw strings, parsed by modifiers.parser
# ---------------------------------------------------------------------------

_keep_mod = Combine(
    (CaselessLiteral("kh") | CaselessLiteral("kl") | CaselessLiteral("k"))
    + Optional(Word(nums))
)

_drop_mod = Combine(
    (CaselessLiteral("dh") | CaselessLiteral("dl"))
    + Optional(Word(nums))
)

_explode_mod = Combine(
    (Literal("!!") | Literal("!p") | Literal("!"))
    + Optional(_compare_point)
)

_reroll_mod = Combine(
    (CaselessLiteral("ro") | CaselessLiteral("r"))
    + Optional(_compare_point)
)

_modifier = (_keep_mod | _drop_mod | _explode_mod | _reroll_mod).set_name("modifier")

# ---------------------------------------------------------------------------
# Dice expression:  [count] 'd' sides [modifiers...]
# ---------------------------------------------------------------------------

_dice_count = Word(nums).set_results_name("count").set_name("dice_count")
_dice_sides = (
    CaselessLiteral("F")
    | CaselessLiteral("fate")
    | Literal("%")
    | Word(nums)
).set_results_name("sides").set_name("dice_sides")

_dice_expr = Group(
    Optional(_dice_count)
    + Suppress(CaselessLiteral("d"))
    + _dice_sides
    + Group(
        Optional(
            _modifier
            + Optional(
                _modifier
                + Optional(_modifier + Optional(_modifier))
            )
        )
    )
    .set_results_name("modifiers")
).set_parse_action(make_dice_term).set_name("dice_expr")

# ---------------------------------------------------------------------------
# Forward-declare expression for recursive grammar
# ---------------------------------------------------------------------------

_expression = Forward().set_name("expression")

# ---------------------------------------------------------------------------
# Parenthetical:  '(' expression ')'
# ---------------------------------------------------------------------------

_lparen = Suppress(Literal("("))
_rparen = Suppress(Literal(")"))
_parenthetical = Group(
    _lparen + _expression + _rparen
).set_parse_action(make_parenthetical).set_name("parenthetical")

# ---------------------------------------------------------------------------
# Function call:  floor(...) | ceil(...) | round(...) | abs(...)
# ---------------------------------------------------------------------------

_func_name = (
    CaselessKeyword("floor")
    | CaselessKeyword("ceil")
    | CaselessKeyword("round")
    | CaselessKeyword("abs")
)

_function_call = Group(
    _func_name + _lparen + _expression + _rparen
).set_parse_action(make_function).set_name("function_call")

# ---------------------------------------------------------------------------
# Factor (atom):  dice | function | parenthetical | number
# ---------------------------------------------------------------------------

_factor = (_dice_expr | _function_call | _parenthetical | _number).set_name("factor")

# ---------------------------------------------------------------------------
# Flavor text:  [some text]
# ---------------------------------------------------------------------------

_flavor = (
    Suppress(Literal("["))
    + Regex(r"[^\]]*")
    + Suppress(Literal("]"))
).set_results_name("flavor").set_name("flavor_text")

# ---------------------------------------------------------------------------
# Full expression with operator precedence via infixNotation
# ---------------------------------------------------------------------------

_mul_op = Literal("*") | Literal("/")
_add_op = Literal("+") | Literal("-")

_full_expression = infix_notation(
    _factor,
    [
        (_mul_op, 2, opAssoc.LEFT, make_mul_div),
        (_add_op, 2, opAssoc.LEFT, make_add_sub),
    ],
)

_expression <<= _full_expression  # type: ignore[operator]

# ---------------------------------------------------------------------------
# Top-level: expression with optional flavor text
# ---------------------------------------------------------------------------

_top_level = _full_expression + Optional(_flavor)


def parse_notation(text: str) -> tuple[list, str | None]:
    """Parse *text* and return ``(term_list, flavor_or_none)``.

    The term_list contains RollTerm objects ready to be wrapped in a
    RollExpression.  Flavor text (e.g. ``[attack]``) is returned
    separately.
    """
    result = _top_level.parse_string(text, parse_all=True)

    flavor: str | None = None
    if "flavor" in result:
        raw = result["flavor"]
        # pyparsing may return a ParseResults list; take the first element
        if hasattr(raw, "__getitem__") and not isinstance(raw, str):
            raw = raw[0]
        flavor = str(raw).strip() or None

    # Collect all RollTerm objects from the parse result
    from dice.terms.base import RollTerm

    terms: list[RollTerm] = []
    for item in result:
        if isinstance(item, RollTerm):
            terms.append(item)
        elif isinstance(item, list):
            terms.extend(item)

    return terms, flavor
