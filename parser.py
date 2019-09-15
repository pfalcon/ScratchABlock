import sys
import string
from graph import Graph
from core import *
import yaml


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

    def is_punct(self, c):
        return c in "&|^-+*/%=<>"

    def match(self, tok):
        if not self.l.startswith(tok):
            return False

        is_word = tok[0] in string.ascii_letters
        rest = self.l[len(tok):]
        if rest:
            if is_word and rest[0] not in string.whitespace:
                    return False
            elif self.is_punct(tok[0]) and self.is_punct(rest[0]):
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

    def expect(self, tok, msg=None):
        if not self.match(tok):
            if msg is None:
                msg = "Expected: '%s'" % tok
            raise ParseError(msg, self.l)

    def ws(self):
        while self.l and self.l[0] == " ":
            self.l = self.l[1:]

    def rest(self):
        return self.l.rstrip()

    def word(self):
        w = ""
        while self.l and self.l[0] in (string.ascii_letters + string.digits + "_.$"):
            w += self.l[0]
            self.l = self.l[1:]
        return w

    def isident(self):
        return self.l[0] in string.ascii_letters + "_."

    def isdigit(self):
        return self.l[0] in string.digits

    def ident(self):
        assert self.isident(), repr(self.l)
        w = self.word()
        self.ws()
        return w

    def num(self):
        assert self.isdigit(), repr(self.l)
        base = 10
        if self.l.startswith("0x"):
            base = 16
        w = self.word()
        self.ws()
        return int(w, 0), base

    def skip_comment(self):
        if self.match("/*"):
            self.match_till("*/")
            self.expect("*/")

