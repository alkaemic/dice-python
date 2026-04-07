from dice.grammar import parse
from dice.terms import FATE_FACE_VALUES, DiceTerm


def test_parse_fate():
    r = parse("4dF")
    assert len(r.errors) == 0
    dt = r.ast.children[0]
    assert isinstance(dt, DiceTerm)
    assert dt.face_values == FATE_FACE_VALUES
    assert dt.count == 4


def test_parse_fate_with_modifier():
    r = parse("4dF+3")
    assert len(r.errors) == 0
    children = r.ast.children
    assert isinstance(children[0], DiceTerm)
    assert children[0].face_values == FATE_FACE_VALUES
    assert children[1].kind == "operator_term"
    assert children[2].kind == "numeric_term"
    assert children[2].value == 3


def test_parse_fate_implicit_count():
    r = parse("dF")
    assert len(r.errors) == 0
    dt = r.ast.children[0]
    assert isinstance(dt, DiceTerm)
    assert dt.face_values == FATE_FACE_VALUES
    assert dt.count == 1
