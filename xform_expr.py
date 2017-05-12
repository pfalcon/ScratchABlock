from core import *
import arch


def is_expr_2args(e):
    return is_expr(e) and len(e.args) == 2


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


def add_vals(a, b):
    val = a.val + b.val
    base = max(a.base, b.base)
    return VALUE(val, base)


def expr_neg(expr):
    if is_value(expr):
        return VALUE(-expr.val, expr.base)
    assert 0


def expr_sub_to_add(e):
    if is_expr_2args(e):
        if e.op == "-" and is_value(e.args[1]):
            return EXPR("+", [e.args[0], expr_neg(e.args[1])])


def expr_commutative_normalize(e):
    if e.op not in ("+", "&", "|", "^"):
        return
    e.args.sort()


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
        base = 0
        for a in e.args:
            if is_value(a):
                val = mod_add(val, a.val)
                base = max(base, a.base)
            else:
                new_args.append(a)
        if new_args:
            if val != 0:
                new_args.append(VALUE(val, base))
            if len(new_args) == 1:
                return new_args[0]
            return EXPR("+", new_args)
        else:
            return VALUE(val, base)


def expr_simplify_xor(e):
    if is_expr(e) and e.op == "^":
        assert is_expr_2args(e)

        if e.args[0] == e.args[1]:
            return VALUE(0)

        expr_commutative_normalize(e)
        if is_value(e.args[1]) and e.args[1].val == 0:
            return e.args[0]


def simplify_expr(expr):
    new_expr = expr_xform(expr, expr_associative_add)
    new_expr = expr_xform(new_expr, expr_simplify_add)
    new_expr = expr_xform(new_expr, expr_simplify_xor)
    return new_expr


# Should transform inplace
def simplify_cond(e):
    if is_expr_2args(e.arg1) and e.arg1.op == "+" and is_value(e.arg1.args[1]) and is_value(e.arg2):
        arg1 = e.arg1
        e.arg1 = arg1.args[0]
        e.arg2 = add_vals(expr_neg(arg1.args[1]), e.arg2)
