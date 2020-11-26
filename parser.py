import sys
import string
from itertools import permutations
from graph import Graph
from core import *


class ParseError(Exception):
    pass

class UndefinedLabel(ParseError):
    pass


class Lexer:

    def __init__(self, l):
        self.l = l
        self.ws()

    def error(self, msg):
        assert False, msg

    def peek(self):
        if not self.l:
            return self.l
        return self.l[0]

    def eol(self):
        return not self.l

    def match(self, tok):
        if not self.l.startswith(tok):
            return False

        word = tok[0] in string.ascii_letters
        rest = self.l[len(tok):]
        if rest and word:
            if rest[0] not in string.whitespace:
                return False
        self.l = rest
        self.ws()
        return True

    def match_till(self, tok):
        res = ""
        while self.l and not self.l.startswith(tok):
            res += self.l[0]
            self.l = self.l[1:]
        return res

    def match_bracket(self, open_b, close_b):
        self.expect(open_b)
        level = 1
        res = ""
        while self.l and level:
            if self.match(open_b):
                level += 1
            elif self.match(close_b):
                level -= 1
            else:
                res += self.l[0]
                self.l = self.l[1:]
        return res

    def expect(self, tok):
        if not self.match(tok):
            self.error("Expected: %s, buffer: %s" % (tok, self.l))

    def ws(self):
        while self.l and self.l[0] == " ":
            self.l = self.l[1:]

    def rest(self):
        return self.l.rstrip()

    def word(self):
        w = ""
        while self.l and self.l[0] in (string.ascii_letters + string.digits + "_."):
            w += self.l[0]
            self.l = self.l[1:]
        return w

    def isident(self):
        return self.l[0] in string.ascii_letters + "_"

    def isdigit(self):
        return self.l[0] in string.digits

    def ident(self):
        assert self.isident(), repr(self.l)
        return self.word()

    def num(self):
        assert self.isdigit(), repr(self.l)
        base = 10
        if self.l.startswith("0x"):
            base = 16
        return int(self.word(), 0), base


