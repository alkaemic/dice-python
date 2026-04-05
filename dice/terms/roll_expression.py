from __future__ import annotations

from typing import Any

from dice.rng import RNG
from dice.terms.base import RollTerm
from dice.terms.eval_helpers import compute_infix_total


class RollExpression(RollTerm):
    """Root node representing a complete dice roll expression."""

    kind: str = "roll_expression"

    def __init__(
        self,
        *,
        expression: str,
        children: list[RollTerm],
        label: str | None = None,
        id: str | None = None,
    ) -> None:
        super().__init__(id=id)
        self.expression = expression
        self.children = children
        self.label = label
        self._total: int | float = 0

    @property
    def total(self) -> int | float:
        return self._total

    def evaluate(self, rng: RNG) -> RollExpression:
        if self._evaluated:
            return self
        for child in self.children:
            child.evaluate(rng)
        self._total = compute_infix_total(self.children)
        self._evaluated = True
        return self

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "id": self.id,
            "kind": self.kind,
            "expression": self.expression,
            "children": [c.to_dict() for c in self.children],
            "total": self.total,
        }
        if self.label:
            d["label"] = self.label
        return d
