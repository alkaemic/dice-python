from dice.rng import SeededRNG
from dice.terms import FateDiceTerm


def test_fate_dice_kind():
    dt = FateDiceTerm(count=4)
    assert dt.kind == "fate_dice_term"


def test_fate_dice_notation():
    dt = FateDiceTerm(count=4)
    assert dt.notation == "4dF"


def test_fate_dice_values_in_range():
    rng = SeededRNG(42)
    dt = FateDiceTerm(count=100)
    dt.evaluate(rng)
    for r in dt.results:
        assert r.value in {-1, 0, 1}


def test_fate_dice_deterministic():
    dt1 = FateDiceTerm(count=10)
    dt2 = FateDiceTerm(count=10)
    dt1.evaluate(SeededRNG(42))
    dt2.evaluate(SeededRNG(42))
    assert [r.value for r in dt1.results] == [r.value for r in dt2.results]


def test_fate_dice_total():
    rng = SeededRNG(42)
    dt = FateDiceTerm(count=4)
    dt.evaluate(rng)
    assert dt.total == sum(r.value for r in dt.results if r.kept)


def test_fate_dice_to_dict():
    rng = SeededRNG(42)
    dt = FateDiceTerm(count=4, id="fate01")
    dt.evaluate(rng)
    d = dt.to_dict()
    assert d["id"] == "fate01"
    assert d["kind"] == "fate_dice_term"
    assert d["notation"] == "4dF"
    assert len(d["dice"]) == 4


def test_fate_dice_with_modifier():
    rng = SeededRNG(42)
    dt = FateDiceTerm(count=4, modifier_strings=["kh2"])
    dt.evaluate(rng)
    kept = [r for r in dt.results if r.kept]
    assert len(kept) == 2
    assert dt.notation == "4dFkh2"


# ---------------------------------------------------------------------------
# Bug: modifiers produce invalid values for fate dice
#
# FateDiceTerm.evaluate() offsets initial rolls by -2 (roll_die(3) - 2) to
# get {-1, 0, 1}. But modifiers (reroll, explode) call roll_die(faces, rng)
# directly, producing raw values {1, 2, 3} without the offset.
# ---------------------------------------------------------------------------


def test_rerolled_fate_dice_values_must_be_in_valid_range():
    """Rerolled fate dice should only contain values in {-1, 0, 1}.

    The reroll modifier creates replacement dice via roll_die(3, rng) which
    returns 1-3. Without applying the -2 fate offset, these replacements
    will have invalid values (1, 2, or 3 instead of -1, 0, or 1).
    """
    # "r<1" means: reroll any die with value < 1, i.e. fate values 0 and -1.
    for seed in range(50):
        dt = FateDiceTerm(count=4, modifier_strings=["r<1"])
        dt.evaluate(SeededRNG(seed))
        for r in dt.results:
            assert r.value in {-1, 0, 1}, (
                f"Fate die has invalid value {r.value} after reroll "
                f"(seed={seed}, all values={[x.value for x in dt.results]})"
            )


def test_reroll_once_fate_dice_values_must_be_in_valid_range():
    """Reroll-once replacement dice must also be in {-1, 0, 1}."""
    for seed in range(50):
        dt = FateDiceTerm(count=4, modifier_strings=["ro<1"])
        dt.evaluate(SeededRNG(seed))
        for r in dt.results:
            assert r.value in {-1, 0, 1}, (
                f"Fate die has invalid value {r.value} after reroll-once "
                f"(seed={seed}, all values={[x.value for x in dt.results]})"
            )


def test_exploded_fate_dice_values_must_be_in_valid_range():
    """Exploded fate dice should only contain values in {-1, 0, 1}.

    The explode modifier creates new dice via roll_die(3, rng) which returns
    1-3. Without applying the -2 fate offset, these new dice will have
    impossible values for fate dice.
    """
    # "!=1" means: explode any die that equals 1.
    for seed in range(50):
        dt = FateDiceTerm(count=4, modifier_strings=["!=1"])
        dt.evaluate(SeededRNG(seed))
        for r in dt.results:
            assert r.value in {-1, 0, 1}, (
                f"Fate die has invalid value {r.value} after explode "
                f"(seed={seed}, all values={[x.value for x in dt.results]})"
            )


def test_fate_dice_total_cannot_exceed_result_count():
    """The total of fate dice can never exceed the number of kept results.

    Each fate die is at most +1, so the maximum total equals the number of
    kept results. If modifiers introduce raw 1-3 values, the total can
    exceed this theoretical maximum.
    """
    for seed in range(50):
        dt = FateDiceTerm(count=4, modifier_strings=["!=1"])
        dt.evaluate(SeededRNG(seed))
        kept = [r for r in dt.results if r.kept]
        kept_count = len(kept)
        assert dt.total <= kept_count, (
            f"Fate dice total {dt.total} exceeds maximum possible "
            f"{kept_count} (seed={seed}, "
            f"values={[r.value for r in dt.results]}, "
            f"kept_values={[r.value for r in kept]})"
        )
        assert dt.total >= -kept_count, (
            f"Fate dice total {dt.total} below minimum possible "
            f"{-kept_count} (seed={seed})"
        )
