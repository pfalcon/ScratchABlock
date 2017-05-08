import core
from core import is_expr, is_mem
from utils import set_union, set_intersection
from xform import foreach_bblock


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
        assert len(entry) == 1
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

    def __init__(self, cfg, skip_calls=False):
        """If skip_calls is True, skip call instructions. This is useful
        to estimate current function's argument registers (using unspecific
        call-conventions driven .uses() for a call instruction may/will make
        all call-conventions arg registers live for function entry)."""
        super().__init__(cfg)
        self.skip_calls = skip_calls

    def init(self):
        "In and out sets of all nodes is set to empty."
        exits = self.g.exits()
        assert len(exits) == 1
        exit = exits[0]

        for node, info in self.g.iter_nodes():
            info[self.node_prop_in] = set()
            info[self.node_prop_out] = set()

            bblock = info["val"]

            kill = set()
            gen = set()
            for inst in bblock.items:
                if inst.op == "call" and self.skip_calls:
                    continue
                for r in inst.uses(self.g):
                    if r not in kill:
                        gen.add(r)
                if inst.dest:
                    kill.add(inst.dest)

            info[self.node_prop_kill] = kill
            info[self.node_prop_gen] = gen


def make_du_chains(cfg):

    def trace(bblock, mapping):
        for inst in bblock.items:
            args = inst.args
            if len(args) == 1 and is_expr(args[0]):
                args = args[0].args
            for r in inst.uses(cfg):
                if r in mapping:
                    mapping[r].comments["uses"].append(inst.addr)

            for dest in inst.defs(regs_only=False):
                mapping[dest] = inst
                inst.comments["uses"] = []

    # sorted_nodes are for unit testing
    # Generally, should either start from single entry or initialize
    # last_def_insts with reachdef_in.
    for addr, node_props in cfg.iter_sorted_nodes():
        bblock = node_props["val"]
        last_def_insts = {}
        trace(bblock, last_def_insts)

        for addr, node_props in cfg.iter_sorted_nodes():
            bblock = node_props["val"]
            for var, inst in last_def_insts.items():
                if (var, inst.addr) in node_props["reachdef_in"]:
                    mapping = last_def_insts.copy()
                    trace(bblock, mapping)
