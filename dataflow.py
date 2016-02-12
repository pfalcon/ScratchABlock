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
        prop_in = self.node_prop_in
        prop_out = self.node_prop_out

        changed = True
        while changed:
            changed = False

            for node, info in self.g.iter_sorted_nodes():
                if self.forward:
                    sources = self.g.pred(node)
                else:
                    sources = self.g.succ(node)

                if prop_out:
                    info[prop_out] = self.transfer(node, info[prop_in])

                if sources:
                    # If there're no "sources" for this node, it's an initial node,
                    # and should keep it's "in" set (which may be non-empty).
                    new = self.join(node, sources)
                    if new != info[prop_in]:
                        info[prop_in] = new
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
