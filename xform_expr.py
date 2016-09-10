from core import *
import arch


def is_expr_2args(e):
    return is_expr(e) and len(e.args)


def mod_add(a, b, bits=arch.BITNESS):
    "Addition modulo power of 2, but preserve sign."
    s = a + b
    if s < 0:
        return s % 2**bits - 2**bits
    else:
        return s % 2**bits


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


def expr_simplify_add(e):
    if is_expr(e) and e.op == "+":
        new_args = []
        val = 0
        for a in e.args:
            if is_value(a):
                val = mod_add(val, a.val)
            else:
                new_args.append(a)
        if new_args:
            if val != 0:
                new_args.append(VALUE(val))
            if len(new_args) == 1:
                return new_args[0]
            return EXPR("+", new_args)
        else:
            return VALUE(val)
