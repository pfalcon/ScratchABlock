import copy

from graph import Graph
from core import *


def split_bblock(cfg, n):
    # If a node is non-empty bblock, splits it in two, with 2nd one being
    # empty, and having all out edges, and returns this 2nd one. If bblock
    # is already empty, returns it directly.
    if not cfg[n]["val"].items:
        return n
    addr = n + ".if"
    pre = BBlock(addr)
    cfg.add_node(addr, val=pre)
    cfg.move_succ(n, addr)
    cfg.add_edge(n, addr)
    return addr


def split_node(cfg, n):
    """Split node "horizontally", by duplicating its content and splitting
    incoming and outgoing edges.
    """
    assert cfg.degree_in(n) == 2
    assert cfg.degree_out(n) == 1
    preds = cfg.pred(n)
    node_props = cfg[n]
    node2_props = copy.deepcopy(node_props)
    n2 = n + ".split1"
    cfg.add_node(n2, **node2_props)
    cfg.remove_edge(preds[1], n)
    cfg.add_edge(preds[1], n2)
    cfg.add_edge(n2, cfg.succ(n)[0])


class Seq(BBlock):
    def __init__(self, b1, b2):
        super().__init__(b1.addr)
        self.items = [b1, b2]

    def subblocks(self):
        return self.items

    def __repr__(self):
        return "%s(%r, %r)" % (self.__class__.__name__, self.items[0], self.items[1])

    def dump(self, stream, indent=0, printer=str):
        for b in self.items:
            b.dump(stream, indent, printer)


def match_seq(cfg):
    for v, _ in cfg.iter_nodes():
        if cfg.degree_out(v) == 1:
            succ = cfg.succ(v)[0]
            if cfg.degree_in(succ) == 1:
                print("seq:", v, succ)
                newb = Seq(cfg.node(v)["val"], cfg.node(succ)["val"])
                cfg.add_node(v, val=newb)
                cfg.move_succ(succ, v)
                cfg.remove_node(succ)
                return True


def match_if(cfg):
    for v, _ in cfg.iter_nodes():
        if cfg.degree_out(v) == 2:
            a, b = cfg.sorted_succ(v)

            if cfg.degree_in(a) >= 2 and cfg.degree_in(b) == 1 and cfg.degree_out(b) == 1:
                truth = False
                cond = cfg.edge(v, a).get("cond")
            elif cfg.degree_in(b) >= 2 and cfg.degree_in(a) == 1 and cfg.degree_out(a) == 1:
                truth = True
                cond = cfg.edge(v, a).get("cond")
                a, b = b, a
            else:
                continue

            c = cfg.succ(b)[0]
            if c == a:
                print("if:", v, b, c)
                v = split_bblock(cfg, v)
                if_header = cfg.node(v)["val"]
                t_block = cfg.node(b)["val"]
                if truth == False:
                    cond = cond.neg()
                newb = IfElse(if_header, t_block, None, cond)
                cfg.add_node(v, val=newb)
                cfg.remove_node(b)
                cfg.set_edge(v, a, cond=None)
                return True


IFELSE_COND = 0
IFELSE_BRANCH = 1

class IfElse(BBlock):
    def __init__(self, header, t_block, f_block, true_cond):
        super().__init__(header.addr)
        self.header = header
        self.branches = [(true_cond, t_block), (None, f_block)]

    def subblocks(self):
        return [x[1] for x in self.branches if x[1]]

    def swap_branches(self):
        # Swap If/Else branches, negating condition
        assert len(self.branches) == 2
        assert self.branches[1][1] is not None
        [(true_cond, t_block), (dummy, f_block)] = self.branches
        self.branches = [(true_cond.neg(), f_block), (None, t_block)]

    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, self.branches)

    def dump(self, stream, indent=0, printer=str):
        self.write(stream, indent, "if %s {" % self.branches[0][0])
        self.branches[0][1].dump(stream, indent + 1, printer)

        for cond, block in self.branches[1:-1]:
            self.write(stream, indent, "} else if %s {" % cond)
            block.dump(stream, indent + 1, printer)

        assert self.branches[-1][0] is None
        if self.branches[-1][1] is not None:
            self.write(stream, indent, "} else {")
            self.branches[-1][1].dump(stream, indent + 1, printer)
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
            cond = cfg.edge(v, succ[0]).get("cond")
            if cond:
                f_v = succ[0]
                t_v = succ[1]
                f_v_s = cfg.succ(f_v)
                t_v_s = cfg.succ(t_v)

                if len(t_v_s) != 1: continue
                if len(f_v_s) != 1: continue
                common = list(set(t_v_s) & set(f_v_s))
                if common:
                    f_v_s = common

                    print("ifelse:", v, t_v, f_v, f_v_s[0])
                    v = split_bblock(cfg, v)
                    if_header = cfg.node(v)["val"]
                    t_block = cfg.node(t_v)["val"]
                    f_block = cfg.node(f_v)["val"]
                    newb = IfElse(if_header, t_block, f_block, cond.neg())
                    cfg.add_node(v, val=newb)
                    cfg.remove_node(t_v)
                    cfg.remove_node(f_v)
                    cfg.add_edge(v, f_v_s[0])
                    return True


