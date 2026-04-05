"""Tests that verify the dice library does not pollute the root logger.

Libraries must not call logging.basicConfig() — doing so adds a handler to
the root logger, which silently overrides the host application's logging
configuration. See: https://docs.python.org/3/howto/logging.html#configuring-logging-for-a-library

The recommended pattern for libraries is:

    logger = logging.getLogger(__name__)
    logger.addHandler(logging.NullHandler())
"""

from __future__ import annotations

import importlib
import logging
import sys


def _fresh_import_dice() -> int:
    """Import (or re-import) the dice package and return the number of
    handlers added to the root logger during the import.

    We snapshot root handlers before and after to isolate the effect
    of the import.
    """
    # Remove dice and all submodules from sys.modules so the import
    # re-executes __init__.py from scratch.
    dice_modules = [key for key in sys.modules if key == "dice" or key.startswith("dice.")]
    for mod in dice_modules:
        del sys.modules[mod]

    # Snapshot current root handlers
    root = logging.getLogger()
    handlers_before = list(root.handlers)

    import dice  # noqa: F401

    handlers_after = list(root.handlers)
    new_handlers = len(handlers_after) - len(handlers_before)

    # Clean up: remove any handlers the import added so we don't
    # pollute other tests.
    for handler in handlers_after:
        if handler not in handlers_before:
            root.removeHandler(handler)

    return new_handlers


def test_import_does_not_add_root_handlers():
    """Importing the dice package should not add handlers to the root logger."""
    new_handlers = _fresh_import_dice()
    assert new_handlers == 0, (
        f"Importing dice added {new_handlers} handler(s) to the root logger. "
        f"Libraries must not call logging.basicConfig(). Use "
        f"logging.getLogger(__name__).addHandler(logging.NullHandler()) instead."
    )


def test_import_does_not_call_basic_config():
    """The dice package should not call logging.basicConfig()."""
    # Re-import to ensure __init__.py runs
    dice_modules = [key for key in sys.modules if key == "dice" or key.startswith("dice.")]
    for mod in dice_modules:
        del sys.modules[mod]

    root = logging.getLogger()
    # Clear existing handlers to ensure basicConfig would actually add one
    original_handlers = list(root.handlers)
    root.handlers = []

    try:
        importlib.import_module("dice")
        # If basicConfig was called, it would have added a StreamHandler
        stream_handlers = [
            h for h in root.handlers if isinstance(h, logging.StreamHandler)
        ]
        assert len(stream_handlers) == 0, (
            f"Importing dice added {len(stream_handlers)} StreamHandler(s) to "
            f"the root logger, indicating logging.basicConfig() was called."
        )
    finally:
        # Restore original handlers
        root.handlers = original_handlers
