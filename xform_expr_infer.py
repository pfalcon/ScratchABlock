from core import *
from xform_expr import expr_neg


# Capturing var
class V:

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return "V(%r)" % self.name

    def __repr__(self):
        return self.__str__()


class Failed(Exception):
    pass


def _uni(ex, pat, ctx):
#    print("_uni: %r vs %r" % (ex, pat))

    if isinstance(pat, V):
        if pat.name in ctx and ctx[pat.name] != ex:
            raise Failed
        ctx[pat.name] = ex

    elif type(ex) is type(pat):
        if isinstance(ex, EXPR):
            if len(ex.args) == len(pat.args):
                _uni(ex.op, pat.op, ctx)
                for i in range(len(ex.args)):
                    _uni(ex.args[i], pat.args[i], ctx)
            else:
                raise Failed
        elif isinstance(ex, MEM):
            if ex.type == pat.type:
                _uni(ex.expr, pat.expr, ctx)
            else:
                raise Failed
        elif isinstance(ex, REG):
            _uni(ex.name, pat.name, ctx)
        elif isinstance(ex, ADDR):
            _uni(ex.addr, pat.addr, ctx)
        elif isinstance(ex, VALUE):
            _uni(ex.val, pat.val, ctx)
        else:
            if ex == pat:
                return True
            raise Failed(str((ex, pat)))

    else:
        raise Failed


def uni(ex, pat):
    ctx = {}
    _uni(ex, pat, ctx)
    return ctx

RULES = []

RULES.append((
    EXPR("-", V("x"), V("x")),
    lambda W: VALUE(0)
))

RULES.append((
    EXPR("^", V("x"), V("x")),
    lambda W: VALUE(0)
))

RULES.append((
    EXPR("+", V("x"), VALUE(0)),
    lambda W: W["x"]
))

RULES.append((
    EXPR("^", V("x"), VALUE(0)),
    lambda W: W["x"]
))

RULES.append((
    EXPR("&", VALUE(V("x1")), VALUE(V("x2"))),
    lambda W: VALUE(W["x1"] & W["x2"])
))

RULES.append((
    EXPR("-", VALUE(V("x1")), VALUE(V("x2"))),
    lambda W: VALUE(W["x1"] - W["x2"])
))

RULES.append((
    EXPR(V("rel_op"), EXPR("+", V("x1"), V("x2")), VALUE(0)),
    lambda W: W["rel_op"] in ("==", "!=", "<", "<=", ">=", ">"),
    lambda W: EXPR(W["rel_op"], W["x1"], expr_neg(W["x2"]))
))

RULES.append((
    EXPR("!", EXPR(V("rel_op"), V("x1"), V("x2"))),
    lambda W: W["rel_op"] in ("==", "!=", "<", "<=", ">=", ">"),
    lambda W: EXPR(COND.NEG[W["rel_op"]], W["x1"], W["x2"])
))


def simplify(ex):
    for r in RULES:
        pat = r[0]
        if len(r) == 2:
            test = None
            prod = r[1]
        else:
            test = r[1]
            prod = r[2]
        #print("Trying", repr(pat))
        try:
            ctx = uni(ex, pat)
            #print("Matched")
            if test:
                if not test(ctx):
                    continue
                #print("Test passed")
        except Failed:
            #print("Failed")
            continue
        return prod(ctx)


if __name__ == "__main__":
    ex = EXPR("-", REG("a1"), REG("a1"))
    ex = EXPR("^", REG("a1"), REG("a1"))
    ex = EXPR("^", REG("a1"), VALUE(1))
    ex = EXPR("==", EXPR("+", REG("a1"), EXPR("NEG", REG("a2"))), VALUE(0))
    ex = EXPR("!=", EXPR("+", REG("a1"), EXPR("NEG", REG("a2"))), VALUE(0))
    ex = EXPR("<", EXPR("+", REG("a1"), EXPR("NEG", REG("a2"))), VALUE(0))
    print(ex, repr(ex))
    print(simplify(ex))
