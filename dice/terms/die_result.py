from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class DieResult:
    value: int
    kept: bool = True
    exploded: bool = False
    rerolled: bool = False
    critical: str | None = None  # "success" or "failure"
    matched: bool = False
    failure: bool = False

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {"value": self.value, "kept": self.kept}
        if self.exploded:
            d["exploded"] = True
        if self.rerolled:
            d["rerolled"] = True
        if self.critical:
            d["critical"] = self.critical
        if self.matched:
            d["matched"] = True
        if self.failure:
            d["failure"] = True
        return d
