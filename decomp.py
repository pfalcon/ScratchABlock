import copy
import logging

from graph import Graph
from core import *
from xform import *
import cfgutils


log = logging.getLogger(__name__)


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


class RecursiveBlock(BBlock):
    """A structured block, consisting recursively of BBlock's and
    RecursiveBlock's."""

    def recursive_union(self, func):
        res = set()
        for subb in self.subblocks():
            res |= func(subb)
        return res

    def uses(self):
        return self.recursive_union(lambda b: b.uses())

    def defs(self, regs_only=True):
        return self.recursive_union(lambda b: b.defs(regs_only))


class Seq(RecursiveBlock):
    def __init__(self, b1, b2):
        super().__init__(b1.addr)
        if isinstance(b1, Seq):
            b1 = b1.items
        else:
            b1 = [b1]
        if isinstance(b2, Seq):
            b2 = b2.items
        else:
            b2 = [b2]
        self.items = b1 + b2

    def subblocks(self):
        return self.items

    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, self.items)

    def dump(self, stream, indent=0, printer=str):
        for b in self.items:
            b.dump(stream, indent, printer)


def match_seq(cfg):
    for v in cfg.nodes():
        if cfg.degree_out(v) == 1:
            succ = cfg.succ(v)[0]
            if cfg.degree_in(succ) == 1:
                log.info("seq: %s %s", v, succ)
                newb = Seq(cfg.node(v)["val"], cfg.node(succ)["val"])
                cfg.add_node(v, val=newb)
                cfg.move_succ(succ, v)
                cfg.remove_node(succ)
                return True


def match_if(cfg):
    for v in cfg.nodes():
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
                log.info("if: %s, %s, %s", v, b, c)
                v = split_bblock(cfg, v, ".if", only_non_empty=True)
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

class IfElse(RecursiveBlock):
    def __init__(self, header, t_block, f_block, true_cond):
        super().__init__(header.addr)
        self.header = header
        self.branches = [(true_cond, t_block), (None, f_block)]

    def subblocks(self):
        return [x[1] for x in self.branches if x[1]]

    def recursive_union(self, func):
        res = set()
        for cond, subb in self.branches:
            if cond:
                res |= func(cond)
            if subb:
                res |= func(subb)
        return res

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
    for v in cfg.nodes():
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
                if not common:
                    continue

                f_v_preds = cfg.pred(f_v)
                t_v_preds = cfg.pred(t_v)
                if len(f_v_preds) != 1 or len(t_v_preds) != 1:
                    log.warn("ifelse: %s, %s, %s, %s is part of abnormal selection", v, t_v, f_v, f_v_s[0])
                    continue

                f_v_s = common

                log.info("ifelse: %s, %s, %s, %s", v, t_v, f_v, f_v_s[0])
                v = split_bblock(cfg, v, ".if", only_non_empty=True)
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

def match_if_else_inv_ladder_recursive(block):
    if isinstance(block, IfElse):
        if len(block.branches) != 2:
            log.warn("match_if_else_inv_ladder: Must be applied before match_if_else_ladder")
            return
        if_block = block.branches[0][IFELSE_BRANCH]
        else_block = block.branches[1][IFELSE_BRANCH]
        if isinstance(if_block, IfElse) and not isinstance(else_block, IfElse):
            block.swap_branches()
        if_block = block.branches[0][IFELSE_BRANCH]
        else_block = block.branches[1][IFELSE_BRANCH]
        match_if_else_inv_ladder_recursive(if_block)
        match_if_else_inv_ladder_recursive(else_block)

def match_if_else_inv_ladder(cfg):
    for v, node_props in cfg.nodes_props():
        block = node_props["val"]
        match_if_else_inv_ladder_recursive(block)


#
# If we have:
#
# $a0 = val1
# if (...) {
#   $a0 = val2
# }
#
# it's equivalent to:
#
# if (...) {
#   $a0 = val2
# } else {
#   $a0 = val1
# }
#
# And transforming it to such may enable match_if_else_ladder
def match_if_else_unjumped(cfg):
    for v, node_props in cfg.nodes_props():
        #print((v, node_props))
        block = node_props["val"]
        if type(block) is BBlock and cfg.degree_out(v) == 1:
            succ = cfg.succ(v)[0]
            #print(">", (succ, cfg.node(succ)))
            succ_block = cfg.node(succ)["val"]
            if isinstance(succ_block, IfElse) \
              and succ_block.branches[-1][IFELSE_BRANCH] is None \
              and type(succ_block.branches[0][IFELSE_BRANCH]) is BBlock:
                first_defs = block.defs(regs_only=False)
                second_defs = succ_block.defs(regs_only=False)
                second_uses = succ_block.uses()
                log.info("ifelse_unjumped: first: defs: %s | second: defs: %s, uses: %s", first_defs, second_defs, second_uses)
                if not first_defs:
                    # Everything was apparently DCEed
                    return
                if not first_defs.issubset(second_defs):
                    log.info("ifelse_unjumped: can't apply, because first defines more other vars than 2nd: %s vs %s",
                         first_defs, second_defs)
                    return
                if first_defs & second_uses:
                    log.info("ifelse_unjumped: can't apply, because if uses (%s) vals defined in preceding block (%s)",
                        second_uses, first_defs)
                    return
                # TODO: Are the checks above enough?
                log.info("ifelse_unjumped: %s, %s", v, succ)
                cfgutils.detach_node(cfg, v)
                succ_block.branches[-1] = (None, block)
                return True


