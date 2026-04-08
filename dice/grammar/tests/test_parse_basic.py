from dice.grammar import parse


def test_parse_1d6():
    r = parse("1d6")
    assert len(r.errors) == 0
    assert len(r.ast.children) == 1
    assert r.ast.children[0].kind == "dice_term"


def test_parse_2d20():
    r = parse("2d20")
    assert len(r.errors) == 0
    dt = r.ast.children[0]
    assert dt.kind == "dice_term"
    assert dt.count == 2
    assert dt.faces == 20


def test_parse_implicit_count():
    r = parse("d12")
    assert len(r.errors) == 0
    dt = r.ast.children[0]
    assert dt.count == 1
    assert dt.faces == 12


def test_parse_addition():
    r = parse("3d8+5")
    assert len(r.errors) == 0
    children = r.ast.children
    assert len(children) == 3
    assert children[0].kind == "dice_term"
    assert children[1].kind == "operator_term"
    assert children[1].operator == "+"
    assert children[2].kind == "numeric_term"
    assert children[2].value == 5


def test_parse_subtraction():
    r = parse("2d6-1")
    assert len(r.errors) == 0
    children = r.ast.children
    assert children[1].operator == "-"
    assert children[2].value == 1


def test_parse_precedence():
    r = parse("1d20+3*2")
    assert len(r.errors) == 0
    children = r.ast.children
    # Should have exactly 3 top-level children: 1d20, +, (3*2 grouped)
    assert len(children) == 3
    assert children[0].kind == "dice_term"
    assert children[1].kind == "operator_term"
    assert children[1].operator == "+"
    # The multiplication is grouped into a GroupingTerm for precedence
    assert children[2].kind == "grouping_term"
    assert len(children[2].children) == 3
    assert children[2].children[1].operator == "*"


def test_parse_ast_is_roll_expression():
    r = parse("1d6")
    assert r.ast.kind == "roll_expression"


def test_parse_expression_preserved():
    r = parse("  2d6+3  ")
    assert r.expression == "  2d6+3  "
    assert r.ast.expression == "2d6+3"


def test_parse_syntax_version():
    r = parse("1d6")
    assert r.syntax_version == "1.0"


def test_parse_plain_number():
    r = parse("42")
    assert len(r.errors) == 0
    assert r.ast.children[0].kind == "numeric_term"
    assert r.ast.children[0].value == 42
