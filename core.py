import sys
from graph import Graph


class BBlock:
    def __init__(self, addr):
        self.addr = addr
        self.items = []

    def add(self, s):
        self.items.append(s)

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.addr)

    def write(self, stream, indent, s):
        stream.write("  " * indent)
        stream.write(str(s) + "\n")

    def dump(self, stream, indent=0, printer=str):
        for s in self.items:
            self.write(stream, indent, printer(s))

class REG:

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "REG(%s)" % self.name

    def __str__(self):
        return "$" + self.name

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

class VALUE:

    def __init__(self, val):
        self.val = val

    def __repr__(self):
        return "VALUE(0x%x)" % self.val

    def __str__(self):
        return "0x%x" % self.val

class ADDR:

    def __init__(self, addr):
        self.addr = addr

    def __repr__(self):
        return "ADDR(%s)" % self.addr

    def __str__(self):
        return self.addr

class MEM:
    def __init__(self, type, base, offset=0):
        self.type = type
        self.base = base
        self.offset = offset

    def __repr__(self):
        if self.offset == 0:
            return "*(%s*)%s" % (self.type, self.base)
        else:
            return "*(%s*)(%s + %s)" % (self.type, self.base, self.offset)

class SFUNC:

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "(SFUNC)%s" % (self.name)

    def __str__(self):
        return "%s" % self.name

class Inst:
    def __init__(self, dest, op, args, addr=None):
        self.op = op
        self.dest = dest
        self.args = args
        self.addr = addr
        self.comments = {}

    def __repr__(self):
        if self.addr is not None:
            s = "/*%s*/ " % self.addr
        if self.dest is None:
            if self.op == "LIT":
                s += self.args[0]
            else:
                s += "%s(%s)" % (self.op, self.args)
        else:
            s += "%s = %s(%s)" % (self.dest, self.op, self.args)
        if self.comments:
            s += " # " + repr(self.comments)
        return s

    def __str__(self):
        if self.dest is None:
            if self.op == "LIT":
                return self.args[0]
            else:
                if self.op in ("goto", "call"):
                    return "%s %s" % (self.op, self.args[0])
                return "%s(%s)" % (self.op, self.args)
        else:
            if self.op == "ASSIGN":
                return "%s = %s" % (self.dest, self.args[0])
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


def dump_bblocks(cfg, stream=sys.stdout, printer=str):
    cnt = 0
    for addr, info in cfg.iter_sorted_nodes():
        bblock = info["val"]
        if cnt > 0:
            stream.write("\n")
        print("// Predecessors: %s" % sorted(cfg.pred(addr)), file=stream)
        if "dfsno" in info:
            print("// DFS#: %d" % info["dfsno"], file=stream)
        print("%s:" % addr, file=stream)
        if bblock:
            bblock.dump(stream, 0, printer)
        else:
            print("   ", bblock, file=stream)
        succ = cfg.succ(addr)
        print("Exits:", [(cfg.edge(addr, x), x) for x in succ], file=stream)
        cnt += 1
