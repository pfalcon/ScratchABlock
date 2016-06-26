import core
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
        "Entry node is set to itself, the rest - to graph's all nodes."
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
                if inst.dest and (not self.regs_only or isinstance(inst.dest, core.REG)):
                    kill |= set(filter(lambda x: x[0] == inst.dest, all_defs)) | {(inst.dest, None)}
                    if self.inst_level:
                        addr = inst.addr
                    else:
                        addr = bblock.addr
                    gen.add((inst.dest, addr))
            info[self.node_prop_kill] = kill
            info[self.node_prop_gen] = gen


class LiveVarAnalysis(GenKillAnalysis):
    forward = False
    join_op = staticmethod(set_union)
    prop_prefix = "live"

    def init(self):
        "Entry node is set to itself, the rest - to graph's all nodes."
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
                for r in inst.uses():
                    if r not in kill:
                        gen.add(r)
                if inst.dest:
                    kill.add(inst.dest)

            info[self.node_prop_kill] = kill
            info[self.node_prop_gen] = gen
