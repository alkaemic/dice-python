from __future__ import annotations

from typing import Any

from dice.rng import RNG, roll_die
from dice.terms.base import RollTerm
from dice.terms.die_result import DieResult


class DiceTerm(RollTerm):
    """A term representing one or more dice of the same type to be rolled."""

    kind: str = "dice_term"

    def __init__(
        self,
        *,
        count: int,
        faces: int,
        modifier_strings: list[str] | None = None,
        id: str | None = None,
    ) -> None:
        super().__init__(id=id)
        self.count = count
        self.faces = faces
        self.modifier_strings: list[str] = modifier_strings or []
        self.results: list[DieResult] = []

    @property
    def notation(self) -> str:
        base = f"{self.count}d{self.faces}"
        return base + "".join(self.modifier_strings)

    @property
    def total(self) -> int:
        return sum(r.value for r in self.results if r.kept)

    def evaluate(self, rng: RNG) -> DiceTerm:
        if self._evaluated:
            return self
        self.results = [
            DieResult(value=roll_die(self.faces, rng))
            for _ in range(self.count)
        ]
        if self.modifier_strings:
            from dice.modifiers.parser import parse_modifier_string
            from dice.modifiers.registry import apply_modifiers

            specs = parse_modifier_string("".join(self.modifier_strings))
            self.results = apply_modifiers(self.results, specs, rng, self.faces)
        self._evaluated = True
        return self

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "kind": self.kind,
            "notation": self.notation,
            "dice": [r.to_dict() for r in self.results],
            "total": self.total,
        }
