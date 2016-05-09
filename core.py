import sys
import re
from graph import Graph

def natural_sort_key(s):
    arr = re.split("([0-9]+)", s)
    return [int(x) if x.isdigit() else x for x in arr]


class Singleton:

    def __init__(self, n):
        self.n = n

    def __repr__(self):
        return self.n

UNK = Singleton("UNK")
DYN = Singleton("DYN")


class BBlock:
    def __init__(self, addr):
        self.addr = addr
        self.items = []
        self.props = {}

    def add(self, s):
        self.items.append(s)

    def def_addrs(self):
        """Return all variable definitions for this basic block,
        as set of (var, inst_addr) pairs. Note that this includes
        multiple entries for the same var, if it is redefined
        multiple times within the basic block.
        """
        defs = set()
        for i in self.items:
            if i.dest:
                defs.add((i.dest, i.addr))
        return defs

    def defs(self):
        """Return set of all variable defined in this basic block."""
        defs = set()
        for i in self.items:
            if i.dest:
                defs.add(i.dest)
        return defs

    def uses(self):
        """Return set of all variables used in this basic block."""
        uses = set()
        for i in self.items:
            for a in i.args:
                for r in a.regs():
                    uses.add(r)
        return uses

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.addr)

    def write(self, stream, indent, s):
        for l in str(s).splitlines():
            stream.write("  " * indent)
            stream.write(l + "\n")

    def dump(self, stream, indent=0, printer=str):
        for s in self.items:
            self.write(stream, indent, printer(s))

# Helper predicates for types below

def is_value(e):
    return isinstance(e, VALUE)

def is_expr(e):
    return isinstance(e, EXPR)


class SimpleExpr:
    # Something which is a simple expression

    comment = ""
    simple_repr = True

    def reg(self):
        "Get register referenced by the expression"
        return None

class REG(SimpleExpr):

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        if self.simple_repr:
            return self.__str__()
        return self.comment + "REG(%s)" % self.name

    def __str__(self):
        return self.comment + "$" + self.name

    def __eq__(self, other):
        return type(self) == type(other) and self.name == other.name

    def __lt__(self, other):
        if type(self) != type(other):
            return type(self).__name__ < type(other).__name__

        n1 = natural_sort_key(self.name)
        n2 = natural_sort_key(other.name)
        return n1 < n2

    def __hash__(self):
        return hash(self.name)

    def reg(self):
        return self

    def regs(self):
        return [self]


class VALUE(SimpleExpr):

    def __init__(self, val, base=16):
        self.val = val
        self.base = base

    def __repr__(self):
        if self.simple_repr:
            return self.__str__()
        return self.comment + "VALUE(0x%x)" % self.val

    def __str__(self):
        if self.base == 16:
            val = "0x%x" % self.val
        else:
            val = str(self.val)
        return self.comment + val

    def __eq__(self, other):
        return type(self) == type(other) and self.val == other.val

    def __hash__(self):
        return hash(self.val)

    def regs(self):
        return []


class ADDR(SimpleExpr):

    resolver = staticmethod(lambda x: x)

    def __init__(self, addr):
        self.addr = addr

    def __repr__(self):
        return self.comment + "ADDR(%s)" % self.addr

    def __str__(self):
        return self.comment + self.resolver(self.addr)

    def __eq__(self, other):
        return type(self) == type(other) and self.addr == other.addr

    def __hash__(self):
        return hash(self.addr)

class MEM(SimpleExpr):
    def __init__(self, type, base, offset=0):
        self.type = type
        self.base = base
        self.offset = offset

    def __repr__(self):
        if self.offset == 0:
            return self.comment + "*(%s*)%s" % (self.type, self.base)
        else:
            return self.comment + "*(%s*)(%s + 0x%x)" % (self.type, self.base, self.offset)

    def __eq__(self, other):
        return type(self) == type(other) and self.type == other.type and \
            self.base == other.base and self.offset == other.offset

    def __lt__(self, other):
        if type(self) == type(other):
            return (self.base, self.offset) < (other.base, other.offset)
        return type(self).__name__ < type(other).__name__

    def __hash__(self):
        return hash(self.type) ^ hash(self.base) ^ hash(self.offset)

    def reg(self):
        if isinstance(self.base, REG):
            return self.base
        return None

class SFUNC(SimpleExpr):

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "(SFUNC)%s" % (self.name)

    def __str__(self):
        return "%s" % self.name

    def __eq__(self, other):
        return type(self) == type(other) and self.name == other.name


class EXPR:
    "A recursive expression."
    def __init__(self, op, args):
        self.op = op
        self.args = tuple(args)

    def __repr__(self):
        return "EXPR(%s%s)" % (self.op, self.args)

    def __eq__(self, other):
        return type(self) == type(other) and self.op == other.op and self.args == other.args

    def __hash__(self):
        return hash(self.op) ^ hash(self.args)


