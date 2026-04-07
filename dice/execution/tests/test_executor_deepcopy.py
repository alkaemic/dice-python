"""Tests proving that copy.deepcopy in executor.py is redundant.

dice/execution/executor.py line 27 does:

    tree = copy.deepcopy(ast.to_dict())

Every to_dict() implementation builds fresh dict and list objects via
dict literals and list comprehensions. There are no shared references
between successive to_dict() calls, so deepcopy duplicates already-fresh
objects for no benefit.

These tests verify this by calling to_dict() twice and confirming that
all objects at every level are already distinct (different identity),
while remaining structurally equal.
"""

from __future__ import annotations

import copy
import timeit
from typing import Any

from dice.execution.config import ExecutionConfig
from dice.execution.evaluator import _EvalContext, evaluate_tree
from dice.grammar import parse
from dice.rng import SeededRNG


def _evaluate_ast(expression: str, seed: int = 42):
    """Parse and evaluate an expression, returning the AST."""
    ast = parse(expression).ast
    ctx = _EvalContext(rng=SeededRNG(seed), config=ExecutionConfig())
    evaluate_tree(ast, ctx)
    return ast


def _collect_all_objects(obj: Any, seen: set[int] | None = None) -> list[Any]:
    """Recursively collect all dict and list objects from a nested structure."""
    if seen is None:
        seen = set()
    result = []
    obj_id = id(obj)
    if obj_id in seen:
        return result
    seen.add(obj_id)
    if isinstance(obj, dict):
        result.append(obj)
        for v in obj.values():
            result.extend(_collect_all_objects(v, seen))
    elif isinstance(obj, list):
        result.append(obj)
        for item in obj:
            result.extend(_collect_all_objects(item, seen))
    return result


def test_to_dict_produces_distinct_objects_simple():
    """Two to_dict() calls on the same AST produce entirely separate objects."""
    ast = _evaluate_ast("2d6+3")

    d1 = ast.to_dict()
    d2 = ast.to_dict()

    assert d1 == d2, "to_dict() should produce structurally equal results"

    objs1 = _collect_all_objects(d1)
    objs2 = _collect_all_objects(d2)

    ids1 = {id(o) for o in objs1}
    ids2 = {id(o) for o in objs2}

    shared = ids1 & ids2
    assert not shared, (
        f"to_dict() calls share {len(shared)} objects — deepcopy is needed "
        f"only if this set is non-empty"
    )


def test_to_dict_produces_distinct_objects_complex():
    """Verify no shared references for a more complex expression."""
    ast = _evaluate_ast("2d20+1d8+5")

    d1 = ast.to_dict()
    d2 = ast.to_dict()

    assert d1 == d2

    objs1 = _collect_all_objects(d1)
    objs2 = _collect_all_objects(d2)

    ids1 = {id(o) for o in objs1}
    ids2 = {id(o) for o in objs2}

    shared = ids1 & ids2
    assert not shared, (
        f"to_dict() calls share {len(shared)} objects for complex expression"
    )


def test_to_dict_produces_distinct_objects_with_modifiers():
    """Verify no shared references when dice have modifiers."""
    ast = _evaluate_ast("4d6kh3")

    d1 = ast.to_dict()
    d2 = ast.to_dict()

    assert d1 == d2

    objs1 = _collect_all_objects(d1)
    objs2 = _collect_all_objects(d2)

    ids1 = {id(o) for o in objs1}
    ids2 = {id(o) for o in objs2}

    shared = ids1 & ids2
    assert not shared, (
        f"to_dict() calls share {len(shared)} objects for expression with modifiers"
    )


def test_mutating_to_dict_result_does_not_affect_ast():
    """Mutating a to_dict() result must not change the AST or future calls.

    If to_dict() returned references to internal AST state, mutations
    would corrupt the AST. This test proves to_dict() is already safe
    without deepcopy.
    """
    ast = _evaluate_ast("2d6+3")

    d1 = ast.to_dict()
    # Mutate the result at multiple levels
    d1["total"] = 9999
    d1["children"][0]["dice"][0]["value"] = -1
    d1["children"].pop()

    # A fresh to_dict() call should be unaffected
    d2 = ast.to_dict()
    assert d2["total"] != 9999, "Mutation of to_dict() result corrupted the AST"
    assert d2["children"][0]["dice"][0]["value"] != -1
    assert len(d2["children"]) == 3


def test_deepcopy_of_to_dict_equals_plain_to_dict():
    """deepcopy(to_dict()) produces the same result as to_dict() alone.

    Since to_dict() already creates all-new objects, deepcopy is a no-op
    in terms of data — it just wastes time copying fresh objects.
    """
    ast = _evaluate_ast("3d8+1d4-2")

    plain = ast.to_dict()
    copied = copy.deepcopy(ast.to_dict())

    assert plain == copied, (
        "deepcopy(to_dict()) and to_dict() should be structurally identical"
    )


def test_deepcopy_is_slower_than_plain_to_dict():
    """deepcopy(to_dict()) takes measurably longer than to_dict() alone.

    This demonstrates the performance cost of the redundant deepcopy.
    We use a moderately complex expression to make the overhead visible.
    """
    ast = _evaluate_ast("4d20+3d8+2d6+1d4+5")

    iterations = 1000
    plain_time = timeit.timeit(lambda: ast.to_dict(), number=iterations)
    copy_time = timeit.timeit(
        lambda: copy.deepcopy(ast.to_dict()), number=iterations
    )

    assert copy_time > plain_time, (
        f"Expected deepcopy ({copy_time:.4f}s) to be slower than plain "
        f"to_dict ({plain_time:.4f}s) over {iterations} iterations"
    )
