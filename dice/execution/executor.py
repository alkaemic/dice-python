from __future__ import annotations

from dice.constants import SYNTAX_VERSION
from dice.execution.config import ExecutionConfig
from dice.execution.evaluator import _EvalContext, evaluate_tree
from dice.execution.result import ExecutionResult
from dice.rng import RNG, DefaultRNG
from dice.terms import RollExpression


def execute(
    ast: RollExpression,
    *,
    rng: RNG | None = None,
    config: ExecutionConfig | None = None,
) -> ExecutionResult:
    """Execute a parsed AST and return the execution tree."""
    if rng is None:
        rng = DefaultRNG()
    if config is None:
        config = ExecutionConfig()

    evaluate_tree(ast, _EvalContext(rng, config))

    tree = ast.to_dict()
    return ExecutionResult(
        tree=tree,
        total=ast.total,
        expression=ast.expression,
        syntax_version=SYNTAX_VERSION,
    )
