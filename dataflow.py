def solve(cfg, analysis):
    "Solve dataflow for analysis object on a graph."
    analysis.init(cfg)
    prop = analysis.node_prop

    changed = True
    while changed:
        changed = False

        for node, info in cfg.iter_sorted_nodes():
            if analysis.forward:
                sources = cfg.pred(node)
            else:
                sources = cfg.succ(node)
            new = analysis.new_state(node, sources)
            if new != info[prop]:
                info[prop] = new
                changed = True


class DominatorAnalysis:
    "Encapsulation of dataflow analysis to discover graph node dominators."

    forward = True
    node_prop = "dom"

    def init(self, cfg):
        "Entry node is set to itself, the rest - to graph's all nodes."
        self.cfg = cfg
        entry = cfg.entries()
        assert len(entry) == 1
        entry = entry[0]
        all_nodes = set(cfg.nodes())
        for node, info in cfg.iter_nodes():
            if node == entry:
                info[self.node_prop] = {node}
            else:
                info[self.node_prop] = all_nodes

    def new_state(self, node, sources):
        if sources:
            state = set.intersection(*(self.cfg.get_node_attr(x, self.node_prop) for x in sources))
        else:
            state = set()
        return state | {node}
