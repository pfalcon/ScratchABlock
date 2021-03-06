import sys
from graph import Graph
import copy

import utils


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

    def __getitem__(self, i):
        return self.items[i]

    def def_addrs(self, regs_only=True):
        """Return all variable definitions for this basic block,
        as set of (var, inst_addr) pairs. Note that this includes
        multiple entries for the same var, if it is redefined
        multiple times within the basic block.
        """
        defs = set()
        for i in self.items:
            inst_defs = i.defs(regs_only)
            for d in inst_defs:
                defs.add((d, i.addr))
        return defs

    def defs(self, regs_only=True):
        """Return set of all variables defined in this basic block."""
        defs = set()
        for i in self.items:
            defs |= i.defs(regs_only)
        return defs

    def uses(self):
        """Return set of all variables used in this basic block."""
        uses = set()
        for i in self.items:
            uses |= i.uses()
        return uses

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.addr)

    def write(self, stream, indent, s):
        for l in str(s).splitlines():
            stream.write("  " * indent)
            stream.write(l + "\n")

    def dump(self, stream, indent=0, printer=str):
        for s in self.items:
            out = printer(s)
            if out is not None:
                self.write(stream, indent, out)

TYPE_SORT = ("REG", "ADDR", "MEM", "EXPR", "COND", "VALUE")

def type_sort(t):
    return TYPE_SORT.index(t.__name__)

# Helper predicates for types below

def is_value(e):
    return isinstance(e, VALUE)

def is_addr(e):
    return isinstance(e, ADDR)

def is_reg(e):
    return isinstance(e, REG)

def is_mem(e):
    return isinstance(e, MEM)

def is_expr(e):
    return isinstance(e, EXPR)

def is_cond(e):
    return isinstance(e, COND)

def is_sfunc(e, name):
    return is_expr(e) and e.args[0] == SFUNC(name)


class SimpleExpr:
    # Something which is a simple expression

    comment = ""
    simple_repr = True

    def regs(self):
        "Get registers referenced by the expression"
        return set()

    def side_effect(self):
        return False

    def __len__(self):
        return 1


class REG(SimpleExpr):

    def __init__(self, name):
        #assert isinstance(name, str)
        self.name = name
        self.signed = False

    def __repr__(self):
        if self.simple_repr:
            return self.__str__()
        type = "REG_S" if self.signed else "REG"
        return self.comment + type + "(%s)" % self.name

    def __str__(self):
        cast = "(i32)" if self.signed else ""
        return self.comment + cast + "$" + str(self.name)

    def __eq__(self, other):
        return type(self) == type(other) and self.name == other.name

    def __lt__(self, other):
        if type(self) != type(other):
            return type_sort(type(self)) < type_sort(type(other))

        n1 = utils.natural_sort_key(self.name)
        n2 = utils.natural_sort_key(other.name)
        return n1 < n2

    def __contains__(self, other):
        return self == other

    def __hash__(self):
        return hash(self.name)

    def regs(self):
        return {self}


class VALUE(SimpleExpr):

    def __init__(self, val, base=16):
        self.val = val
        self.base = base

    def __repr__(self):
        if self.simple_repr:
            return self.__str__()
        return self.comment + "VALUE(%#x)" % self.val

    def __str__(self):
        if isinstance(self.val, int) and self.base == 16:
            val = "%#x" % self.val
        else:
            val = str(self.val)
        return self.comment + val

    def __eq__(self, other):
        return type(self) == type(other) and self.val == other.val

    def __lt__(self, other):
        if type(self) != type(other):
            return type_sort(type(self)) < type_sort(type(other))
        return self.val < other.val

    def __contains__(self, other):
        return self == other

    def __hash__(self):
        return hash(self.val)


class STR(SimpleExpr):

    def __init__(self, s):
        self.val = s

    def __repr__(self):
        if self.simple_repr:
            return self.__str__()
        return self.comment + "STR(%s)" % self.val

    def __str__(self):
        return self.comment + self.val


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

    def __lt__(self, other):
        if type(self) != type(other):
            return type_sort(type(self)) < type_sort(type(other))
        return self.addr < other.addr

    def __contains__(self, other):
        return self == other

    def __hash__(self):
        return hash(self.addr)


class CVAR(SimpleExpr):

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.comment + "CVAR(%s)" % self.name

    def __str__(self):
        return self.comment + self.name

    def __eq__(self, other):
        return type(self) == type(other) and self.name == other.name

    def __hash__(self):
        return hash(self.name)


