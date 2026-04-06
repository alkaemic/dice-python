from __future__ import annotations

import threading
from typing import Any

from dice.evaluation.base import Evaluator
from dice.evaluation.default import DefaultEvaluator

_EVALUATOR_REGISTRY: dict[str, Evaluator] = {}
_EVALUATOR_LOCK = threading.Lock()
_DEFAULT_EVALUATOR = DefaultEvaluator()


def register_evaluator(system: str, evaluator: Evaluator) -> None:
    """Register a game-system evaluator."""
    with _EVALUATOR_LOCK:
        _EVALUATOR_REGISTRY[system] = evaluator


def get_evaluator(system: str | None) -> Evaluator:
    """Get evaluator by system identifier, falling back to default."""
    if system is None:
        return _DEFAULT_EVALUATOR
    with _EVALUATOR_LOCK:
        return _EVALUATOR_REGISTRY.get(system, _DEFAULT_EVALUATOR)


def evaluate(
    execution_tree: dict[str, Any],
    system: str | None = None,
    template: str | None = None,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Evaluate an execution tree using the registered evaluator."""
    evaluator = get_evaluator(system)
    return evaluator.evaluate(execution_tree, template, context)
