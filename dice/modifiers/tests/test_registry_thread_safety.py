"""Tests for registry thread safety.

Both _MODIFIER_REGISTRY and _EVALUATOR_REGISTRY are module-level mutable
dicts with no synchronization. Under CPython's GIL, simple dict
operations are effectively atomic, so concurrent access does not corrupt
state. On free-threaded Python (PEP 703), this guarantee does not hold.

These tests verify that concurrent registration does not corrupt the
registry under the current runtime. They pass today because of the GIL,
not because the code is thread-safe by design. They serve as a canary:
if they start failing on a free-threaded build, the registries need a
lock.
"""

from __future__ import annotations

import threading

from dice.evaluation.registry import (
    _EVALUATOR_REGISTRY,
    get_evaluator,
    register_evaluator,
)
from dice.modifiers.registry import (
    _MODIFIER_REGISTRY,
    get_modifier,
    register_modifier,
)


def test_concurrent_modifier_registration_does_not_corrupt():
    """Concurrent register_modifier calls should not lose entries."""
    key_prefix = "_thread_test_mod_"
    num_threads = 10
    registrations_per_thread = 100

    def register_batch(thread_id: int) -> None:
        for i in range(registrations_per_thread):
            key = f"{key_prefix}{thread_id}_{i}"
            register_modifier(key, lambda r, s, rng, f, me=0: r)

    threads = [
        threading.Thread(target=register_batch, args=(t,))
        for t in range(num_threads)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # Verify all registrations landed
    expected = num_threads * registrations_per_thread
    registered = [k for k in _MODIFIER_REGISTRY if k.startswith(key_prefix)]
    assert len(registered) == expected, (
        f"Expected {expected} test modifiers, found {len(registered)}. "
        f"Concurrent registration lost entries."
    )

    # Clean up
    for k in registered:
        _MODIFIER_REGISTRY.pop(k, None)


def test_concurrent_modifier_read_write_does_not_crash():
    """Concurrent reads and writes to the modifier registry should not crash."""
    key = "_thread_rw_test"
    barrier = threading.Barrier(4)

    def writer() -> None:
        barrier.wait()
        for _ in range(500):
            register_modifier(key, lambda r, s, rng, f, me=0: r)

    def reader() -> None:
        barrier.wait()
        for _ in range(500):
            get_modifier(key)

    threads = [
        threading.Thread(target=writer),
        threading.Thread(target=writer),
        threading.Thread(target=reader),
        threading.Thread(target=reader),
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    _MODIFIER_REGISTRY.pop(key, None)


def test_concurrent_evaluator_registration_does_not_corrupt():
    """Concurrent register_evaluator calls should not lose entries."""
    key_prefix = "_thread_test_eval_"
    num_threads = 10
    registrations_per_thread = 100

    class StubEvaluator:
        def evaluate(self, tree, template=None, context=None):
            return {"primary_total": 0, "outcome": None}

    def register_batch(thread_id: int) -> None:
        for i in range(registrations_per_thread):
            key = f"{key_prefix}{thread_id}_{i}"
            register_evaluator(key, StubEvaluator())

    threads = [
        threading.Thread(target=register_batch, args=(t,))
        for t in range(num_threads)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    expected = num_threads * registrations_per_thread
    registered = [k for k in _EVALUATOR_REGISTRY if k.startswith(key_prefix)]
    assert len(registered) == expected, (
        f"Expected {expected} test evaluators, found {len(registered)}. "
        f"Concurrent registration lost entries."
    )

    for k in registered:
        _EVALUATOR_REGISTRY.pop(k, None)