class Parser:

    def __init__(self, fname):
        self.fname = fname
        self.expect_line_addr = None
        self.cfg = None
        self.labels = {}
        self.curline = -1
        self.script = []
        self.pass_no = None
        self.lex = None

    def error(self, msg):
        print("%s:%d: %s" % (self.fname, self.curline, msg))
        sys.exit(1)

    def parse_cond(self, lex):
        self.lex = lex
        lex.expect("(")
        e = self.parse_expr()
        lex.expect(")")
        return COND(e)

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
                    elif l.startswith("xform_inst: "):
                        self.script.append(l.split(None, 1))
                    elif l.startswith("script: "):
                        self.script.append(l.split(None, 1))
                    elif l.startswith("struct: "):
                        import progdb
                        data = yaml.safe_load(l.split(None, 1)[1])
                        progdb.set_struct_types(data)
                    elif l.startswith("struct_addr: "):
                        import progdb
                        data = yaml.safe_load(l.split(None, 1)[1])
                        data = {(start, start + max(progdb.get_struct_types()[name].keys()) + 4): name for start, name in data.items()}
                        progdb.set_struct_instances(data)
                continue

            if self.expect_line_addr is None:
                self.expect_line_addr = self.detect_addr_field(l)

            if self.expect_line_addr:
                addr, l = l.split(" ", 1)
            else:
                addr = "%04d" % self.curline
            l = l.lstrip()

            if l.startswith("if "):
                # May need to expand "if macro"
                lex = Lexer(l)
                lex.expect("if")
                c = self.parse_cond(lex)
                rest = lex.rest()
                if not lex.match("goto"):
                    # Uncomment to treat as literal line for roundtrip testing
                    #return [(addr, "\x01" + l)]
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
                        self.labels[l[:-1]] = addr

    def parse_reg(self, lex):
        lex.expect("$")
        return REG(lex.ident())

    def parse_arglist(self):
        args = []
        self.lex.expect("(")
        while not self.lex.match(")"):
            comm = ""
            if self.lex.match("/*"):
                comm = "/*" + self.lex.match_till("*/") + "*/"
                self.lex.expect("*/")
            a = self.parse_expr()
            assert a, (repr(a), repr(self.lex.l))
            a.comment = comm
            args.append(a)
            if self.lex.match(","):
                pass
        return args

    def parse_num(self):
        if self.lex.isdigit():
            return VALUE(*self.lex.num())

    def parse_primary(self):
        if self.lex.match("*"):
            self.lex.expect("(", "Dereference requires explicit pointer cast")
            type = self.lex.ident()
            self.lex.expect("*")
            self.lex.expect(")")
            e = self.parse_primary()
            return MEM(type, e)
        elif self.lex.match("("):
            e = self.parse_expr()
            self.lex.expect(")")
            if is_addr(e):
                # If there was identifier, check it for being a type name
                if e.addr in ("i8", "u8", "i16", "u16", "i32", "u32", "i64", "u64"):
                    tp = TYPE(e.addr)
                    e = self.parse_primary()
                    return EXPR("CAST", [tp, e])
            return e
        elif self.lex.peek() == "$":
            return self.parse_reg(self.lex)
        elif self.lex.isdigit():
            return VALUE(*self.lex.num())
        elif self.lex.match("-"):
            e = self.parse_primary()
            if is_value(e):
                return VALUE(-e.val, e.base)
            return EXPR("NEG", [e])
        elif self.lex.match("!"):
            e = self.parse_primary()
            return EXPR("!", [e])
        elif self.lex.isident():
            id = self.lex.ident()
            if self.lex.peek() == "(":
                args = self.parse_arglist()
                return EXPR("SFUNC", [SFUNC(id)] + args)
            else:
                return ADDR(self.labels.get(id, id))
        else:
            self.error("Cannot parse")

    def parse_level(self, operators, next_level):
        e = next_level()
        match = True
        while match:
            match = False
            for op in operators:
                if self.lex.match(op):
                    e2 = next_level()
                    e = EXPR(op, [e, e2])
                    match = True
                    break
        return e

    def parse_mul(self):
        return self.parse_level(("*", "/", "%"), self.parse_primary)

    def parse_add(self):
        return self.parse_level(("+", "-"), self.parse_mul)

    def parse_shift(self):
        return self.parse_level(("<<", ">>"), self.parse_add)

    def parse_lt_gt(self):
        return self.parse_level(("<", "<=", ">=", ">"), self.parse_shift)
    def parse_eq(self):
        return self.parse_level(("==", "!="), self.parse_lt_gt)

    def parse_band(self):
        return self.parse_level(("&",), self.parse_eq)
    def parse_bxor(self):
        return self.parse_level(("^",), self.parse_band)
    def parse_bor(self):
        return self.parse_level(("|",), self.parse_bxor)

    def parse_land(self):
        return self.parse_level(("&&",), self.parse_bor)
    def parse_lor(self):
        return self.parse_level(("||",), self.parse_land)

    def parse_expr(self):
        return self.parse_lor()


    # If there's numeric value, treat it as address. Otherwise, parse expression.
    def parse_local_addr_expr(self):
        if self.lex.isdigit():
            w = self.lex.word()
            return ADDR(self.labels.get(w, w))
        return self.parse_expr()

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
        lex = self.lex = Lexer(l)
        if lex.peek() == ".":
            # Asm directive, ignore
            return None
        if lex.match("db") or lex.match("unk"):
            arg = self.parse_num()
            if arg is None:
                arg = STR(lex.l)
            return Inst(None, "SFUNC", [EXPR("SFUNC", [SFUNC("litbyte"), arg])])
        if lex.match("goto"):
            return Inst(None, "goto", [self.parse_local_addr_expr()])
        if lex.match("call"):
            return Inst(None, "call", [self.parse_expr()])
        if lex.match("if"):
            args = []
            while True:
                if lex.match("else"):
                    c = None
                else:
                    c = self.parse_cond(lex)
                lex.expect("goto")
                label = lex.match_till(",").strip()
                addr = ADDR(self.get_label(label))
                args.extend([c, addr])
                if not lex.match(","):
                    break
            return Inst(None, "if", args)
        if lex.match("return"):
            args = []
            while True:
                lex.skip_comment()
                if lex.eol():
                    break
                a = self.parse_expr()
                args.append(a)
                if not lex.eol():
                    lex.expect(",")
            return Inst(None, "return", args)

        dest = self.parse_expr()
        if not dest:
            return Inst(None, "LIT", [l])

        if is_expr(dest) and isinstance(dest.args[0], SFUNC) and lex.eol():
            return Inst(None, "SFUNC", [dest])

        def make_assign_inst(dest, op, args):
            #return Inst(dest, op, args)
            return Inst(dest, "=", [EXPR(op, args)])

        lex.ws()
        if lex.match("&="):
            lex.ws()
            src = self.parse_expr()
            return make_assign_inst(dest, "&", [dest, src])
        elif lex.match("|="):
            lex.ws()
            src = self.parse_expr()
            return make_assign_inst(dest, "|", [dest, src])
        elif lex.match("^="):
            lex.ws()
            src = self.parse_expr()
            return make_assign_inst(dest, "^", [dest, src])
        elif lex.match("+="):
            lex.ws()
            src = self.parse_expr()
            return make_assign_inst(dest, "+", [dest, src])
        elif lex.match("-="):
            lex.ws()
            src = self.parse_expr()
            return make_assign_inst(dest, "-", [dest, src])
        elif lex.match("*="):
            lex.ws()
            src = self.parse_expr()
            return make_assign_inst(dest, "*", [dest, src])
        elif lex.match("/="):
            lex.ws()
            src = self.parse_expr()
            return make_assign_inst(dest, "/", [dest, src])
        elif lex.match("%="):
            lex.ws()
            src = self.parse_expr()
            return make_assign_inst(dest, "%", [dest, src])
        elif lex.match(">>="):
            lex.ws()
            src = self.parse_expr()
            return make_assign_inst(dest, ">>", [dest, src])
        elif lex.match("<<="):
            src = self.parse_expr()
            return make_assign_inst(dest, "<<", [dest, src])
        elif lex.match("="):
            lex.ws()
            src = self.parse_expr()
            assert src, repr(lex.l)
            if isinstance(src, SFUNC):
                args = self.parse_arglist()
                return Inst(dest, "SFUNC", [src] + args)
            lex.ws()
            if lex.eol():
                return Inst(dest, "=", [src])
            else:
                assert 0, (lex.l, self.curline)
        else:
            assert False, (repr(lex.l), self.curline)


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


    def _parse_bblocks(self, f):
            self.cfg = Graph()
            # TODO: not stored in props to avoid modifying tests
            self.cfg.filename = self.fname
            self.cfg.props["name"] = None
            self.cfg.props["trailing_jumps"] = True
            block = None
            last_block = None

            l = ""
            while l is not None:
                for addr, l in self.get_expand_line(f):
                    if l is None:
                        break
                    if self.should_stop(addr, l):
                        return

                    #print(addr, l)
                    l = l.split(";", 1)[0]
                    l = l.strip()
                    if not l:
                        continue

                    if l[-1] == ":":
                        # label
                        if self.cfg.props["name"] is None:
                            # First label is function name
                            if block is None and self.cfg.is_empty():
                                self.cfg.props["name"] = l[:-1]
                                self.cfg.props["addr"] = addr

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

                    if l[0] == "\x01":
                        inst = Inst(None, "LIT", [l[1:]], addr=addr)
                        block.add(inst)
                        continue

                    inst = self.parse_inst(l)
                    if not inst:
                        continue
                    inst.addr = addr

                    if inst.op in ("goto", "if", "call"):
                        if inst.op != "if":
                            pairs = [None, inst.args[0]]
                        else:
                            pairs = inst.args

                        # Add out edge to each successor block, which can be
                        # many for generalized "if".
                        for i in range(0, len(pairs), 2):
                            cond = pairs[i]
                            addr = pairs[i + 1]
                            # Skip adding bblocks for indirect jumps
                            if isinstance(addr, ADDR):
                                addr = addr.addr
                                if addr not in self.cfg:
                                    self.cfg.add_node(addr)
                                self.cfg.add_edge(block.addr, addr, cond=cond)

                        if cond or inst.op == "call":
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
                print("Warning: function %s was not properly terminated" % self.cfg.props["name"])
                # block may be None e.g. if last instruction was call,
                # and function abruptly ended without return.
                if block:
                    self.cfg.add_edge(last_block.addr, block.addr)

    def parse_bblocks(self, f):
        self.pass_no = 2
        try:
            self._parse_bblocks(f)
        except ParseError as e:
            print("Error: %d: %r" % (self.curline + 1, e))
            raise
            sys.exit(1)
        # External labels may produce empty CFG nodes during parsing.
        # Make a pass over graph and remove such.
        for node, info in list(self.cfg.nodes_props()):
            if not info:
                self.cfg.remove_node(node)


    def parse(self):
        self.parse_labels()
        self.curline = 0
        with open(self.fname) as f:
            self.parse_bblocks(f)
        return self.cfg

    def should_stop(self, addr, l):
        return False
