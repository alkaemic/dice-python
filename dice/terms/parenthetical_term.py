from __future__ import annotations

from typing import Any

from dice.rng import RNG
from dice.terms.base import RollTerm
from dice.terms.eval_helpers import compute_infix_total


class ParentheticalTerm(RollTerm):
    """A term representing a parenthesized sub-expression."""

    kind: str = "parenthetical_term"

    def __init__(
        self,
        *,
        expression: str,
        children: list[RollTerm],
        id: str | None = None,
    ) -> None:
        super().__init__(id=id)
        self.expression = expression
        self.children = children
        self._total: int | float = 0

    @property
    def total(self) -> int | float:
        return self._total

    def evaluate(self, rng: RNG) -> ParentheticalTerm:
        if self._evaluated:
            return self
        for child in self.children:
            child.evaluate(rng)
        self._total = compute_infix_total(self.children)
        self._evaluated = True
        return self

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "kind": self.kind,
            "expression": self.expression,
            "children": [c.to_dict() for c in self.children],
            "total": self.total,
        }
