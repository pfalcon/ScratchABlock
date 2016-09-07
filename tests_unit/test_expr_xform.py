from core import *
from xform_expr import *

E = EXPR
V = VALUE
R = REG

def test_sub_to_add():
    e = E("-", [V(2), V(1)])
    e2 = expr_xform(e, expr_sub_to_add)
    assert e2 == E("+", [V(2), V(-1)])

    e = E("-", [R("r0"), V(10)])
    e2 = expr_xform(e, expr_sub_to_add)
    assert e2 == E("+", [R("r0"), V(-10)])

    e = E("-", [R("r0"), R("r1")])
    e2 = expr_xform(e, expr_sub_to_add)
    assert e2 == E("-", [R("r0"), R("r1")])

    e = E("-", [V(5), R("r2")])
    e2 = expr_xform(e, expr_sub_to_add)
    assert e2 == E("-", [V(5), R("r2")])

    e = E("-", [E("-", [V(3), V(2)]), V(1)])
    e2 = expr_xform(e, expr_sub_to_add)
    assert e2 == E("+", [E("+", [V(3), V(-2)]), V(-1)])


def test_associative_add():
    e = E("+", [E("+", [V(3), V(2)]), V(1)])
    e2 = expr_xform(e, expr_associative_add)
    assert e2 == E("+", [V(3), V(2), V(1)])

    e = E("+", [E("+", [V(4), V(3), V(2)]), V(1), V(5), V(6)])
    e2 = expr_xform(e, expr_associative_add)
    assert e2 == E("+", [V(4), V(3), V(2), V(1), V(5), V(6)])
