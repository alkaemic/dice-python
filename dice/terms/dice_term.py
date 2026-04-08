from __future__ import annotations

from typing import Any

from dice.constants import MAX_EXPLOSIONS
from dice.rng import RNG, roll_die
from dice.terms.base import RollTerm
from dice.terms.die_result import DieResult

FATE_FACE_VALUES: tuple[int, ...] = (-1, 0, 1)


class DiceTerm(RollTerm):
    """A term representing one or more dice of the same type to be rolled.

    For standard dice (d4, d6, d20, etc.), *faces* determines the range
    ``[1, faces]``.  For non-standard dice like fate/fudge dice, pass
    *face_values* to specify the exact set of outcomes — modifiers will
    then produce correct values automatically.
    """

    kind: str = "dice_term"

    def __init__(
        self,
        *,
        count: int,
        faces: int,
        face_values: tuple[int, ...] | None = None,
        notation_label: str | None = None,
        modifier_strings: list[str] | None = None,
        id: str | None = None,
    ) -> None:
        super().__init__(id=id)
        self.count = count
        self.faces = faces
        self.face_values: tuple[int, ...] | None = face_values
        self._notation_label: str | None = notation_label
        self.modifier_strings: list[str] = modifier_strings or []
        self.max_explosions: int = MAX_EXPLOSIONS
        self.results: list[DieResult] = []
        self._modifier_specs: list["ModifierSpec"] = []  # noqa: F821
        self._has_target: bool = False

    _TARGET_KEYS = frozenset({">", "<", "=", "f"})

    @property
    def notation(self) -> str:
        sides = self._notation_label or str(self.faces)
        base = f"{self.count}d{sides}"
        return base + "".join(self.modifier_strings)

    @property
    def total(self) -> int:
        if self._has_target:
            successes = sum(1 for r in self.results if r.matched)
            failures = sum(1 for r in self.results if r.failure)
            return successes - failures
        return sum(r.value for r in self.results if r.kept)

    def _roll_value(self, rng: RNG) -> int:
        """Produce a single die value.

        For standard dice this returns ``roll_die(faces, rng)``.  When
        *face_values* is set, it picks uniformly from that tuple instead,
        so non-standard mappings (e.g. fate ``{-1, 0, 1}``) work correctly.
        """
        if self.face_values is not None:
            idx = roll_die(len(self.face_values), rng) - 1
            return self.face_values[idx]
        return roll_die(self.faces, rng)

    def _make_dice_context(self) -> "DiceContext":  # noqa: F821
        from dice.modifiers.base import DiceContext

        if self.face_values is not None:
            return DiceContext(
                max_value=max(self.face_values),
                min_value=min(self.face_values),
                roll_fn=self._roll_value,
            )
        return DiceContext(
            max_value=self.faces,
            min_value=1,
            roll_fn=self._roll_value,
        )

    def evaluate(self, rng: RNG) -> DiceTerm:
        if self._evaluated:
            return self
        self.results = [
            DieResult(value=self._roll_value(rng))
            for _ in range(self.count)
        ]
        if self.modifier_strings:
            from dice.modifiers.parser import parse_modifier_string
            from dice.modifiers.registry import apply_modifiers

            specs = parse_modifier_string("".join(self.modifier_strings))
            self._modifier_specs = specs
            self._has_target = any(s.key in self._TARGET_KEYS for s in specs)
            ctx = self._make_dice_context()
            self.results = apply_modifiers(
                self.results, specs, rng, ctx, self.max_explosions
            )
        self._evaluated = True
        return self

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "id": self.id,
            "kind": self.kind,
            "notation": self.notation,
            "dice": [r.to_dict() for r in self.results],
            "total": self.total,
        }
        if self._modifier_specs:
            d["modifiers"] = [
                {"key": s.key, "argument": s.argument, "compare_point": s.compare_point}
                for s in self._modifier_specs
            ]
        return d
