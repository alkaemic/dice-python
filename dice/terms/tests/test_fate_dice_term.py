from dice.rng import SeededRNG
from dice.terms import FATE_FACE_VALUES, DiceTerm


def _fate(count: int, **kwargs: object) -> DiceTerm:
    """Shorthand for creating a fate DiceTerm."""
    return DiceTerm(
        count=count,
        faces=len(FATE_FACE_VALUES),
        face_values=FATE_FACE_VALUES,
        notation_label="F",
        **kwargs,  # type: ignore[arg-type]
    )


def test_fate_dice_kind():
    dt = _fate(4)
    assert dt.kind == "dice_term"


def test_fate_dice_notation():
    dt = _fate(4)
    assert dt.notation == "4dF"


def test_fate_dice_values_in_range():
    rng = SeededRNG(42)
    dt = _fate(100)
    dt.evaluate(rng)
    for r in dt.results:
        assert r.value in {-1, 0, 1}


def test_fate_dice_deterministic():
    dt1 = _fate(10)
    dt2 = _fate(10)
    dt1.evaluate(SeededRNG(42))
    dt2.evaluate(SeededRNG(42))
    assert [r.value for r in dt1.results] == [r.value for r in dt2.results]


def test_fate_dice_total():
    rng = SeededRNG(42)
    dt = _fate(4)
    dt.evaluate(rng)
    assert dt.total == sum(r.value for r in dt.results if r.kept)


def test_fate_dice_to_dict():
    rng = SeededRNG(42)
    dt = _fate(4, id="fate01")
    dt.evaluate(rng)
    d = dt.to_dict()
    assert d["id"] == "fate01"
    assert d["kind"] == "dice_term"
    assert d["notation"] == "4dF"
    assert len(d["dice"]) == 4


def test_fate_dice_with_modifier():
    rng = SeededRNG(42)
    dt = _fate(4, modifier_strings=["kh2"])
    dt.evaluate(rng)
    kept = [r for r in dt.results if r.kept]
    assert len(kept) == 2
    assert dt.notation == "4dFkh2"


# ---------------------------------------------------------------------------
# Modifiers produce correct values for fate dice
#
# Because DiceTerm now passes a DiceContext with the correct roll_fn to
# modifiers, all modifier-created dice (reroll, explode, etc.) automatically
# produce values within {-1, 0, 1} for fate dice.
# ---------------------------------------------------------------------------


def test_rerolled_fate_dice_values_must_be_in_valid_range():
    """Rerolled fate dice should only contain values in {-1, 0, 1}."""
    # "r<1" means: reroll any die with value < 1, i.e. fate values 0 and -1.
    for seed in range(50):
        dt = _fate(4, modifier_strings=["r<1"])
        dt.evaluate(SeededRNG(seed))
        for r in dt.results:
            assert r.value in {-1, 0, 1}, (
                f"Fate die has invalid value {r.value} after reroll "
                f"(seed={seed}, all values={[x.value for x in dt.results]})"
            )


def test_reroll_once_fate_dice_values_must_be_in_valid_range():
    """Reroll-once replacement dice must also be in {-1, 0, 1}."""
    for seed in range(50):
        dt = _fate(4, modifier_strings=["ro<1"])
        dt.evaluate(SeededRNG(seed))
        for r in dt.results:
            assert r.value in {-1, 0, 1}, (
                f"Fate die has invalid value {r.value} after reroll-once "
                f"(seed={seed}, all values={[x.value for x in dt.results]})"
            )


def test_exploded_fate_dice_values_must_be_in_valid_range():
    """Exploded fate dice should only contain values in {-1, 0, 1}."""
    # "!=1" means: explode any die that equals 1.
    for seed in range(50):
        dt = _fate(4, modifier_strings=["!=1"])
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
        dt = _fate(4, modifier_strings=["!=1"])
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
