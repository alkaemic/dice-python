from __future__ import annotations

from dice.errors import DiceExecutionError
from dice.terms.base import RollTerm
from dice.terms.operator_term import OperatorTerm


def compute_infix_total(children: list[RollTerm]) -> int | float:
    """Compute total from an infix sequence [term, op, term, op, term, ...]."""
    if not children:
        return 0
    result = children[0].total
    i = 1
    while i < len(children) - 1:
        op = children[i]
        if not isinstance(op, OperatorTerm):
            raise TypeError(
                f"Expected OperatorTerm at index {i}, " f"got {type(op).__name__}"
            )
        right = children[i + 1]
        if op.operator == "+":
            result = result + right.total
        elif op.operator == "-":
            result = result - right.total
        elif op.operator == "*":
            result = result * right.total
        elif op.operator == "/":
            if right.total == 0:
                raise DiceExecutionError(
                    code="DIVISION_BY_ZERO",
                    message="Division by zero in dice expression",
                )
            result = result / right.total
        i += 2
    return result
