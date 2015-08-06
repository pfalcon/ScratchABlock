from collections import defaultdict


class Graph:

    directed = True

    def __init__(self):
        self._nodes = {}
        self._edges = {}
        self._succ = defaultdict(list)
        self._pred = defaultdict(list)
        self._entries = []

    def add_node(self, node, value=None):
        "Add node to a graph. Node is an ID of a node. Value is an object associated with a node."
        if node in self._nodes:
            self._nodes[node]["val"] = value
        else:
            self._nodes[node] = {"val": value}
        if not self._entries:
            self._entries.append(node)

    def remove_node(self, node):
        for s in self._succ[node][:]:
            self.remove_edge(node, s)
        for p in self._pred[node][:]:
            self.remove_edge(p, node)
        del self._nodes[node]
        del self._succ[node]
        del self._pred[node]

    def node(self, n):
        return self._nodes[n]["val"]

    def set_node_attr(self, node, attr, val):
        self._nodes[node][attr] = val

    def get_node_attr(self, node, attr, default=Ellipsis):
        if default is Ellipsis:
            return self._nodes[node][attr]
        else:
            return self._nodes[node].get(attr, default)


    def add_edge(self, from_node, to_node, label=None):
        """Add edge between 2 nodes. If any of the nodes does not exist,
        it will be created."""
        self._edges[(from_node, to_node)] = label
        self._succ[from_node].append(to_node)
        self._pred[to_node].append(from_node)

    def set_edge(self, from_node, to_node, label=None):
        "Update label for existing edge."
        self._edges[(from_node, to_node)] = label

    def remove_edge(self, from_node, to_node):
        del self._edges[(from_node, to_node)]
        self._succ[from_node].remove(to_node)
        self._pred[to_node].remove(from_node)

    def edge(self, from_node, to_node):
        return self._edges[(from_node, to_node)]

    def succ(self, n):
        "Return successors of a node."
        return self._succ[n][:]

    def sorted_succ(self, n):
        """Return successors ordered the way that successor with labeled
        edge comes first. Assumes 2 succesors."""
        succ = self.succ(n)
        assert len(succ) == 2
        if self.edge(n, succ[0]) is None:
            succ = [succ[1], succ[0]]
        return succ

    def pred(self, n):
        "Return predecessors of a node."
        return self._pred[n][:]

    def degree_out(self, n):
        return len(self._succ[n])

    def degree_in(self, n):
        return len(self._pred[n])

    def __contains__(self, val):
        if isinstance(val, tuple):
            return val in self._edges
        else:
            return val in self._nodes

    def iter_nodes(self):
        return self._nodes.items()

    def iter_sorted_nodes(self):
        return sorted(self._nodes.items(), key=lambda x: x[0])

    def iter_edges(self):
        return self._edges.items()

    def entries(self):
        return self._entries

    def move_pred(self, from_node, to_node):
        for p in self.pred(from_node):
            self.add_edge(p, to_node, self._edges[(p, from_node)])
            self.remove_edge(p, from_node)

    def move_succ(self, from_node, to_node):
        for p in self.succ(from_node):
            self.add_edge(to_node, p, self._edges[(from_node, p)])
            self.remove_edge(from_node, p)

    def __repr__(self):
        return "<Graph nodes=%r edges=%r pred=%r succ=%r>" % (self._nodes, self._edges, self._pred, self._succ)

    def reset_numbering(self):
        for n, info in self._nodes.items():
            info["dfsno"] = None

    def _number_postorder(self, node, num):
        self.set_node_attr(node, "dfsno", True)
        succ = self.succ(node)
        # TODO: If not using reverse, numbering changes to less natural, but
        # algos which depend on postorder should not?
        succ.sort(reverse=True)
        for n in succ:
            if not self.get_node_attr(n, "dfsno", None):
                num = self._number_postorder(n, num)
        self.set_node_attr(node, "dfsno", num)
        #print("Setting %s to %s" % (node, num))
        num += 1
        return num

    def number_postorder(self):
        "Number nodes in depth-first search post-order order."
        self.reset_numbering()
        assert len(self._entries) == 1
        node = self._entries[0]
        return self._number_postorder(node, 1)