class MEM(SimpleExpr):
    def __init__(self, type, expr):
        self.type = type
        self.expr = expr

    def __repr__(self):
        return self.comment + "*(%s*)%r" % (self.type, self.expr)

    def __str__(self):
        if isinstance(self.expr, EXPR):
            return self.comment + "*(%s*)(%s)" % (self.type, self.expr)
        else:
            return self.comment + "*(%s*)%s" % (self.type, self.expr)

    def __eq__(self, other):
        return type(self) == type(other) and self.type == other.type and \
            self.expr == other.expr

    def __lt__(self, other):
        if type(self) == type(other):
            return self.expr < other.expr
        return type_sort(type(self)) < type_sort(type(other))

    def __contains__(self, other):
        if other == self:
            return True
        return other in self.expr

    def __hash__(self):
        return hash(self.type) ^ hash(self.expr)

    def regs(self):
        return self.expr.regs()


class SFIELD(SimpleExpr):

    def __init__(self, type, addr, field):
        self.type = type
        self.addr = addr
        self.field = field

    def __repr__(self):
        return self.comment + "SFIELD(%s, %s, %s)" % (self.type, self.addr, self.field)

    def __str__(self):
        return self.comment + "((%s*)%s)->%s" % (self.type, self.addr, self.field)


class SFUNC(SimpleExpr):

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "(SFUNC)%s" % (self.name)

    def __str__(self):
        return "%s" % self.name

    def __eq__(self, other):
        return type(self) == type(other) and self.name == other.name

    def __contains__(self, other):
        return False

    def __hash__(self):
        return hash(self.name)


class TYPE(SimpleExpr):

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "(TYPE)%s" % (self.name)

    def __str__(self):
        return "%s" % self.name

    def __eq__(self, other):
        return type(self) == type(other) and self.name == other.name

    def __contains__(self, other):
        return False

    def __hash__(self):
        return hash(self.name)

    def bitsize(self):
        assert self.name[0] in ("i", "u")
        return int(self.name[1:])


class EXPR:
    "A recursive expression."
    def __init__(self, op, *args):
        self.op = op
        if isinstance(args[0], list):
            args = args[0]
        else:
            args = list(args)
        self.args = args

    def __repr__(self):
        return "EXPR(%s%s)" % (self.op, self.args)

    @staticmethod
    def preced(e):
        if is_expr(e):
            # See e.g. http://en.cppreference.com/w/c/language/operator_precedence
            return {
                "+=": 14, "-=": 14, "*=": 14, "/=": 14, "%=": 14,
                "<<=": 14, ">>=": 14, "&=": 14, "|=": 14, "^=": 14,
                "||": 12, "&&": 11,
                "|": 10, "^": 9, "&": 8,
                "==": 7, "!=": 7,
                ">": 6, "<": 6, ">=": 6, "<=": 6,
                "<<": 5, ">>": 5,
                "+": 4, "-": 4,
                "*": 3, "/": 3, "%": 3,
                # All the below is highest precedence
                "CAST": 1, "SFUNC": 1, "NEG": 1, "!": 1,
            }[e.op]
        return 1

    # Render this expr's arg, wrapped in parens if needed
    @staticmethod
    def strarg(expr, arg):
        if isinstance(arg, (set, frozenset)):
            s = utils.repr_stable(arg)
        else:
            s = str(arg)
        preced_my = EXPR.preced(expr)
        preced_arg = EXPR.preced(arg)
        full_assoc = expr.op in {"+", "*", "&", "^", "|"}
        if preced_arg == preced_my and full_assoc:
            # Render repeated fully associative operators without extra parens
            pass
        elif preced_arg > preced_my or (preced_arg == preced_my and preced_arg != 1):
            # Otherwise, if precedence rules require parens, render them, unless
            # the arg is a unary/primary term
            s = "(%s)" % s
        else:
            # Parens would not be required per the precedence rules, but
            # handle common cases of confusing precedence in C, where parens
            # are usually suggested.
            if expr.op in ("&", "^", "|") and preced_arg != 1:
                # Any binary op subexpression of bitwise ops in parens
                s = "(%s)" % s
            elif expr.op in ("<<", ">>") and preced_arg != 1:
                # Any binary op subexpression of shift in parens
                s = "(%s)" % s
        return s

    def __str__(self):
        if not SimpleExpr.simple_repr:
            return self.__repr__()

        if self.op == "SFUNC":
            return str(self.args[0]) + "(" + ", ".join([str(a) for a in self.args[1:]]) + ")"
        if self.op == "CAST":
            return "(" + str(self.args[0]) + ")" + self.strarg(self, self.args[1])

        DICT = {
            "NEG": "-",
            "!": "!",
        }
        if self.op in DICT:
            assert len(self.args) == 1
            s = DICT [self.op]
            return s + self.strarg(self, self.args[0])

        l = [self.strarg(self, self.args[0])]
        for a in self.args[1:]:
            if self.op == "+" and is_value(a) and a.val < 0:
                l.append("-")
                a = VALUE(-a.val, a.base)
            else:
                l.append(self.op)
            l.append(self.strarg(self, a))
        return " ".join(l)

    def __eq__(self, other):
        return type(self) == type(other) and self.op == other.op and self.args == other.args

    def __lt__(self, other):
        if type(self) == type(other):
            return str(self) < str(other)
        return type_sort(type(self)) < type_sort(type(other))

    def __contains__(self, other):
        if other == self:
            return True
        for a in self.args:
            if other in a:
                return True
        return False

    def __hash__(self):
        return hash(self.op) ^ hash(tuple(self.args))

    def __len__(self):
        # One for operation itself
        l = 1
        for a in self.args:
            l += len(a)
        return l

    def regs(self):
        r = set()
        for a in self.args:
            r |= set(a.regs())
        return r

    uses = regs

    def defs(self, regs_only=True):
        assert not self.side_effect()
        return set()

    def side_effect(self):
        if self.op == "SFUNC":
            return self.args[0].name not in {
                "BIT", "abs", "bitfield", "count_leading_zeroes",
                "phi",
            }
        return False

    def foreach_subexpr(self, func):
        # If func returned True, it means it handled entire subexpression,
        # so we don't recurse into it.
        # Note that this function recurses only within EXPR tree, it doesn't
        # recurse e.g. inside MEM.
        if func(self):
            return
        for a in self.args:
            if is_expr(a):
                a.foreach_subexpr(func)
            else:
                func(a)


