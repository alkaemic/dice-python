from dice.grammar import parse


def test_parse_advantage_plus_modifier():
    r = parse("2d20kh1+7")
    assert len(r.errors) == 0
    children = r.ast.children
    assert children[0].kind == "dice_term"
    assert children[0].count == 2
    assert children[0].faces == 20
    assert children[0].modifier_strings == ["kh1"]
    assert children[1].operator == "+"
    assert children[2].value == 7


def test_parse_stat_roll():
    r = parse("4d6dl1+2d4+5")
    assert len(r.errors) == 0
    children = r.ast.children
    assert children[0].kind == "dice_term"
    assert children[0].modifier_strings == ["dl1"]
    assert children[1].operator == "+"
    assert children[2].kind == "dice_term"
    assert children[3].operator == "+"
    assert children[4].value == 5


def test_parse_parenthetical_complex():
    r = parse("(1d8+3)*2-1d4")
    assert len(r.errors) == 0
    children = r.ast.children
    # Should be: grouping(paren, *, 2), -, 1d4
    assert children[0].kind == "grouping_term"


def test_parse_function_in_expression():
    r = parse("floor(1d6+3)")
    assert len(r.errors) == 0
    ft = r.ast.children[0]
    assert ft.kind == "function_term"
    assert ft.function == "floor"
    assert len(ft.children) >= 1
