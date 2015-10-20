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
        assert self.match(tok), "Expected: %s, buffer: %s" % (tok, self.l)

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
        self.cfg = Graph()
        self.labels = {}
        self.curline = -1
        self.script = []

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
                    lex.error("Expected a comparison operator: " + lex.l)
                arg2 = self.parse_expr(lex)
        lex.expect(")")
        return SimpleCond(arg1, cond, arg2)


    def parse_goto(self, s):
        # Return (condition, address)
        left, right = s.strip().split("goto")
        label = right.split()[0]
        try:
            addr = self.labels[label]
        except KeyError:
            raise UndefinedLabel(label)
        #addr = "%08x" % addr
        if not left:
            return (None, addr)
        return (self.parse_cond(left[3:].strip()), addr)

    def parse_labels(self):
        with open(self.fname) as f:
            for i, l in enumerate(f):
                self.curline = i
                l = l.rstrip()
                if l[0] == "#":
                    if l.startswith("#xform: "):
                        self.script.append(l.split(None, 1)[1])
                    continue
                addr, l = l.split(" ", 1)
                #addr = int(addr, 16)
                l = l.lstrip()
                if l[-1] == ":":
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
            return MEM(type, base, offset)
        elif lex.peek() == "$":
            return self.parse_reg(lex)
        elif lex.isdigit():
            return VALUE(*lex.num())
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

    def parse_inst(self, l):
        lex = Lexer(l)
        if lex.match("goto"):
            return Inst(None, "goto", [self.get_label(lex.rest())])
        if lex.match("call"):
            return Inst(None, "call", [lex.rest()])
        if lex.match("if"):
            c = self.parse_cond(lex)
            lex.expect("goto")
            return Inst(None, "if", [c, self.get_label(lex.rest())])
        if lex.match("return"):
            return Inst(None, "return", [])
        dest = self.parse_expr(lex)
        if not dest:
            return Inst(None, "LIT", [l])
        if isinstance(dest, SFUNC):
            args = self.parse_arglist(lex)
            return Inst(None, "SFUNC", [dest.name] + args)

        lex.ws()
        if lex.match("&="):
            lex.ws()
            src = self.parse_expr(lex)
            return Inst(dest, "&", [dest, src])
        elif lex.match("+="):
            lex.ws()
            src = self.parse_expr(lex)
            return Inst(dest, "+", [dest, src])
        elif lex.match("-="):
            lex.ws()
            src = self.parse_expr(lex)
            return Inst(dest, "-", [dest, src])
        elif lex.match(">>="):
            lex.ws()
            src = self.parse_expr(lex)
            return Inst(dest, ">>", [dest, src])
        elif lex.match("="):
            lex.ws()
            src = self.parse_expr(lex)
            assert src
            if isinstance(src, SFUNC):
                args = self.parse_arglist(lex)
                return Inst(dest, "SFUNC", [src.name] + args)
            lex.ws()
            if lex.eol():
                return Inst(dest, "ASSIGN", [src])
            else:
                for op in ("+", "-", "*", "/", "&", "|", "^", "<<", ">>"):
                    if lex.match(op):
                        src2 = self.parse_expr(lex)
                        return Inst(dest, op, [src, src2])
                assert 0
        else:
            assert False, repr(lex.l)


    def _parse_bblocks(self):
        with open(self.fname) as f:
            block = None
            last_block = None
            for i, l in enumerate(f):
                self.curline = i
                l = l.rstrip()
                if l[0] == "#":
                    continue
                addr, l = l.split(" ", 1)
                #addr = int(addr, 16)
                #print((hex(addr), l))
                l = l.split(";", 1)[0]
                l = l.strip()
                if not l:
#                if l[0] == ";":
                    continue

                if l[-1] == ":":
                    # label
                    if block:
                        last_block = block
                    block = BBlock(addr)
                    self.cfg.add_node(addr, val=block)
                    continue
                elif not block:
                    block = BBlock(addr)
                    self.cfg.add_node(addr, val=block)


                if last_block:
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
