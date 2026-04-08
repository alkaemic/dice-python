from dice.rng import SeededRNG
from dice.terms import DiceTerm


def test_dice_term_kind():
    dt = DiceTerm(count=2, faces=6)
    assert dt.kind == "dice_term"


def test_dice_term_notation():
    dt = DiceTerm(count=2, faces=20)
    assert dt.notation == "2d20"


def test_dice_term_notation_with_modifiers():
    dt = DiceTerm(count=2, faces=20, modifier_strings=["kh1"])
    assert dt.notation == "2d20kh1"


def test_dice_term_evaluate_populates_results():
    rng = SeededRNG(42)
    dt = DiceTerm(count=3, faces=6)
    dt.evaluate(rng)
    assert len(dt.results) == 3
    for r in dt.results:
        assert 1 <= r.value <= 6


def test_dice_term_evaluate_deterministic():
    dt1 = DiceTerm(count=4, faces=20)
    dt2 = DiceTerm(count=4, faces=20)
    dt1.evaluate(SeededRNG(99))
    dt2.evaluate(SeededRNG(99))
    assert [r.value for r in dt1.results] == [r.value for r in dt2.results]


def test_dice_term_total_sums_kept():
    rng = SeededRNG(42)
    dt = DiceTerm(count=3, faces=6)
    dt.evaluate(rng)
    expected = sum(r.value for r in dt.results if r.kept)
    assert dt.total == expected


def test_dice_term_keep_highest():
    rng = SeededRNG(42)
    dt = DiceTerm(count=4, faces=20, modifier_strings=["kh1"])
    dt.evaluate(rng)
    assert len(dt.results) == 4
    kept = [r for r in dt.results if r.kept]
    assert len(kept) == 1
    assert kept[0].value == max(r.value for r in dt.results)


def test_dice_term_keep_lowest():
    rng = SeededRNG(42)
    dt = DiceTerm(count=4, faces=20, modifier_strings=["kl1"])
    dt.evaluate(rng)
    kept = [r for r in dt.results if r.kept]
    assert len(kept) == 1
    assert kept[0].value == min(r.value for r in dt.results)


def test_dice_term_drop_highest():
    rng = SeededRNG(42)
    dt = DiceTerm(count=4, faces=20, modifier_strings=["dh1"])
    dt.evaluate(rng)
    kept = [r for r in dt.results if r.kept]
    assert len(kept) == 3
    max_val = max(r.value for r in dt.results)
    dropped = [r for r in dt.results if not r.kept]
    assert dropped[0].value == max_val


def test_dice_term_drop_lowest():
    rng = SeededRNG(42)
    dt = DiceTerm(count=4, faces=20, modifier_strings=["dl1"])
    dt.evaluate(rng)
    kept = [r for r in dt.results if r.kept]
    assert len(kept) == 3
    min_val = min(r.value for r in dt.results)
    dropped = [r for r in dt.results if not r.kept]
    assert dropped[0].value == min_val


def test_dice_term_to_dict():
    rng = SeededRNG(42)
    dt = DiceTerm(count=2, faces=6, id="test1234")
    dt.evaluate(rng)
    d = dt.to_dict()
    assert d["id"] == "test1234"
    assert d["kind"] == "dice_term"
    assert d["notation"] == "2d6"
    assert len(d["dice"]) == 2
    assert d["total"] == dt.total


def test_dice_term_to_dict_with_modifier():
    rng = SeededRNG(42)
    dt = DiceTerm(count=2, faces=20, modifier_strings=["kh1"], id="abc")
    dt.evaluate(rng)
    d = dt.to_dict()
    assert d["notation"] == "2d20kh1"
    kept_dice = [die for die in d["dice"] if die["kept"]]
    assert len(kept_dice) == 1


def test_dice_term_single_die():
    rng = SeededRNG(0)
    dt = DiceTerm(count=1, faces=20)
    dt.evaluate(rng)
    assert len(dt.results) == 1
    assert dt.total == dt.results[0].value


# ---------------------------------------------------------------------------
# GAP #7: Modifiers not serialized in execution tree
# ---------------------------------------------------------------------------


def test_to_dict_without_modifiers_has_no_modifiers_key():
    """A plain dice term (no modifiers) should not include a 'modifiers' key."""
    rng = SeededRNG(42)
    dt = DiceTerm(count=2, faces=6, id="plain")
    dt.evaluate(rng)
    d = dt.to_dict()
    # 'modifiers' should be absent when no modifiers were applied
    assert "modifiers" not in d


