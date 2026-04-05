from __future__ import annotations

from typing import Any

from dice.rng import RNG
from dice.terms.base import RollTerm


class OperatorTerm(RollTerm):
    """A term representing an infix arithmetic operator."""

    kind: str = "operator_term"

    VALID_OPERATORS = frozenset({"+", "-", "*", "/"})

    def __init__(self, *, operator: str, id: str | None = None) -> None:
        if operator not in self.VALID_OPERATORS:
            raise ValueError(f"Invalid operator: {operator!r}")
        super().__init__(id=id)
        self.operator = operator

    @property
    def total(self) -> int | float:
        raise TypeError("OperatorTerm has no total")

    def evaluate(self, rng: RNG) -> OperatorTerm:
        if self._evaluated:
            return self
        self._evaluated = True
        return self

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "kind": self.kind,
            "operator": self.operator,
        }