class Parser:

    def __init__(self, fname):
        self.fname = fname
        self.expect_line_addr = None
        self.cfg = Graph()
        self.labels = {}
        self.curline = -1
        self.script = []
        self.pass_no = None

    def error(self, msg):
        print("%s:%d: %s" % (self.fname, self.curline + 1, msg))
        sys.exit(1)

    def parse_cond(self, lex):
        lex.expect("(")
        if lex.match("!"):
            arg1 = self.parse_expr(lex)
            cond = "=="
            arg2 = VALUE(0, 10)
        else:
            arg1 = self.parse_expr(lex)
            lex.ws()
            if lex.peek() == ")":
                cond = "!="
                arg2 = VALUE(0, 10)
            else:
                matched = False
                for cond in ("==", "!=", ">=", "<=", ">", "<"):
                    if lex.match(cond):
                        matched = True
                        break
                if not matched:
                    self.error("Expected a comparison operator: " + lex.l)
                arg2 = self.parse_expr(lex)
        lex.expect(")")
        return COND(arg1, cond, arg2)


    # Get line from a file, expanding any "macro-like" features,
    # like "if (cond) $r0 = $r1"
    def get_expand_line(self, f):
        while True:
            l = f.readline()
            if not l:
                return [(None, None)]
            self.curline += 1
            l = l.rstrip()
            if not l:
                continue

            if l[0] == "#":
                if self.pass_no == 1:
                    l = l[1:]
                    if l.startswith("xform: "):
                        self.script.append(l.split(None, 1))
                    elif l.startswith("xform_bblock: "):
                        self.script.append(l.split(None, 1))
                continue

            if self.expect_line_addr is None:
                self.expect_line_addr = self.detect_addr_field(l)

            if self.expect_line_addr:
                addr, l = l.split(" ", 1)
            else:
                addr = str(self.curline)
            l = l.lstrip()

            if l.startswith("if "):
                # May need to expand "if macro"
                lex = Lexer(l)
                lex.expect("if")
                c = self.parse_cond(lex)
                rest = lex.rest()
                if not lex.match("goto"):
                    out = [
                        (addr, "if %s goto %s.1.cond" % (str(c.neg()), addr)),
                        (addr + ".0", rest),
                        (addr + ".1", addr + ".1.cond:"),
                    ]
                    return out

            return [(addr, l)]

    def parse_labels(self):
        self.pass_no = 1
        self.curline = 0
        with open(self.fname) as f:
            l = ""
            while l is not None:
                for addr, l in self.get_expand_line(f):
                    if l is None:
                        break
                    if l[-1] == ":":
                        if not self.labels:
                            # First label is function name
                            self.cfg.name = l[:-1]
                        self.labels[l[:-1]] = addr

    def parse_reg(self, lex):
        lex.expect("$")
        return REG(lex.ident())

    def parse_arglist(self, lex):
        args = []
        lex.expect("(")
        while not lex.match(")"):
            comm = ""
            if lex.match("/*"):
                comm = "/*" + lex.match_till("*/") + "*/"
                lex.expect("*/")
            a = self.parse_expr(lex)
            assert a, (repr(a), repr(lex.l))
            a.comment = comm
            args.append(a)
            if lex.match(","):
                pass
        return args

    def parse_expr(self, lex):
        if lex.match("*"):
            lex.expect("(")
            type = lex.ident()
            lex.expect("*")
            lex.expect(")")
            offset = 0
            if lex.match("("):
                base = self.parse_reg(lex)
                lex.ws()
                lex.expect("+")
                lex.ws()
                offset = lex.num()[0]
                lex.expect(")")
            else:
                base = self.parse_reg(lex)
            if offset == 0:
                return MEM(type, base)
            return MEM(type, EXPR("+", [base, VALUE(offset)]))
        elif lex.peek() == "$":
            return self.parse_reg(lex)
        elif lex.isdigit():
            return VALUE(*lex.num())
        elif lex.match("-"):
            assert lex.isdigit()
            n, base = lex.num()
            return VALUE(-n, base)
        elif lex.isident():
            id = lex.ident()
            if lex.peek() == "(":
                return SFUNC(id)
            else:
                return ADDR(id)
        else:
            return None
            assert False, "Cannot parse: " + repr(lex.l)

    def get_label(self, label):
        try:
            return self.labels[label]
        except KeyError:
            raise UndefinedLabel(label)

    def label_from_addr(self, addr):
        labels = list(filter(lambda x: x[1] == addr, self.labels.items()))
        if not labels:
            return addr
        return labels[0][0]

    def parse_inst(self, l):
        lex = Lexer(l)
        if lex.match("goto"):
            return Inst(None, "goto", [ADDR(self.get_label(lex.rest()))])
        if lex.match("call"):
            return Inst(None, "call", [self.parse_expr(lex)])
        if lex.match("if"):
            c = self.parse_cond(lex)
            lex.expect("goto")
            return Inst(None, "if", [c, ADDR(self.get_label(lex.rest()))])
        if lex.match("return"):
            args = []
            while not lex.eol():
                a = self.parse_expr(lex)
                args.append(a)
                if not lex.eol():
                    lex.expect(",")
            return Inst(None, "return", args)
        dest = self.parse_expr(lex)
        if not dest:
            return Inst(None, "LIT", [l])
        if isinstance(dest, SFUNC):
            args = self.parse_arglist(lex)
            return Inst(None, "SFUNC", [dest] + args)

        def make_assign_inst(dest, op, args):
            #return Inst(dest, op, args)
            return Inst(dest, "=", [EXPR(op, args)])

        lex.ws()
        if lex.match("&="):
            lex.ws()
            src = self.parse_expr(lex)
            return make_assign_inst(dest, "&", [dest, src])
        elif lex.match("|="):
            lex.ws()
            src = self.parse_expr(lex)
            return make_assign_inst(dest, "|", [dest, src])
        elif lex.match("^="):
            lex.ws()
            src = self.parse_expr(lex)
            return make_assign_inst(dest, "^", [dest, src])
        elif lex.match("+="):
            lex.ws()
            src = self.parse_expr(lex)
            return make_assign_inst(dest, "+", [dest, src])
        elif lex.match("-="):
            lex.ws()
            src = self.parse_expr(lex)
            return make_assign_inst(dest, "-", [dest, src])
        elif lex.match("*="):
            lex.ws()
            src = self.parse_expr(lex)
            return make_assign_inst(dest, "*", [dest, src])
        elif lex.match("/="):
            lex.ws()
            src = self.parse_expr(lex)
            return make_assign_inst(dest, "/", [dest, src])
        elif lex.match("%="):
            lex.ws()
            src = self.parse_expr(lex)
            return make_assign_inst(dest, "%", [dest, src])
        elif lex.match(">>="):
            lex.ws()
            src = self.parse_expr(lex)
            return make_assign_inst(dest, ">>", [dest, src])
        elif lex.match("<<="):
            src = self.parse_expr()
            return make_assign_inst(dest, "<<", [dest, src])
        elif lex.match("="):
            lex.ws()
            src = self.parse_expr(lex)
            assert src, repr(lex.l)
            if isinstance(src, SFUNC):
                args = self.parse_arglist(lex)
                return Inst(dest, "SFUNC", [src] + args)
            lex.ws()
            if lex.eol():
                return Inst(dest, "=", [src])
            else:
                for op in ("+", "-", "*", "/", "&", "|", "^", "<<", ">>"):
                    if lex.match(op):
                        src2 = self.parse_expr(lex)
                        return make_assign_inst(dest, op, [src, src2])
                assert 0
        else:
            assert False, repr(lex.l)


    def detect_addr_field(self, l):
        # Autodetect whether there's address as first field
        # of line or not.
        self.expect_line_addr = False
        if l[0].isdigit():
            # Can be either label or address
            if l[-1] == ":":
                if " " in l:
                    return True
            else:
                return True
        return False


    def _parse_bblocks(self):
        with open(self.fname) as f:
            block = None
            last_block = None

            l = ""
            while l is not None:
                for addr, l in self.get_expand_line(f):
                    if l is None:
                        break

                    #print(addr, l)
                    l = l.split(";", 1)[0]
                    l = l.strip()
                    if not l:
                        continue

                    if l[-1] == ":":
                        # label
                        if block is not None:
                            last_block = block
                        block = BBlock(addr)
                        block.cfg = self.cfg
                        block.label = l[:-1]
                        self.cfg.add_node(addr, val=block)
                        continue
                    elif block is None:
                        block = BBlock(addr)
                        block.cfg = self.cfg
                        self.cfg.add_node(addr, val=block)


                    if last_block is not None:
                        self.cfg.add_edge(last_block.addr, block.addr)
                        #last_block.end.append(addr)
                        last_block = None

                    inst = self.parse_inst(l)
                    inst.addr = addr

                    if inst.op in ("goto", "if"):
                        cond = None
                        if inst.op == "goto":
                            addr = inst.args[0]
                        else:
                            cond, addr = inst.args
                        addr = addr.addr
                        #print("!", (cond, addr))
                        if addr not in self.cfg:
                            self.cfg.add_node(addr)
                        self.cfg.add_edge(block.addr, addr, cond=cond)
                        if cond:
                            last_block = block
                        else:
                            last_block = None
                        block.add(inst)
                        block = None
                    elif inst.op == "return":
                        block.add(inst)
                        block = None
                        last_block = None
                    else:
                        block.add(inst)

            if last_block:
                print("Warning: function was not properly terminated")
                self.cfg.add_edge(last_block.addr, block.addr)

    def parse_bblocks(self):
        self.pass_no = 2
        self.curline = 0
        try:
            self._parse_bblocks()
        except ParseError as e:
            print("Error: %d: %r" % (self.curline + 1, e))
            raise
            sys.exit(1)

    def parse(self):
        self.parse_labels()
        self.parse_bblocks()
        return self.cfg