def test_to_dict_includes_modifiers_key_for_keep_highest():
    """When kh3 is applied, to_dict() should include a 'modifiers' field
    listing the parsed modifier specs so consumers can inspect which
    modifiers were applied — not just their side-effects on individual dice.
    """
    rng = SeededRNG(42)
    dt = DiceTerm(count=4, faces=6, modifier_strings=["kh3"], id="kh-test")
    dt.evaluate(rng)
    d = dt.to_dict()

    # This assertion documents the gap: 'modifiers' is missing from the dict
    assert "modifiers" in d, (
        "to_dict() does not include a 'modifiers' key — consumers cannot "
        "programmatically determine which modifiers were applied"
    )
    assert len(d["modifiers"]) == 1
    assert d["modifiers"][0]["key"] == "kh"
    assert d["modifiers"][0]["argument"] == 3


def test_to_dict_includes_modifiers_key_for_drop_lowest():
    """dl1 and kh3 have the same observable effect on 4d6, but to_dict()
    should let a consumer distinguish between them.
    """
    rng = SeededRNG(42)
    dt = DiceTerm(count=4, faces=6, modifier_strings=["dl1"], id="dl-test")
    dt.evaluate(rng)
    d = dt.to_dict()

    assert "modifiers" in d, (
        "to_dict() does not include a 'modifiers' key — consumers cannot "
        "distinguish dl1 from kh3"
    )
    assert len(d["modifiers"]) == 1
    assert d["modifiers"][0]["key"] == "dl"
    assert d["modifiers"][0]["argument"] == 1


def test_to_dict_includes_multiple_modifiers():
    """When multiple modifiers are chained (e.g. reroll + keep highest),
    all of them should appear in the serialized output.
    """
    rng = SeededRNG(42)
    dt = DiceTerm(count=4, faces=6, modifier_strings=["r<2kh3"], id="multi")
    dt.evaluate(rng)
    d = dt.to_dict()

    assert "modifiers" in d, (
        "to_dict() does not include a 'modifiers' key for chained modifiers"
    )
    keys = [m["key"] for m in d["modifiers"]]
    assert "r" in keys, "Reroll modifier (r<2) missing from serialized output"
    assert "kh" in keys, "Keep-highest modifier missing from serialized output"


def test_to_dict_modifier_includes_compare_point():
    """Modifiers with compare points (e.g. r<2) should serialize the
    compare_point so consumers can reconstruct the full modifier spec.
    """
    rng = SeededRNG(42)
    dt = DiceTerm(count=4, faces=6, modifier_strings=["r<2"], id="cp-test")
    dt.evaluate(rng)
    d = dt.to_dict()

    assert "modifiers" in d, (
        "to_dict() does not include a 'modifiers' key — compare point "
        "information is lost"
    )
    mod = d["modifiers"][0]
    assert mod["key"] == "r"
    assert mod["compare_point"] == "<2"


def test_to_dict_kh_vs_dl_distinguishable():
    """The whole point of serializing modifiers: a consumer should be able
    to tell kh3 apart from dl1 even though both drop 1 die from 4d6.

    Currently to_dict() only shows kept=False on individual dice, making
    it impossible to determine which modifier caused the drop.
    """
    rng_seed = 42
    dt_kh = DiceTerm(count=4, faces=6, modifier_strings=["kh3"], id="kh")
    dt_kh.evaluate(SeededRNG(rng_seed))

    dt_dl = DiceTerm(count=4, faces=6, modifier_strings=["dl1"], id="dl")
    dt_dl.evaluate(SeededRNG(rng_seed))

    d_kh = dt_kh.to_dict()
    d_dl = dt_dl.to_dict()

    # Without a 'modifiers' field, these two dicts are structurally identical
    # (same dice values, same kept/dropped pattern) — this is the gap.
    assert "modifiers" in d_kh and "modifiers" in d_dl, (
        "Cannot distinguish kh3 from dl1 in to_dict() output — "
        "both produce identical dice arrays with no modifier metadata"
    )
    assert d_kh["modifiers"] != d_dl["modifiers"], (
        "kh3 and dl1 should serialize to different modifier specs"
    )
