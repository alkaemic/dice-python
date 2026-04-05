# Testing

## Running Tests

```bash
# Run all tests (stop on first failure)
uv run pytest -x

# Run all tests with verbose output
uv run pytest -v

# Run tests with coverage
uv run pytest --cov=dice --cov-report=term-missing

# Run a specific test file
uv run pytest dice/terms/tests/test_dice_term.py

# Run tests matching a keyword
uv run pytest -k "explode"
```

Or with Task:

```bash
task test
task test:coverage
```

## Test Organization

Tests live inside the package they test:

```
dice/grammar/tests/test_parse_basic.py
dice/terms/tests/test_dice_term.py
dice/modifiers/tests/test_keep.py
dice/execution/tests/test_execute_basic.py
dice/evaluation/tests/test_default_evaluator.py
dice/rng/tests/test_seeded_rng.py
dice/tests/test_integration.py
```

## Writing Tests

- Function-based tests only (no test classes)
- Use `SeededRNG` for deterministic results whenever dice are rolled
- Test names should describe the behavior being verified
- Test edge cases, not just happy paths

Example:

```python
from dice import roll, SeededRNG


def test_keep_highest_drops_lowest_rolls():
    rng = SeededRNG(42)
    result = roll("4d6kh3", rng=rng)
    tree = result.tree
    dice_node = tree["children"][0]
    kept = [d for d in dice_node["dice"] if d["kept"]]
    dropped = [d for d in dice_node["dice"] if not d["kept"]]
    assert len(kept) == 3
    assert len(dropped) == 1
    assert min(d["value"] for d in kept) >= max(d["value"] for d in dropped)
```

## Linting and Type Checking

```bash
uv run ruff check dice/    # Lint
uv run mypy dice/          # Type check
```
