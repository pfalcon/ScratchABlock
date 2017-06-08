from core import *


# Capturing var
class V:

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return "V(%r)" % self.name


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
            if ex.op == pat.op and len(ex.args) == len(pat.args):
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


def simplify(ex):
    for pat, prod in RULES:
        #print("Trying", pat)
        try:
            ctx = uni(ex, pat)
        except Failed:
            #print("Failed")
            continue
        return prod(ctx)


if __name__ == "__main__":
    ex = EXPR("-", REG("a1"), REG("a1"))
    ex = EXPR("^", REG("a1"), REG("a1"))
    ex = EXPR("^", REG("a1"), VALUE(1))
    print(simplify(ex))