class Inst:

    trail = ""
    show_addr = False
    show_comments = True
    annotate_calls = False
    comment = "//"

    def __init__(self, dest, op, args, addr=None):
        self.op = op
        self.dest = dest
        self.args = args
        self.addr = addr
        self.comments = {}

    def jump_addr(self):
        "If instruction may transfer control, return jump address(es), otherwise return None."
        if self.op in ("call", "goto"):
            if isinstance(self.args[0], ADDR):
                return self.args[0].addr
        if self.op == "if":
            res = []
            for i in range(0, len(self.args), 2):
                if isinstance(self.args[i + 1], ADDR):
                    res.append(self.args[i + 1].addr)
            if len(res) == 1:
                return res[0]
            return res
        return None

    def side_effect(self):
        if self.op == "call":
            return True
        if self.op in ("=", "SFUNC"):
            assert len(self.args) == 1, self.args
            return self.args[0].side_effect()
        return False


    def uses(self, cfg=None):
        # Avoid circular import. TODO: fix properly
        import arch
        import progdb

        """Return set of all registers used by this instruction. Function
        calls (and maybe SFUNCs) require special treatment."""
        if self.op == "call":
            addr = self.args[0]
            uses = addr.regs()
            if isinstance(addr, ADDR):
                # Direct call with known address
                addr = addr.addr
                if addr in progdb.FUNC_DB and "params" in progdb.FUNC_DB[addr]:
                    return uses | progdb.FUNC_DB[addr]["params"]

            # Indirect call or not params in funcdb
            # TODO: need to allow saving callsite info in funcdb
            return uses | arch.call_params(addr)

        if self.op == "return":
            if not self.args:
                return arch.ret_uses(cfg)

        uses = set()
        for a in self.args:
            for r in a.regs():
                uses.add(r)
        if is_mem(self.dest):
            for r in self.dest.regs():
                uses.add(r)
        return uses


    def defs(self, regs_only=True, cfg=None):
        # Avoid circular import. TODO: fix properly
        import arch
        import progdb
        """Return set of all registers defined by this instruction. Function
        calls (and maybe SFUNCs) require special treatment."""
        if self.op == "call":
            addr = self.args[0]
            if isinstance(addr, ADDR):
                # Direct call with known address
                addr = addr.addr
                if addr in progdb.FUNC_DB and "modifieds" in progdb.FUNC_DB[addr]:
                    return progdb.FUNC_DB[addr]["modifieds"]

            # Indirect call or not params in funcdb
            # TODO: need to allow saving callsite info in funcdb
            return arch.call_defs(addr)

        defs = set()
        if self.dest:
            if not regs_only or isinstance(self.dest, REG):
                defs.add(self.dest)
        return defs


    def foreach_subexpr(self, func):
        def do(arg):
            if arg:
                if is_expr(arg) or is_cond(arg):
                    arg.foreach_subexpr(func)
                else:
                    func(arg)

        do(self.dest)
        for a in self.args:
            do(a)


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
        if not SimpleExpr.simple_repr:
            return self.__repr__()

        comments = self.comments.copy()

        addr = ""
        if self.show_addr:
            addr = "/*%s*/ " % self.addr

        if self.op == "LIT":
            return addr + self.args[0]

        s = ""
        if self.show_comments and "org_inst" in comments:
            s = self.comment + " " + str(comments.pop("org_inst")) + " "

        s = addr + s

        if self.op == "call" and self.annotate_calls:
            comments["uses"] = sorted(self.uses())
            comments["defs"] = sorted(self.defs())

        tail = self.trail
        if self.show_comments and comments:
            tail += " " + self.comment + " " + utils.repr_stable_dict(comments)

        if self.op == "return":
            args = ", ".join([str(a) for a in self.args])
            if args:
                args = " " + args
            return s + self.op + args + tail
        if self.op in ("goto", "call"):
            return s + "%s %s" % (self.op, self.args[0]) + tail
        if self.op == "if":
            joined = ", ".join(["%s goto %s" % (self.args[i] or "else", self.args[i + 1]) for i in range(0, len(self.args), 2)])
            return s + "if " + joined + tail

        if self.op == "DEAD":
            return s + "(dead)" + tail

        if self.op == "SFUNC":
            assert self.dest is None
            assert len(self.args) == 1, repr(self.args)
            return s + str(self.args[0]) + tail

        assert self.op == "=", repr(self.op)
        assert len(self.args) == 1, (self.op, repr(self.args))

        if self.op == "=" and not is_expr(self.args[0]):
            s += "%s = %s" % (self.dest, self.args[0])
        else:
            e = copy.copy(self.args[0])
            args = e.args
            op = e.op
            if not (op == "!" or op[0].isalpha()):
                # Infix operator
                assert len(args) >= 2, repr(args)
                if self.dest == args[0]:
                    s += "%s %s= " % (self.dest, op)
                    # Render operator as a compound statement operator
                    # (lowest priority, no extra parens).
                    e.op += "="
                    e.args = args[1:]
                else:
                    s += "%s = " % self.dest
            else:
                if self.dest is not None:
                    s += "%s = " % self.dest
            s += "%s" % e

        s += tail
        return s


    def __eq__(self, other):
        return self.op == other.op and self.dest == other.dest and self.args == other.args


