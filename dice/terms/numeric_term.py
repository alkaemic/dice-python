from __future__ import annotations

from typing import Any

from dice.rng import RNG
from dice.terms.base import RollTerm


class NumericTerm(RollTerm):
    """A term representing a literal numeric value."""

    kind: str = "numeric_term"

    def __init__(self, *, value: int | float, id: str | None = None) -> None:
        super().__init__(id=id)
        self.value = value

    @property
    def total(self) -> int | float:
        return self.value

    def evaluate(self, rng: RNG) -> NumericTerm:
        if self._evaluated:
            return self
        self._evaluated = True
        return self

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "kind": self.kind,
            "value": self.value,
        }
