import sys
from graph import Graph


class BBlock:
    def __init__(self, addr):
        self.addr = addr
        self.l = []

    def add(self, s):
        self.l.append(s)

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.addr)

    def write(self, stream, indent, s):
        stream.write("  " * indent)
        stream.write(str(s) + "\n")

    def dump(self, stream, indent=0):
        for s in self.l:
            self.write(stream, indent, s)


class MEM:
    def __init__(self, type, base, offset=0):
        self.type = type
        self.base = base
        self.offset = offset

    def __str__(self):
        if self.offset == 0:
            return "*(%s*)%s" % (self.type, self.base)
        else:
            return "*(%s*)(%s + %s)" % (self.type, self.base, self.offset)


class Inst:
    def __init__(self, dest, op, args):
        self.op = op
        self.dest = dest
        self.args = args

    def __repr__(self):
        if self.dest is None:
            if self.op == "LIT":
                return self.args[0]
            else:
                return "%s(%s)" % (self.op, self.args)
        else:
            return "%s = %s(%s)" % (self.dest, self.op, self.args)


class SimpleCond:

    NEG = {
        "==": "!=",
        "!=": "==",
        ">":  "<=",
        "<":  ">=",
        ">=": "<",
        "<=": ">",
    }

    def __init__(self, arg1, op, arg2):
        self.arg1 = arg1
        self.op = op
        self.arg2 = arg2

    def neg(self):
        return self.__class__(self.arg1, self.NEG[self.op], self.arg2)

    def list(self):
        return [self]

    def __str__(self):
        return "(%s %s %s)" % (self.arg1, self.op, self.arg2)

    def __repr__(self):
        return "SCond%s" % str(self)


class CompoundCond:

    NEG = {
        "&&": "||",
        "||": "&&",
    }

    def __init__(self, l):
        self.args = l

    def append(self, op, arg2):
        self.args.extend([op, arg2])

    def neg(self):
        return self.__class__([self.NEG[x] if isinstance(x, str) else x.neg() for x in self.args])

    def list(self):
        return self.args

    def __str__(self):
        r = " ".join([str(x) for x in self.args])
        return "(" + r + ")"

    def __repr__(self):
        return "CCond%s" % str(self)


def dump_bblocks(cfg):
    for addr, bblock in cfg.iter_sorted_nodes():
        print("\n// Predecessors: %s" % cfg.pred(addr))
        print("%s:" % addr)
        if bblock:
            bblock.dump(sys.stdout)
        else:
            print("   ", bblock)
        succ = cfg.succ(addr)
        print("Exits:", [(cfg.edge(addr, x), x) for x in succ])