class Inst:

    trail = ""
    show_comments = True

    def __init__(self, dest, op, args, addr=None):
        self.op = op
        self.dest = dest
        self.args = args
        self.addr = addr
        self.comments = {}

    def jump_addr(self):
        "If instruction may transfer control, return jump address, otherwise return None."
        if self.op in ("call", "goto"):
            assert isinstance(self.args[0], ADDR)
            return self.args[0].addr
        if self.op == "if":
            assert isinstance(self.args[1], ADDR)
            return self.args[1].addr
        return None

    def side_effect(self):
        if self.op == "call":
            return True
        if self.op == "SFUNC":
            return self.args[0] not in ("bitfield",)
        return False

    def __repr__(self):
        comments = self.comments.copy()
        s = ""
        if "org_inst" in comments:
            s = "// " + str(comments.pop("org_inst")) + "\n"
        if self.addr is not None:
            s += "/*%s*/ " % self.addr
        if self.dest is None:
            if self.op == "LIT":
                s += self.args[0]
            else:
                s += "%s(%s)" % (self.op, self.args)
        else:
            if self.op == "=":
                # Simplify repr for assignment
                s += "%s = %s" % (self.dest, self.args)
            else:
                s += "%s = %s(%s)" % (self.dest, self.op, self.args)
        if comments:
            s += " # " + repr(comments)
        return s

    def __str__(self):
        if self.op == "LIT":
            return self.args[0]

        s = ""
        if self.show_comments and "org_inst" in self.comments:
            s = "// " + str(self.comments["org_inst"]) + "\n"

        if self.op == "return":
            args = ", ".join([str(a) for a in self.args])
            if args:
                args = " " + args
            return s + self.op + args + self.trail
        if self.op in ("goto", "call"):
            return s + "%s %s" % (self.op, self.args[0]) + self.trail
        if self.op == "if":
            return s + "if %s goto %s" % (self.args[0], self.args[1]) + self.trail

        if self.op == "=":
            s += "%s = %s" % (self.dest, self.args[0])
        else:
            args = self.args
            op = self.op
            if not op[0].isalpha():
                # Infix operator
                assert len(args) == 2
                if self.dest == args[0]:
                    s += "%s %s= %s" % (self.dest, op, args[1])
                else:
                    s += "%s = %s %s %s" % (self.dest, args[0], op, args[1])
            else:
                if self.dest is not None:
                    s += "%s = " % self.dest
                if op == "SFUNC":
                    op = args[0]
                    args = args[1:]
                args = ", ".join([str(a) for a in args])
                s += "%s(%s)" % (op, args)

        return s + self.trail

    def __eq__(self, other):
        return self.op == other.op and self.dest == other.dest and self.args == other.args


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
        return "SCond(%r %s %r)" % (self.arg1, self.op, self.arg2)

    def __eq__(self, other):
        return type(self) == type(other) and self.op == other.op and self.arg1 == other.arg1 and self.arg2 == other.arg2

    def __hash__(self):
        return hash(self.op) ^ hash(self.arg1) ^ hash(self.arg2)

    def regs(self):
        return [x for x in (self.arg1, self.arg2) if isinstance(x, REG)]


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

def repr_state(state):
    res = []
    unk = []
    for k, v in sorted(state.items()):
        if v == UNK:
            unk.append(str(k))
        else:
            res.append("%s=%s" % (k, v))
    res = " ".join(res)
    if unk:
        res += " UNK: " + ",".join(unk)
    return res


class CFGPrinter:
    """Print BBlocks in a CFG. Various printing params can be overriden
    via methods."""

    def __init__(self, cfg, stream=sys.stdout):
        self.cfg = cfg
        self.stream = stream
        # Current bblock addr
        self.addr = 0
        # Current CFG node properties
        self.node_props = None
        # Current BBlock
        self.bblock = None
        self.inst_printer = str

    def bblock_order(self):
        "Return iterator over bblocks to be printed."
        return self.cfg.iter_sorted_nodes()

    def print_header(self):
        print("// Predecessors: %s" % sorted(self.cfg.pred(self.addr)), file=self.stream)

        if "dfsno" in self.node_props:
            print("// DFS#: %d" % self.node_props.pop("dfsno"), file=self.stream)

        if "uses" in self.bblock.props:
            print("// Uses: %s" % sorted(self.bblock.props["uses"].items()), file=self.stream)
        if "defs" in self.bblock.props:
            print("// Defs: %s" % sorted(self.bblock.props["defs"].items()), file=self.stream)
        if "in_state" in self.bblock.props:
            print("// InState : %s" % repr_state(self.bblock.props["in_state"]), file=self.stream)
        if "out_state" in self.bblock.props:
            print("// OutState: %s" % repr_state(self.bblock.props["out_state"]), file=self.stream)

        if self.node_props:
            print("// " + repr(sorted(self.node_props.items())), file=self.stream)


    def print_trailer(self):
        succ = self.cfg.succ(self.addr)
        print("Exits:", [(self.cfg.edge(self.addr, x).get("cond"), x) for x in succ], file=self.stream)


    def print_label(self):
        print("%s:" % self.addr, file=self.stream)


    def print_separator(self):
        self.stream.write("\n")


    def print(self):
        cnt = 0
        for self.addr, info in self.bblock_order():
            self.node_props = info.copy()
            self.bblock = self.node_props.pop("val")
            if cnt > 0:
                self.print_separator()
            self.print_header()
            self.print_label()
            if self.bblock:
                self.bblock.dump(self.stream, 0, self.inst_printer)
            else:
                print("   ", self.bblock, file=self.stream)
            self.print_trailer()
            cnt += 1


def dump_bblocks(cfg, stream=sys.stdout, printer=str):
    p = CFGPrinter(cfg, stream)
    p.inst_printer = printer
    p.print()