def match_if_else_ladder(cfg):
    for v, node_props in cfg.nodes_props():
        block = node_props["val"]
        if isinstance(block, IfElse):
            else_block = block.branches[-1][1]
            if isinstance(else_block, IfElse):
                block.branches = block.branches[:-1] + else_block.branches
                return True


class Loop(RecursiveBlock):
    def __init__(self, b):
        super().__init__(b.addr)
        self.items = [b]

    def subblocks(self):
        return self.items

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.items[0])

    def dump(self, stream, indent=0, printer=str):
        self.write(stream, indent, "while (1) {")
        for b in self.items:
            b.dump(stream, indent + 1, printer)
        self.write(stream, indent, "}")


def match_infloop(cfg):
    for v in cfg.nodes():
        if cfg.degree_out(v) == 1:
            for s in cfg.succ(v):
                if s == v:
                    log.info("infloop: %s", v)
                    b = cfg.node(v)["val"]
                    newb = Loop(b)
                    cfg.add_node(v, val=newb)
                    cfg.remove_edge(v, v)
                    return True


class DoWhile(RecursiveBlock):
    def __init__(self, b, cond):
        super().__init__(b.addr)
        self.cond = cond
        self.items = [b]

    def subblocks(self):
        return self.items

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.items[0])

    def dump(self, stream, indent=0, printer=str):
        self.write(stream, indent, "do {")
        for b in self.items:
            b.dump(stream, indent + 1, printer)
        self.write(stream, indent, "} while %s;" % self.cond)


def match_dowhile(cfg):
    for v in cfg.nodes():
        if cfg.degree_out(v) == 2:
            for s in cfg.succ(v):
                if s == v:
                    log.info("dowhile: %s", v)
                    b = cfg.node(v)["val"]
                    newb = DoWhile(b, cfg.edge(v, v).get("cond"))
                    cfg.add_node(v, val=newb)
                    cfg.remove_edge(v, v)
                    return True


class While(RecursiveBlock):
    def __init__(self, addr, b, cond):
        super().__init__(addr)
        self.cond = cond
        self.items = [b]

    def subblocks(self):
        return self.items

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.items[0])

    def dump(self, stream, indent=0, printer=str):
        self.write(stream, indent, "while %s {" % self.cond)
        for b in self.items:
            b.dump(stream, indent + 1, printer)
        self.write(stream, indent, "}")


def match_while(cfg):
    for v in cfg.nodes():
        if cfg.degree_out(v) == 2:
            succ = cfg.sorted_succ(v)
            back_cand = cfg.succ(succ[0])
            if len(back_cand) == 1 and back_cand[0] == v and cfg.degree_in(succ[0]) == 1:
                log.info("while: %s, %s", v, succ[0])
                b = cfg.node(succ[0])["val"]
                newb = While(v, b, cfg.edge(v, succ[0]).get("cond"))
                cfg.add_node(v, val=newb)
                cfg.remove_node(succ[0])
                return True

#
# if (cond) {
#   do {...} while (cond);
# }
#
# =>
#
# while (cond) {...}
#
def match_if_dowhile(cfg):
    for addr, info in cfg.nodes_props():
        bblock = info["val"]
        if type(bblock) is IfElse:
            subs = bblock.subblocks()
            if len(subs) == 1 and type(subs[0]) is DoWhile:
                if_cond = bblock.branches[0][0]
                dowhile_cond = subs[0].cond
                #print(if_cond, if_cond == dowhile_cond)
                if if_cond != dowhile_cond:
                    continue
                while_bb = While(bblock.branches[0][1], subs[0].items[0], if_cond)
                info["val"] = while_bb
                return True


def match_control_and(cfg):
    for v in cfg.nodes():
        if cfg.degree_out(v) == 2:
            succ1 = cfg.sorted_succ(v)
            v2 = succ1[1]
            if cfg.degree_out(v2) == 2:
                succ2 = cfg.sorted_succ(v2)
                assert len(succ2) == 2
                if succ1[0] == succ2[0]:
                    log.info("and %s, %s", v, v2)
                    new_cond = EXPR(
                        "||",
                        cfg.edge(v, succ1[0]).get("cond").expr,
                        cfg.edge(v2, succ1[0]).get("cond").expr
                    )
                    cfg.edge(v, succ1[0]).get("cond").expr = new_cond
                    cfg.remove_node(v2)
                    cfg.add_edge(v, succ2[1])
                    return True


def match_abnormal_sel(cfg):
    """Should be run only if match_if, match_ifelse don't match anything
    in acyclic graph. Then any join node belong to abnormal selection
    pattern. We try to find the top-most and split it, after which normal
    structured matches should be tried again.
    """
    for v in cfg.iter_rev_postorder():
        if cfg.degree_in(v) == 2 and cfg.degree_out(v) == 1:
            log.info("abnormal_sel: %s", v)
            split_node(cfg, v)
            return True
