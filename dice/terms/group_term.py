from __future__ import annotations

import re
from typing import Any

from dice.rng import RNG
from dice.terms.base import RollTerm
from dice.terms.eval_helpers import compute_infix_total

_GROUP_MODIFIER_RE = re.compile(r"^(kh|kl|dh|dl)(\d+)$")


class GroupTerm(RollTerm):
    """A term representing a group of sub-expressions, e.g. {2d6, 3d8}kh1."""

    kind: str = "group_term"

    def __init__(
        self,
        *,
        children: list[list[RollTerm]],
        modifier_strings: list[str] | None = None,
        id: str | None = None,
    ) -> None:
        super().__init__(id=id)
        self.children = children
        self.modifier_strings: list[str] = modifier_strings or []
        self._kept: list[bool] = []
        self._child_totals: list[int | float] = []

    @property
    def total(self) -> int | float:
        return sum(t for t, k in zip(self._child_totals, self._kept) if k)

    def evaluate(self, rng: RNG) -> GroupTerm:
        if self._evaluated:
            return self
        self._child_totals = []
        for child_expr in self.children:
            for term in child_expr:
                term.evaluate(rng)
            self._child_totals.append(compute_infix_total(child_expr))

        self._kept = [True] * len(self._child_totals)
        self._apply_group_modifiers()
        self._evaluated = True
        return self

    def _apply_group_modifiers(self) -> None:
        for mod in self.modifier_strings:
            m = _GROUP_MODIFIER_RE.match(mod)
            if m is None:
                continue
            action = m.group(1)
            n = int(m.group(2))
            indexed = sorted(
                range(len(self._child_totals)),
                key=lambda i: self._child_totals[i],
            )
            if action == "kh":
                keep = set(indexed[-n:])
            elif action == "kl":
                keep = set(indexed[:n])
            elif action == "dh":
                keep = set(indexed) - set(indexed[-n:])
            elif action == "dl":
                keep = set(indexed) - set(indexed[:n])
            else:
                continue
            self._kept = [i in keep for i in range(len(self._child_totals))]

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "kind": self.kind,
            "children": [
                {
                    "terms": [t.to_dict() for t in child_expr],
                    "total": child_total,
                    "kept": kept,
                }
                for child_expr, child_total, kept in zip(
                    self.children, self._child_totals, self._kept
                )
            ],
            "total": self.total,
        }
