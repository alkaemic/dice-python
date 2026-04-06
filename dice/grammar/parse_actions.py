from __future__ import annotations

from typing import Any

from dice.terms import (
    DiceTerm,
    FateDiceTerm,
    FunctionTerm,
    NumericTerm,
    OperatorTerm,
    ParentheticalTerm,
    RollTerm,
)


def make_integer(string: str, location: int, tokens: Any) -> NumericTerm:
    return NumericTerm(value=int(tokens[0]))


def make_float(string: str, location: int, tokens: Any) -> NumericTerm:
    return NumericTerm(value=float(tokens[0]))


def make_dice_term(string: str, location: int, tokens: Any) -> DiceTerm | FateDiceTerm:
    tok = tokens[0]
    count = int(tok.get("count", 1))
    sides_raw = tok["sides"]

    # Collect modifier strings
    modifier_strings: list[str] = list(tok.get("modifiers", []))

    if isinstance(sides_raw, str) and sides_raw.upper() in ("F", "FATE"):
        return FateDiceTerm(count=count, modifier_strings=modifier_strings)

    if isinstance(sides_raw, str) and sides_raw == "%":
        faces = 100
    else:
        faces = int(sides_raw)

    return DiceTerm(count=count, faces=faces, modifier_strings=modifier_strings)


def _extract_parenthetical_text(string: str, location: int) -> str:
    """Extract the full parenthesized text from the original input string."""
    depth = 0
    for i in range(location, len(string)):
        if string[i] == "(":
            depth += 1
        elif string[i] == ")":
            depth -= 1
            if depth == 0:
                return string[location : i + 1]
    return string[location:]


def make_parenthetical(string: str, location: int, tokens: Any) -> ParentheticalTerm:
    inner_items = tokens[0]
    children: list[RollTerm] = []
    for item in inner_items:
        if isinstance(item, RollTerm):
            children.append(item)
        elif isinstance(item, list):
            children.extend(item)
    expr_text = _extract_parenthetical_text(string, location)
    return ParentheticalTerm(expression=expr_text, children=children)


def make_function(string: str, location: int, tokens: Any) -> FunctionTerm:
    tok = tokens[0]
    fn_name = tok[0].lower()
    inner_terms: list[RollTerm] = list(tok[1:])
    return FunctionTerm(function=fn_name, children=inner_terms)


def _flatten_infix(tokens: Any) -> list[RollTerm]:
    """Flatten pyparsing infixNotation result into [term, op, term, ...] list."""
    items = tokens[0]
    result: list[RollTerm] = []
    for item in items:
        if isinstance(item, str):
            result.append(OperatorTerm(operator=item))
        elif isinstance(item, RollTerm):
            result.append(item)
    return result


def make_add_sub(string: str, location: int, tokens: Any) -> Any:
    return _flatten_infix(tokens)


def make_mul_div(string: str, location: int, tokens: Any) -> Any:
    return _flatten_infix(tokens)
