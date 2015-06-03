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

    def expect(self, tok):
        assert self.match(tok), "Expected: %s, buffer: %s" % (tok, self.l)

    def ws(self):
        while self.l and self.l[0] == " ":
            self.l = self.l[1:]

    def rest(self):
        return self.l.rstrip()


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
            c = SimpleCond(lex.match_till(")"), "==", "0")
        else:
            exp = lex.match_till(")")
            arr = exp.split()
            if len(arr) == 1:
                c = SimpleCond(exp, "!=", "0")
            else:
                c = SimpleCond(*arr)
        lex.expect(")")
        return c

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

    def parse_expr(self, lex):
        if lex.match("*"):
            lex.expect("(")
            type = lex.ident()
            lex.expect("*")
            lex.expect(")")
            offset = 0
            if lex.match("("):
                base = lex.ident()
                lex.expect("+")
                offset = lex.num()
                lex.expect(")")
            else:
                base = lex.ident()
            return MEM(type, base, offset)
        else:
            assert False

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
        return Inst(None, "LIT", [l])
#        dest = self.parse_expr(lex)


    def _parse_bblocks(self):
        with open(sys.argv[1]) as f:
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
                    self.cfg.add_node(addr, block)
                    continue
                elif not block:
                    block = BBlock(addr)
                    self.cfg.add_node(addr, block)


                if last_block:
                    self.cfg.add_edge(last_block.addr, block.addr)
                    #last_block.end.append(addr)
                    last_block = None

                inst = self.parse_inst(l)

                if inst.op in ("goto", "if"):
                    cond = None
                    if inst.op == "goto":
                        addr = inst.args[0]
                    else:
                        cond, addr = inst.args
                    #print("!", (cond, addr))
                    if addr not in self.cfg:
                        self.cfg.add_node(addr)
                    self.cfg.add_edge(block.addr, addr, cond)
                    if cond:
                        last_block = block
                    else:
                        last_block = None
                    block = None
                elif inst.op == "return":
                    block.add(inst)
                    last_block = None
                    break
                else:
                    block.add(inst)

            if last_block:
                print("ERROR: function was not properly terminated")

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
