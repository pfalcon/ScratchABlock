from core import *

def test_render_operator_precedence():

    e = EXPR("+", [VALUE(1), VALUE(2)])
    assert str(e) == "0x1 + 0x2"

    e = EXPR("+", [VALUE(1), EXPR("*", [VALUE(2), VALUE(3)])])
    assert str(e) == "0x1 + 0x2 * 0x3"

    e = EXPR("*", [VALUE(1), EXPR("+", [VALUE(2), VALUE(3)])])
    assert str(e) == "0x1 * (0x2 + 0x3)"

    e = EXPR("-", VALUE(1), VALUE(2))
    assert str(e) == "0x1 - 0x2"

    e = EXPR("-", VALUE(1), EXPR("*", VALUE(2), VALUE(3)))
    assert str(e) == "0x1 - 0x2 * 0x3"

    e = EXPR("-", VALUE(1), EXPR("+", VALUE(2), VALUE(3)))
    assert str(e) == "0x1 - (0x2 + 0x3)", str(e)

    # This is not ideal, but better than have wrong above
    e = EXPR("-", EXPR("+", VALUE(2), VALUE(3)), VALUE(1))
    assert str(e) == "(0x2 + 0x3) - 0x1", str(e)
