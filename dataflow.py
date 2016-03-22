from xform import foreach_bblock


class AnalysisBase:

    # Set to False for backward analysis
    forward = True
    # Set to name of node "in" state
    node_prop_in = None
    # Set to name of node "out" state
    node_prop_out = None

    def __init__(self, graph):
        self.g = graph

    def solve(self):
        "Solve dataflow analysis."
        self.init()
        if self.forward:
            prop_src = self.node_prop_in
            prop_dst = self.node_prop_out
        else:
            prop_src = self.node_prop_out
            prop_dst = self.node_prop_in

        changed = True
        while changed:
            changed = False

            for node, info in self.g.iter_sorted_nodes():
                if self.forward:
                    sources = self.g.pred(node)
                else:
                    sources = self.g.succ(node)

                if prop_dst:
                    new = self.transfer(node, info[prop_src])
                    if new != info[prop_dst]:
                        info[prop_dst] = new
                        changed = True

                if sources:
                    # If there're no "sources" for this node, it's an initial node,
                    # and should keep it's "in" set (which may be non-empty).
                    new = self.join(node, sources)
                    if new != info[prop_src]:
                        info[prop_src] = new
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
        if source_nodes:
            state = set.intersection(*(self.g.get_node_attr(x, self.node_prop_in) for x in source_nodes))
        else:
            state = set()
        return state | {node}


class ReachDefAnalysis(AnalysisBase):
    "Encapsulation of dataflow analysis for reaching definitions."
    forward = True
    node_prop_in = "reachdef_in"
    node_prop_out = "reachdef_out"

    def init(self):
        "Entry node is set to itself, the rest - to graph's all nodes."
        entry = self.g.entries()
        assert len(entry) == 1
        entry = entry[0]
        all_defs = foreach_bblock(self.g, lambda b: b.def_addrs(), set.union)

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
                if inst.dest:
                    kill |= set(filter(lambda x: x[0] == inst.dest, all_defs)) | {(inst.dest, None)}
                    gen.add((inst.dest, inst.addr))
            info["kill_rd"] = kill
            info["gen_rd"] = gen

    def transfer(self, node, src_state):
        return (src_state - self.g.get_node_attr(node, "kill_rd")) | self.g.get_node_attr(node, "gen_rd")

    def join(self, node, source_nodes):
        if source_nodes:
            state = set.union(*(self.g.get_node_attr(x, self.node_prop_out) for x in source_nodes))
        else:
            state = set()
        return state