class COND:
    """This class is a container of EXPR used as a condition in the
    'if (cond) goto' statement. It's needed because the same condition
    is used both in the Inst representing such a statement and a lebel
    of a CFG edge connecting basic blocks. If condition is updated,
    e.g. while transforming its Inst, the change should be mirrored
    to the CFG edge. Using COND class, this can be easily achieved:
    the same COND instance is referenced both in Inst and edge, and
    we can freely update or even completely replace EXPR it contains,
    while both users will stay up to date.
    """

    NEG = {
        "==": "!=",
        "!=": "==",
        ">":  "<=",
        "<":  ">=",
        ">=": "<",
        "<=": ">",
        "in": "not in",
    }

    SWAP = {
        "==": "==",
        "!=": "!=",
        ">":  "<",
        "<":  ">",
        ">=": "<=",
        "<=": ">=",
    }

    def __init__(self, expr):
        self.expr = expr

    def neg(self):
        op = self.expr.op
        if op in self.NEG:
            return self.__class__(EXPR(self.NEG[op], self.expr.args))
        elif op == "!":
            return self.__class__(self.expr.args[0])
        else:
            return self.__class__(EXPR("!", self.expr))

    def swap(self):
        "Swap arguments in-place."
        self.expr.args[0], self.expr.args[1] = self.expr.args[1], self.expr.args[0]
        self.expr.op = self.SWAP[self.expr.op]

    def normalize(self):
        if is_value(self.expr.args[0]) and not is_value(self.expr.args[1]):
            self.swap()

    def is_relation(self):
        return is_expr(self.expr) and self.expr.op in self.NEG

    def list(self):
        return [self]

    def __str__(self):
        return "(%s)" % self.expr

    def __repr__(self):
