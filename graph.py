import sys
import copy
from collections import defaultdict


class Graph:
    """Nodes in a graph are identified by IDs and contain property dictionaries.
    A graph maps node ID to node properties:

    node_props = G[node_id]

    A specific node property thus can be accessed as:

    prop_val = G[node_id][prop_name]

    The "default" property, a "value" of node, is by convention in a property named
    "val".

    Edges in a graph are identified by a pair of node IDs. They also have associated
    property dictionary:

    edge_props = G[(node_id1, node_id2)]

    """

    directed = True

    def __init__(self):
        self._nodes = {}
        self._edges = {}
        self._succ = defaultdict(list)
        self._pred = defaultdict(list)
        self.first_node = None

    def add_node(self, node, **attrs):
        """Add node to a graph. node is an ID of a node (usually lightweight
        scalar value, but can be any immutable value). Arbitrary attributes
        can be associated with a node, e.g. "val" attribute for node's "value".
        """
        if node in self._nodes:
            self._nodes[node].update(attrs)
        else:
            self._nodes[node] = attrs
        # Many algos need proper-entry graph, and if graph is not
        # (e.g., has a loop backedge to entry), it's not possible
        # to detect such entry without explicit pointing or
        # heuristics. We use the latter here - first node added is
        # an entry.
        if self.first_node is None:
            self.first_node = node

    def remove_node(self, node):
        for s in self._succ[node][:]:
            self.remove_edge(node, s)
        for p in self._pred[node][:]:
            self.remove_edge(p, node)
        del self._nodes[node]
        del self._succ[node]
        del self._pred[node]

    def node(self, n):
        return self._nodes[n]

    # Allow to index graph to access node or edge data
    # graph[node], graph[from_n, to_n]
    def __getitem__(self, idx):
        if isinstance(idx, tuple):
            return self.edge(*idx)
        else:
            return self.node(idx)

    def set_node_attr(self, node, attr, val):
        self._nodes[node][attr] = val

    def get_node_attr(self, node, attr, default=Ellipsis):
        if default is Ellipsis:
            return self._nodes[node][attr]
        else:
            return self._nodes[node].get(attr, default)


    def add_edge(self, from_node, to_node, **attrs):
        """Add edge between 2 nodes. If any of the nodes does not exist,
        it will be created."""
        if (from_node, to_node) in self._edges:
            self._edges[(from_node, to_node)].update(attrs)
        else:
            self._edges[(from_node, to_node)] = attrs
            self._succ[from_node].append(to_node)
            self._pred[to_node].append(from_node)

    set_edge = add_edge

    def remove_edge(self, from_node, to_node):
        del self._edges[(from_node, to_node)]
        self._succ[from_node].remove(to_node)
        self._pred[to_node].remove(from_node)

    def edge(self, from_node, to_node):
        return self._edges[(from_node, to_node)]

    def has_edge(self, from_node, to_node):
        return (from_node, to_node) in self._edges

    def is_back_edge(self, from_node, to_node):
        return self[from_node]["dfsno"] < self[to_node]["dfsno"]

    def succ(self, n):
        "Return successors of a node."
        return self._succ[n][:]

    def sorted_succ(self, n):
        """Return successors ordered the way that successor with labeled
        edge comes first. Assumes 2 succesors."""
        succ = self.succ(n)
        if len(succ) < 2:
            return succ
        assert len(succ) == 2
        if self.edge(n, succ[0]).get("cond") is None:
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

    def nodes(self):
        "Return set of all nodes"
        return self._nodes.keys()

    def iter_nodes(self):
        return self._nodes.items()

    def iter_sorted_nodes(self):
        return sorted(self._nodes.items(), key=lambda x: x[0])

    def iter_edges(self):
        return self._edges.items()

    def entries(self):
        # TODO: Will also return single disconnected nodes
        entries = [n for n in self._nodes if not self._pred[n]]
        if entries:
            return entries
        return [self.first_node]

    def entry(self):
        e = self.entries()
        assert len(e) == 1, "Num entries: %d" % len(e)
        return e[0]

    def exits(self):
        # TODO: Will also return single disconnected nodes
        return [n for n in self._nodes if not self._succ[n]]

    def move_pred(self, from_node, to_node):
        """Move all predecessor edges from one node to another. Useful in
        graph transformations involving node folding."""
        for p in self.pred(from_node):
            self.add_edge(p, to_node, **self._edges[(p, from_node)])
            self.remove_edge(p, from_node)

    def move_succ(self, from_node, to_node):
        """Move all succesor edges from one node to another. Useful in
        graph transformations involving node folding."""
        for p in self.succ(from_node):
            self.add_edge(to_node, p, **self._edges[(from_node, p)])
            self.remove_edge(from_node, p)

    def __repr__(self):
        return "<Graph nodes=%r edges=%r pred=%r succ=%r>" % (self._nodes, self._edges, self._pred, self._succ)

    def print_nodes(self, stream=sys.stdout):
        "Print nodes of a graph with all attributes. Useful for debugging."
        for i, info in self.iter_sorted_nodes():
            print("%s\t%s" % (i, info))

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
        entries = self.entries()
        assert len(entries) == 1
        node = entries[0]
        return self._number_postorder(node, 1)

    def iter_postorder(self):
        return sorted(self._nodes.items(), key=lambda x: x[1]["dfsno"])

    def iter_rev_postorder(self):
        return sorted(self._nodes.items(), key=lambda x: -x[1]["dfsno"])

    def copy(self):
        # TODO: not optimal
        return copy.deepcopy(self)


def find_all_nodes_on_path(cfg, from_n, to_n):
    """Find set of nodes which lie on all paths from from_n to to_n.
    from_n and to_b can be a same node to process a loop. Result includes
    from_n and excludes to_n, if they are different nodes (but node
    looping to itself gives result of itself).
    """
    on_path = set()

    stack = [(from_n, [from_n])]
    while stack:
        cur_n, path = stack.pop()
        succ = cfg.succ(cur_n)
        dfsno = cfg.get_node_attr(cur_n, "dfsno")
        assert dfsno is not None
        print("Considering %s, dfsno: %s, succ: %s, cur path: %s" % (cur_n, dfsno, succ, path))

        if not succ:
            print("Found sink path, pruning")

        for s in succ:
            if s == to_n:
                on_path.update(path)
                print("Found full path, joining all path nodes")
            else:
                no = cfg.get_node_attr(s, "dfsno", None)
                if no is None:
                    print("Unmarked node detected (edge %s->%s)" % (cur_n, s))
                    assert False
                if no < dfsno:
                    stack.append((s, path + [s]))
                else:
                    # prune path
                    print("Found far backedge (%s, %s), pruning this path" % (cur_n, s))
    return on_path
