# Development Environment

## Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (package manager)
- [Task](https://taskfile.dev/) (optional, for task runner commands)

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/alkaemic/dice-python.git
   cd dice-python
   ```

2. Install dependencies:
   ```bash
   uv sync
   ```

   This creates a virtual environment in `.venv/` and installs all production and dev dependencies.

3. Verify the setup:
   ```bash
   uv run pytest -x
   ```

## Tools

| Tool | Purpose | Command |
|---|---|---|
| [pytest](https://docs.pytest.org/) | Test runner | `uv run pytest` |
| [ruff](https://docs.astral.sh/ruff/) | Linter | `uv run ruff check dice/` |
| [black](https://black.readthedocs.io/) | Code formatter | `uv run black dice/` |
| [mypy](https://mypy.readthedocs.io/) | Type checker | `uv run mypy dice/` |

## Task Runner

If you have [Task](https://taskfile.dev/) installed, you can use the shorthand commands:

```bash
task build           # Build the package
task test            # Run tests (stop on first failure)
task test:coverage   # Run tests with coverage report
```
