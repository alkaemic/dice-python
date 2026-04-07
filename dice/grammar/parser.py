from __future__ import annotations

from pyparsing import ParseBaseException

from dice.constants import MAX_EXPRESSION_LENGTH, SYNTAX_VERSION
from dice.errors import DiceParseError
from dice.grammar.parse_result import ParseResult
from dice.terms import RollExpression


def parse(expression: str) -> ParseResult:
    """Parse a dice expression string into a typed AST of RollTerm objects."""
    from dice.grammar.notation import parse_notation

    if not expression or not expression.strip():
        error = DiceParseError(
            code="EMPTY_EXPRESSION",
            message="Expression is empty",
            position=0,
            expression=expression,
        )
        dummy = RollExpression(expression=expression, children=[], label=None)
        return ParseResult(
            ast=dummy,
            expression=expression,
            syntax_version=SYNTAX_VERSION,
            errors=[error],
        )

    text = expression.strip()

    if len(text) > MAX_EXPRESSION_LENGTH:
        error = DiceParseError(
            code="EXPRESSION_TOO_LONG",
            message=f"Expression length ({len(text)}) exceeds maximum ({MAX_EXPRESSION_LENGTH})",
            expression=expression,
        )
        dummy = RollExpression(expression=expression, children=[], label=None)
        return ParseResult(
            ast=dummy,
            expression=expression,
            syntax_version=SYNTAX_VERSION,
            errors=[error],
        )

    try:
        terms, flavor = parse_notation(text)
    except ParseBaseException as exc:
        error = DiceParseError(
            code="PARSE_ERROR",
            message=str(exc),
            expression=expression,
        )
        dummy = RollExpression(expression=expression, children=[], label=None)
        return ParseResult(
            ast=dummy,
            expression=expression,
            syntax_version=SYNTAX_VERSION,
            errors=[error],
        )
    except RecursionError:
        error = DiceParseError(
            code="EXPRESSION_TOO_COMPLEX",
            message="Expression is too deeply nested to parse",
            expression=expression,
        )
        dummy = RollExpression(expression=expression, children=[], label=None)
        return ParseResult(
            ast=dummy,
            expression=expression,
            syntax_version=SYNTAX_VERSION,
            errors=[error],
        )

    ast = RollExpression(expression=text, children=terms, label=flavor)
    return ParseResult(
        ast=ast,
        expression=expression,
        syntax_version=SYNTAX_VERSION,
    )


def validate(expression: str) -> list[DiceParseError]:
    """Validate an expression without executing. Returns errors (empty = valid)."""
    result = parse(expression)
    return result.errors
