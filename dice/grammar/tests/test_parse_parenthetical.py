from dice.grammar import parse


def test_parse_parenthetical_multiply():
    r = parse("(2d6+3)*2")
    assert len(r.errors) == 0
    children = r.ast.children
    # Mul/div is wrapped in a ParentheticalTerm for precedence
    mul_group = children[0]
    assert mul_group.kind == "parenthetical_term"
    assert mul_group.children[0].kind == "parenthetical_term"  # (2d6+3)
    assert mul_group.children[1].kind == "operator_term"
    assert mul_group.children[1].operator == "*"
    assert mul_group.children[2].kind == "numeric_term"


def test_parse_nested_parenthetical():
    r = parse("1d20+(2d4+1)")
    assert len(r.errors) == 0
    children = r.ast.children
    assert children[0].kind == "dice_term"
    assert children[1].kind == "operator_term"
    assert children[2].kind == "parenthetical_term"


def test_parse_parenthetical_inner_children():
    r = parse("(1d6+3)*2")
    assert len(r.errors) == 0
    # Top level is the mul/div grouping
    mul_group = r.ast.children[0]
    assert mul_group.kind == "parenthetical_term"
    assert len(mul_group.children) == 3
    # The explicit parens are the first child of the mul group
    paren = mul_group.children[0]
    assert paren.kind == "parenthetical_term"
    assert len(paren.children) == 3
    assert paren.children[0].kind == "dice_term"
    assert paren.children[1].kind == "operator_term"
    assert paren.children[2].kind == "numeric_term"
