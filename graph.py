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
        self._nodes[node] = value
        if not self._entries:
            self._entries.append(node)

    def add_edge(self, from_node, to_node, label=None):
        """Add edge between 2 nodes. If any of the nodes does not exist,
        it will be created."""
        self._edges[(from_node, to_node)] = label
        self._succ[from_node].append(to_node)
        self._pred[to_node].append(from_node)

    def node(self, n):
        return self._nodes[n]

    def edge(self, from_node, to_node):
        return self._edges[(from_node, to_node)]

    def succ(self, n):
        "Return successors of a node."
        return self._succ[n]

    def pred(self, n):
        "Return predecessors of a node."
        return self._pred[n]

    def __contains__(self, val):
        if isinstance(val, tuple):
            return val in self._edges
        else:
            return val in self._nodes

    def iter_sorted_nodes(self):
        return sorted(self._nodes.items(), key=lambda x: x[0])

    def iter_edges(self):
        return self._edges.items()

    def entries(self):
        return self._entries
