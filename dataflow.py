import logging

import core
from core import is_expr, is_mem
from utils import set_union, set_intersection
from cfgutils import foreach_bblock


log = logging.getLogger(__name__)


class AnalysisBase:

    # Set to False for backward analysis
    forward = True
    # property prefix to use
    prop_prefix = None
    # Set to name of node "in" state
    node_prop_in = None
    # Set to name of node "out" state
    node_prop_out = None
    node_prop_gen = None
    node_prop_kill = None

    def __init__(self, graph):
        self.g = graph
        if self.prop_prefix:
            self.node_prop_in = self.prop_prefix + "_in"
            self.node_prop_out = self.prop_prefix + "_out"
            self.node_prop_gen = self.prop_prefix + "_gen"
            self.node_prop_kill = self.prop_prefix + "_kill"

        if self.forward:
            self.node_prop_src = self.node_prop_in
            self.node_prop_dst = self.node_prop_out
        else:
            self.node_prop_src = self.node_prop_out
            self.node_prop_dst = self.node_prop_in


    def solve(self):
        "Solve dataflow analysis."
        self.init()

        changed = True
        while changed:
            changed = False

            for node, info in self.g.iter_sorted_nodes():
                if self.forward:
                    sources = self.g.pred(node)
                else:
                    sources = self.g.succ(node)

                if self.node_prop_dst:
                    new = self.transfer(node, info[self.node_prop_src])
                    if new != info[self.node_prop_dst]:
                        info[self.node_prop_dst] = new
                        changed = True

                if sources:
                    # If there're no "sources" for this node, it's an initial node,
                    # and should keep it's "in" set (which may be non-empty).
                    new = self.join(node, sources)
                    if new != info[self.node_prop_src]:
                        info[self.node_prop_src] = new
                        changed = True

    def transfer(self, node, src_state):
        """Transfer function. Computes next state of a node, based on
        source state. For forward analisys, source state is 'in' state,
        next state is 'out' state. For backward analysis, vice-versa.
        Note that this function should not be concerned with direction
        of analysis, it's just fed with 'source' state by the solver.

        Default implementation does nothing, and is suitable for analyses
        which don't depend on node "content", only on overall graph
        structure (control flow analyses vs data flow analyses).
        """
        return src_state

    def join(self, node, source_nodes):
        raise NotImplementedError


class DominatorAnalysis(AnalysisBase):
    "Encapsulation of dataflow analysis to discover graph node dominators."

    forward = True
    node_prop_in = "dom"

    def init(self):
        "Entry node is set to itself, the rest - to graph's all nodes."
        entry = self.g.entries()
        assert len(entry) == 1
        entry = entry[0]
        all_nodes = set(self.g.nodes())
        for node, info in self.g.iter_nodes():
            if node == entry:
                info[self.node_prop_in] = {node}
            else:
                info[self.node_prop_in] = all_nodes

    def join(self, node, source_nodes):
        state = set_intersection(*(self.g.get_node_attr(x, self.node_prop_in) for x in source_nodes))
        return state | {node}


class GenKillAnalysis(AnalysisBase):

    # Should be staticmethod(set_union) or staticmethod(set_intersection)
    # staticmethod() is required to work around Python's magic handling
    # of functions references within classes.
    join_op = None

    def transfer(self, node, src_state):
        return (src_state - self.g.get_node_attr(node, self.node_prop_kill)) | self.g.get_node_attr(node, self.node_prop_gen)

    def join(self, node, source_nodes):
        # node_prop_dst is named from the point of view of intra-node transfer function.
        # inter-node join function takes source nodes dst set to compute current node
        # src set
        return self.join_op(*(self.g.get_node_attr(x, self.node_prop_dst) for x in source_nodes))


class ReachDefAnalysis(GenKillAnalysis):
    "Encapsulation of dataflow analysis for reaching definitions."
    forward = True
    join_op = staticmethod(set_union)
    prop_prefix = "reachdef"


    def __init__(self, cfg, regs_only=True, inst_level=False):
        """If inst_level is True, perform instruction-level analysis, i.e.
        result will be as a set of (var, inst_addr) pairs. Otherwise, it
        will be (var, bblock_addr). inst_level=True is useful mostly for
        unittests/adhoc cases."""
        super().__init__(cfg)
        self.inst_level = inst_level
        self.regs_only = regs_only

    def init(self):
        """In and out sets of all nodes are initialized to empty sets, but
        entry's in set is initialized to a set of all defined locations with
        None address, representing non-initialized location."""
        entry = self.g.entries()
        assert len(entry) == 1, len(entry)
        entry = entry[0]
        if self.inst_level:
            all_defs = foreach_bblock(self.g, lambda b: b.def_addrs(self.regs_only), set.union)
        else:
            all_defs = foreach_bblock(self.g, lambda b: set((v, b.addr) for v in b.defs(self.regs_only)), set.union)

        for node, info in self.g.iter_nodes():
            if node == entry:
                # Entry's in set to all vars, with "undefined" definition location (None).
                info[self.node_prop_in] = set(((v[0], None) for v in all_defs))
            else:
                info[self.node_prop_in] = set()
            info[self.node_prop_out] = set()

            bblock = info["val"]
            kill = set()
            gen = set()
            for inst in bblock.items:
                addr = inst.addr if self.inst_level else bblock.addr
                defs = inst.defs(self.regs_only)
                # Kill any real matching defs in function
                kill |= {x for x in all_defs if x[0] in defs}
                # and also any "undefined" defs from function reach-in
                kill |= {(r, None) for r in defs}
                for d in defs:
                    gen.add((d, addr))
            info[self.node_prop_kill] = kill
            info[self.node_prop_gen] = gen