#        if self.op in ("in", "not in"):
#            return "COND(%r %s %s)" % (self.arg1, self.op, utils.repr_stable(self.arg2))
        return "COND(%r)" % self.expr

    def __eq__(self, other):
        return type(self) == type(other) and self.expr == other.expr

    def __contains__(self, other):
        return other in self.expr

    def __hash__(self):
        return hash(self.expr) ^ hash(self.__class__)

    def regs(self):
        return self.expr.regs()

    def defs(self, regs_only=True):
        return self.expr.defs(regs_only)

    def uses(self):
        return self.expr.uses()

    def foreach_subexpr(self, func):
        self.expr.foreach_subexpr(func)


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
    res = ", ".join(res)
    if unk:
        res += " UNK: " + ",".join(unk)
    return "{" + res + "}"


class CFGPrinter:
    """Print BBlocks in a CFG. Various printing params can be overriden
    via methods."""

    header_reg_prefix = "$"
    addr_in_header = False

    def __init__(self, cfg, stream=sys.stdout):
        self.cfg = cfg
        self.stream = stream
        # Current bblock addr
        self.addr = 0
        # Current CFG node properties
        self.node_props = None
        # Current BBlock
        self.bblock = None
        # Current BBlock properties
        self.bblock_props = None
        self.inst_printer = str
        self.no_dead = False

    def bblock_order(self):
        "Return iterator over bblocks to be printed."
        return self.cfg.iter_sorted_nodes()

    def print_graph_header(self):
        if self.cfg.props:
            print("// Graph props:", file=self.stream)
            for k in sorted(self.cfg.props.keys()):
                v = self.cfg.props[k]
                v = utils.repr_stable(v)
                print("//  %s: %s" % (k, v), file=self.stream)
            print(file=self.stream)


    def print_header(self):
        if self.addr_in_header:
            print("// %s" % self.addr, file=self.stream)
        print("// Predecessors: %s" % sorted(self.cfg.pred(self.addr)), file=self.stream)

        if self.node_props:
            print("// Node props:", file=self.stream)
            for k in sorted(self.node_props.keys()):
                v = self.node_props[k]
                v = utils.repr_stable(v)
                v = v.replace("$", self.header_reg_prefix)
                print("//  %s: %s" % (k, v), file=self.stream)

        if self.bblock_props:
            print("// BBlock props:", file=self.stream)

            for k in sorted(self.bblock_props.keys()):
                v = self.bblock_props[k]
                if k.startswith("state_"):
                    v = repr_state(v)
                else:
                    v = utils.repr_stable(v)
                v = v.replace("$", self.header_reg_prefix)
                print("//  %s: %s" % (k, v), file=self.stream)


    def print_trailer(self):
        succ = self.cfg.succ(self.addr)
        exits = [(self.cfg.edge(self.addr, x).get("cond"), x) for x in succ]
        print("Exits:", sorted(exits, key=lambda x: utils.natural_sort_key(str(x))), file=self.stream)


    def print_label(self):
        print("%s:" % self.addr, file=self.stream)

    def print_inst(self, inst):
        if inst.op == "DEAD" and self.no_dead:
            return None
        return self.inst_printer(inst)

    def print_separator(self):
        self.stream.write("\n")

    def print(self):
        self.print_graph_header()
        cnt = 0
        for self.addr, info in self.bblock_order():
            self.node_props = info.copy()
            self.bblock = self.node_props.pop("val")
            self.bblock_props = self.bblock.props
            if cnt > 0:
                self.print_separator()
            self.print_header()
            self.print_label()
            if self.bblock is not None:
                self.bblock.dump(self.stream, 0, self.print_inst)
            else:
                print("   ", self.bblock, file=self.stream)
            self.print_trailer()
            cnt += 1


def dump_bblocks(cfg, stream=sys.stdout, printer=str, no_graph_header=False):
    p = CFGPrinter(cfg, stream)
    p.inst_printer = printer
    if no_graph_header:
        p.print_graph_header = lambda: None
    p.print()