#
# If we have:
#
# if (cond) {
#   if ...
# } else {
#   // not if
# }
#
# It's better to transform it to:
#
# if (!cond) {
#   // not if
# } else {
#   if ...
# }
#
# , then to be recognized by match_if_else_ladder
def match_if_else_inv_ladder(cfg):
    for v, node_props in cfg.iter_nodes():
        block = node_props["val"]
        if isinstance(block, IfElse):
            assert len(block.branches) == 2, "Must be applied before match_if_else_ladder"
            if_block = block.branches[0][IFELSE_BRANCH]
            else_block = block.branches[1][IFELSE_BRANCH]
            if isinstance(if_block, IfElse) and not isinstance(else_block, IfElse):
                block.swap_branches()
                return True


def match_if_else_ladder(cfg):
    for v, node_props in cfg.iter_nodes():
        block = node_props["val"]
        if isinstance(block, IfElse):
            else_block = block.branches[-1][1]
            if isinstance(else_block, IfElse):
                block.branches = block.branches[:-1] + else_block.branches
                return True


class Loop(BBlock):
    def __init__(self, b):
        super().__init__(b.addr)
        self.items = [b]

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.items[0])

    def dump(self, stream, indent=0, printer=str):
        self.write(stream, indent, "while (1) {")
        for b in self.items:
            b.dump(stream, indent + 1, printer)
        self.write(stream, indent, "}")


def match_infloop(cfg):
    for v, _ in cfg.iter_nodes():
        if cfg.degree_out(v) == 1:
            for s in cfg.succ(v):
                if s == v:
                    print("infloop:", v)
                    b = cfg.node(v)["val"]
                    newb = Loop(b)
                    cfg.add_node(v, val=newb)
                    cfg.remove_edge(v, v)
                    return True


class DoWhile(BBlock):
    def __init__(self, b, cond):
        super().__init__(b.addr)
        self.cond = cond
        self.items = [b]

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.items[0])

    def dump(self, stream, indent=0, printer=str):
        self.write(stream, indent, "do {")
        for b in self.items:
            b.dump(stream, indent + 1, printer)
        self.write(stream, indent, "} while %s;" % self.cond)


def match_dowhile(cfg):
    for v, _ in cfg.iter_nodes():
        if cfg.degree_out(v) == 2:
            for s in cfg.succ(v):
                if s == v:
                    print("dowhile:", v)
                    b = cfg.node(v)["val"]
                    newb = DoWhile(b, cfg.edge(v, v).get("cond"))
                    cfg.add_node(v, val=newb)
                    cfg.remove_edge(v, v)
                    return True


class While(BBlock):
    def __init__(self, b, cond):
        super().__init__(b.addr)
        self.cond = cond
        self.items = [b]

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.items[0])

    def dump(self, stream, indent=0, printer=str):
        self.write(stream, indent, "while %s {" % self.cond)
        for b in self.items:
            b.dump(stream, indent + 1, printer)
        self.write(stream, indent, "}")


def match_while(cfg):
    for v, _ in cfg.iter_nodes():
        if cfg.degree_out(v) == 2:
            succ = cfg.sorted_succ(v)
            back_cand = cfg.succ(succ[0])
            if len(back_cand) == 1 and back_cand[0] == v:
                print("while:", v, succ[0])
                b = cfg.node(succ[0])["val"]
                newb = While(b, cfg.edge(v, succ[0]).get("cond"))
                cfg.add_node(v, val=newb)
                cfg.remove_node(succ[0])
                return True


class ControlAnd(BBlock):
    def __init__(self, addr, cond1, cond2):
        super().__init__(addr)
        #print((addr, cond1, cond2))
        self.cond = CompoundCond(cond1.list() + ["||"] + cond2.list())
        self.l = []

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.cond)

    def dump(self, stream, indent=0, printer=str):
        self.write(stream, indent, "/* && */")


def match_control_and(cfg):
    for v, _ in cfg.iter_nodes():
        if cfg.degree_out(v) == 2:
            succ1 = cfg.sorted_succ(v)
            v2 = succ1[1]
            if cfg.degree_out(v2) == 2:
                succ2 = cfg.sorted_succ(v2)
                assert len(succ2) == 2
                if succ1[0] == succ2[0]:
                    print("and", v, v2)
                    newb = ControlAnd(v, cfg.edge(v, succ1[0]).get("cond"), cfg.edge(v2, succ1[0]).get("cond"))
                    cfg.add_node(v, val=newb)
                    cfg.set_edge(v, succ1[0], cond=newb.cond)
                    cfg.remove_node(v2)
                    cfg.add_edge(v, succ2[1])
                    return True


def match_abnormal_sel(cfg):
    """Should be run only if match_if, match_ifelse don't match anything
    in acyclic graph. Then any join node belong to abnormal selection
    pattern. We try to find the top-most and split it, after which normal
    structured matches should be tried again.
    """
    for v, _ in cfg.iter_rev_postorder():
        if cfg.degree_in(v) == 2 and cfg.degree_out(v) == 1:
            split_node(cfg, v)
            return True