class LiveVarAnalysis(GenKillAnalysis):
    forward = False
    join_op = staticmethod(set_union)
    prop_prefix = "live"

    def __init__(self, cfg, skip_calls=False, underestimate=False):
        """If skip_calls is True, skip call instructions. This is useful
        to estimate current function's argument registers (using unspecific
        call-conventions driven .uses() for a call instruction may/will make
        all call-conventions arg registers live for function entry)."""
        super().__init__(cfg)
        self.skip_calls = skip_calls
        self.underestimate = underestimate

    def init(self):
        "In and out sets of all nodes is set to empty."
        exits = self.g.exits()
        assert len(exits) == 1
        exit = exits[0]

        for node, info in self.g.iter_nodes():
            info[self.node_prop_in] = set()
            if node == exit:
                if self.underestimate:
                    info[self.node_prop_out] = set()
                elif self.g.props.get("noreturn") or self.g.props.get("name") == "main":
                    info[self.node_prop_out] = set()
                else:
                    import progdb
                    rets = progdb.FUNC_DB.get(self.g.props.get("name"), {}).get("returns")
                    if rets is not None:
                        assert isinstance(rets, set)
                        info[self.node_prop_out] = rets
                    elif "modifieds" in self.g.props:
                        info[self.node_prop_out] = self.g.props["modifieds"]
                        log.warning("Conservatively using modifieds as function live-out")
                    elif "reach_exit" in self.g.props:
                        info[self.node_prop_out] = self.g.props["reach_exit"]
                        log.warning("Conservatively using reach_exit as function live-out")
                    else:
                        info[self.node_prop_out] = set()
            else:
                info[self.node_prop_out] = set()

            bblock = info["val"]

            kill = set()
            gen = set()
            for inst in bblock.items:
                if inst.op == "call" and self.skip_calls:
                    continue

                # If we underestimate liveness, assume function
                # calls don't use anything, only kill liveness below.
                if inst.op != "call" or not self.underestimate:
                    for r in inst.uses(self.g):
                        if r not in kill:
                            gen.add(r)
                else:
                    # We still need to account for reg uses in indirect call expression
                    for r in inst.args[0].regs():
                        if r not in kill:
                            gen.add(r)

                for dest in inst.defs(regs_only=False):
                    kill.add(dest)

            info[self.node_prop_kill] = kill
            info[self.node_prop_gen] = gen


def make_du_chains(cfg):
    log = logging.getLogger("make_du_chains")

    du_map = {}
    bblock_last_def = {}

    for bblock_addr, node_props in cfg.iter_sorted_nodes():
        bblock = node_props["val"]
        last_def = {}

        for inst in bblock.items:
            defs = inst.defs(regs_only=False)
            if defs:
                inst.comments["uses"] = []
                du_map[inst.addr] = inst.comments["uses"]
                for dest in defs:
                    last_def[dest] = inst.addr

        log.debug("last_def for %s: %s", bblock_addr, last_def)
        bblock_last_def[bblock_addr] = last_def

    log.debug("empty du_map: %s", du_map)
    log.debug("bblock_last_def: %s", bblock_last_def)

    for bblock_addr, node_props in cfg.iter_sorted_nodes():
        bblock = node_props["val"]
        last_def = {}

        reachdef_in = node_props["reachdef_in"]
        log.debug("reachdef_in %s: %s", bblock_addr, reachdef_in)
        for var, defined_in_bblock in reachdef_in:
            if defined_in_bblock is not None:
                last_def.setdefault(var, set()).add(bblock_last_def[defined_in_bblock][var])
        log.debug("last_def on entry: %s", last_def)

        for inst in bblock.items:
            log.debug("%s: %s", inst, inst.uses(cfg))
            for r in inst.uses(cfg):
                if r in last_def:
                    log.debug("%s", last_def[r])
                    for inst_addr in last_def[r]:
                        du_map[inst_addr].append(inst.addr)
                else:
                    log.debug("%r not in last_def", r)

            defs = inst.defs(regs_only=False)
            for dest in defs:
                last_def[dest] = {inst.addr}

    log.debug("du_map:", du_map)
