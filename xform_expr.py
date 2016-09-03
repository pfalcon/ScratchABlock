from core import VALUE, ADDR, MEM, EXPR


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
    if isinstance(expr, VALUE):
        return VALUE(-expr.val, expr.base)
    assert 0


def expr_sub_to_add(e):
    if isinstance(e, EXPR) and len(e.args) == 2:
        if e.op == "-" and isinstance(e.args[1], VALUE):
            return EXPR("+", [e.args[0], expr_neg(e.args[1])])
