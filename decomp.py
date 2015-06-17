from graph import Graph
from core import *


class Seq(BBlock):
    def __init__(self, b1, b2):
        self.addr = b1.addr
        self.items = [b1, b2]

    def __repr__(self):
        return "%s(%r, %r)" % (self.__class__.__name__, self.items[0], self.items[1])

    def dump(self, stream, indent=0):
        for b in self.items:
            b.dump(stream, indent)


def match_seq(cfg):
    for v, _ in cfg.iter_nodes():
        if cfg.degree_out(v) == 1:
            succ = cfg.succ(v)[0]
            if cfg.degree_in(succ) == 1:
                print("seq:", v, succ)
                newb = Seq(cfg.node(v), cfg.node(succ))
                cfg.add_node(v, newb)
                cfg.move_succ(succ, v)
                cfg.remove_node(succ)
                return True


class If(BBlock):
    def __init__(self, header, t_block, false_cond):
        self.addr = header.addr
        self.cond = false_cond
        self.items = [header, t_block]

    def __repr__(self):
        return "%s(%r, %r)" % (self.__class__.__name__, self.items[0], self.items[1])

    def dump(self, stream, indent=0):
        self.write(stream, indent, "if %s {" % self.cond.neg())
        self.items[1].dump(stream, indent + 1)
        self.write(stream, indent, "}")


def match_if(cfg):
    for v, _ in cfg.iter_nodes():
        if cfg.degree_out(v) == 2:
            a, b = cfg.sorted_succ(v)
            if cfg.degree_in(a) >= 2 and cfg.degree_in(b) == 1 and cfg.degree_out(b) == 1:
                c = cfg.succ(b)[0]
                if c == a:
                    print("if:", v, b, c)
                    if_header = cfg.node(v)
                    t_block = cfg.node(b)
                    newb = If(if_header, t_block, cfg.edge(v, a))
                    cfg.add_node(v, newb)
                    cfg.remove_node(b)
                    cfg.set_edge(v, a, None)
                    return True


class IfElse(BBlock):
    def __init__(self, header, t_block, f_block, false_cond):
        self.addr = header.addr
        self.cond = false_cond
        self.l = [header, t_block, f_block]

    def __repr__(self):
        return "%s(%r, %r)" % (self.__class__.__name__, self.l[0], self.l[1])

    def dump(self, stream, indent=0):
        self.write(stream, indent, "if (!%s) {" % self.cond)
        self.l[1].dump(stream, indent + 1)
        self.write(stream, indent, "} else {")
        self.l[2].dump(stream, indent + 1)
        self.write(stream, indent, "}")


# if (!(a > b)) goto false
# {true}
# goto out
# false:
# {false}
# out:

def match_ifelse(cfg):
    for v, _ in cfg.iter_nodes():
        if cfg.degree_out(v) == 2:
            succ = cfg.sorted_succ(v)
            cond = cfg.edge(v, succ[0])
            if cond:
                f_v = succ[0]
                t_v = succ[1]
                f_v_s = cfg.succ(f_v)
                t_v_s = cfg.succ(t_v)

                if len(t_v_s) < 1: continue
                if len(f_v_s) < 1: continue
                common = list(set(t_v_s) & set(f_v_s))
                if common:
                    f_v_s = common

                    print("ifelse:", v, t_v, f_v, f_v_s[0])
                    if_header = cfg.node(v)
                    t_block = cfg.node(t_v)
                    f_block = cfg.node(f_v)
                    newb = IfElse(if_header, t_block, f_block, cond)
                    cfg.add_node(v, newb)
                    cfg.remove_node(t_v)
                    cfg.remove_node(f_v)
                    cfg.add_edge(v, f_v_s[0])
                    return True


class DoWhile(BBlock):
    def __init__(self, b, cond):
        self.addr = b.addr
        self.cond = cond
        self.items = [b]

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.items[0])

    def dump(self, stream, indent=0):
        self.write(stream, indent, "do {")
        for b in self.items:
            b.dump(stream, indent + 1)
        self.write(stream, indent, "} while %s" % self.cond)


def match_dowhile(cfg):
    for v, _ in cfg.iter_nodes():
        if cfg.degree_out(v) == 2:
            for s in cfg.succ(v):
                if s == v:
                    print("dowhile:", v)
                    b = cfg.node(v)
                    newb = DoWhile(b, cfg.edge(v, v))
                    cfg.add_node(v, newb)
                    cfg.remove_edge(v, v)
                    return True


class While(BBlock):
    def __init__(self, b, cond):
        self.addr = b.addr
        self.cond = cond
        self.items = [b]

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.items[0])

    def dump(self, stream, indent=0):
        self.write(stream, indent, "while %s {" % self.cond)
        for b in self.items:
            b.dump(stream, indent + 1)
        self.write(stream, indent, "}")


def match_while(cfg):
    for v, _ in cfg.iter_nodes():
        if cfg.degree_out(v) == 2:
            succ = cfg.sorted_succ(v)
            back_cand = cfg.succ(succ[0])
            if len(back_cand) == 1 and back_cand[0] == v:
                print("while:", v, succ[0])
                b = cfg.node(succ[0])
                newb = While(b, cfg.edge(v, succ[0]))
                cfg.add_node(v, newb)
                cfg.remove_node(succ[0])
                return True
