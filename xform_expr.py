from core import *


def is_expr_2args(e):
    return is_expr(e) and len(e.args)


def expr_xform(e, func):
    """Transform expression using a function. A function is called with
    each recursive subexpression of expression (in depth-first order),
    then with expression itself. A function can either return new expression
    to replace original one with, or None to keep an original (sub)expression.
    """
    if isinstance(e, MEM):
        new = expr_xform(e.expr, func)
        if new:
            e = MEM(e.type, new)
        e = func(e) or e
        return e

    if isinstance(e, EXPR):
        new = [expr_xform(a, func) or a for a in e.args]
        e = EXPR(e.op, new)
        return func(e) or e

    return func(e) or e


def expr_neg(expr):
    if is_value(expr):
        return VALUE(-expr.val, expr.base)
    assert 0


def expr_sub_to_add(e):
    if is_expr_2args(e):
        if e.op == "-" and is_value(e.args[1]):
            return EXPR("+", [e.args[0], expr_neg(e.args[1])])


def expr_associative_add(e):
    "Turn (a + b) + c into a + b + c."
    if is_expr(e) and e.op == "+":
        if is_expr(e.args[0]) and e.args[0].op == "+":
            new_args = e.args[0].args.copy()
            new_args.extend(e.args[1:].copy())
            return EXPR("+", new_args)
