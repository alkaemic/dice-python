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
