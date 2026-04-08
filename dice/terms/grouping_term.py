from __future__ import annotations

from typing import Any

from dice.rng import RNG
from dice.terms.base import RollTerm
from dice.terms.eval_helpers import compute_infix_total


class GroupingTerm(RollTerm):
    """A synthetic precedence-grouping node inserted by the parser.

    Unlike :class:`ParentheticalTerm`, which represents user-written
    parentheses, a ``GroupingTerm`` is created by the parser to preserve
    operator precedence (e.g. the ``2*3`` in ``1d6+2*3``).  It has no
    ``expression`` field because there is no corresponding source text —
    the grouping is implicit.
    """

    kind: str = "grouping_term"

    def __init__(
        self,
        *,
        children: list[RollTerm],
        id: str | None = None,
    ) -> None:
        super().__init__(id=id)
        self.children = children
        self._total: int | float = 0

    @property
    def total(self) -> int | float:
        return self._total

    def evaluate(self, rng: RNG) -> GroupingTerm:
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
            "children": [c.to_dict() for c in self.children],
            "total": self.total,
        }
