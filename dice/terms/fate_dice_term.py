from __future__ import annotations

from typing import Any

from dice.rng import RNG, roll_die
from dice.terms.dice_term import DiceTerm
from dice.terms.die_result import DieResult


class FateDiceTerm(DiceTerm):
    """A dice term for Fate/Fudge dice producing values in {-1, 0, 1}."""

    def __init__(
        self,
        *,
        count: int,
        modifier_strings: list[str] | None = None,
        id: str | None = None,
    ) -> None:
        # faces is fixed at 3 internally for the roll_die call
        super().__init__(count=count, faces=3, modifier_strings=modifier_strings, id=id)

    @property
    def notation(self) -> str:
        base = f"{self.count}dF"
        return base + "".join(self.modifier_strings)

    def evaluate(self, rng: RNG) -> FateDiceTerm:
        if self._evaluated:
            return self
        self.results = [
            DieResult(value=roll_die(3, rng) - 2)
            for _ in range(self.count)
        ]
        if self.modifier_strings:
            from dice.modifiers.parser import parse_modifier_string
            from dice.modifiers.registry import apply_modifiers

            specs = parse_modifier_string("".join(self.modifier_strings))
            self.results = apply_modifiers(
                self.results, specs, rng, 3, self.max_explosions
            )
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
