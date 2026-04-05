from __future__ import annotations

import math
from typing import Any

from dice.rng import RNG
from dice.terms.base import RollTerm
from dice.terms.eval_helpers import compute_infix_total

_FUNCTIONS: dict[str, Any] = {
    "floor": math.floor,
    "ceil": math.ceil,
    "round": round,
    "abs": abs,
}


class FunctionTerm(RollTerm):
    """A term applying a math function (floor, ceil, round, abs) to children."""

    kind: str = "function_term"

    def __init__(
        self,
        *,
        function: str,
        children: list[RollTerm],
        id: str | None = None,
    ) -> None:
        if function not in _FUNCTIONS:
            raise ValueError(
                f"Unsupported function: {function!r}. "
                f"Must be one of {sorted(_FUNCTIONS)}"
            )
        super().__init__(id=id)
        self.function = function
        self.children = children
        self._total: int | float = 0

    @property
    def total(self) -> int | float:
        return self._total

    def evaluate(self, rng: RNG) -> FunctionTerm:
        if self._evaluated:
            return self
        for child in self.children:
            child.evaluate(rng)
        child_total = compute_infix_total(self.children)
        self._total = _FUNCTIONS[self.function](child_total)
        self._evaluated = True
        return self

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "kind": self.kind,
            "function": self.function,
            "children": [c.to_dict() for c in self.children],
            "total": self.total,
        }
