# ScratchABlock - Program analysis and decompilation framework
#
# Copyright (c) 2015-2018 Paul Sokolovsky
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""Transformation passes on generic graphs (not CFGs)"""

from utils import make_set
import dot


def t1_transform(g, node):
    if g.has_edge(node, node):
        print("t1: yes", node)
        g.remove_edge(node, node)
        dot.debug_dot(g)
        return True
    return False


def t2_transform(g, node):
    if g.degree_in(node) == 1:
        print("t2: yes", node)
        pred = g.pred(node)[0]
        g.remove_edge(pred, node)
        g.move_succ(node, pred)
        g[pred].setdefault("folded", []).append(node)
        g.remove_node(node)
        dot.debug_dot(g)
        return True
    print("t2: no", node)
    return False


def reduce_graph(g):
    changed = True
    while changed:
        print("!iter")
        changed = False
        for node in list(g.nodes()):
            # Might have been deleted by previous iteration
            if node in g:
                changed |= t1_transform(g, node)
                changed |= t2_transform(g, node)


def recursive_relation(g, n, in_prop, out_prop, is_reflexive=False):
    "Helper function to compute relation closures, don't use directly."
    if out_prop in g[n]:
        return g[n][out_prop]
    if in_prop not in g[n]:
        return

    val = g[n][in_prop]
    if val is None:
        val = set()
    else:
        val = make_set(val)
    res = set()

    for rel_n in val:
        res |= recursive_relation(g, rel_n, in_prop, out_prop, is_reflexive)

    res |= val
    if is_reflexive:
        res |= {n}

    g[n][out_prop] = res
    return res


def transitive_closure(g, in_prop, out_prop):
    """Compute a transitive closure of some graph relation.

    in_prop: Name of node property storing relation (i.e.
             value of property should be id of another node).
    out_prop: Name of node property to store transitive closure
              of the relation.
    """

    for n, info in g.iter_nodes():
        recursive_relation(g, n, in_prop, out_prop, False)


def reflexive_transitive_closure(g, in_prop, out_prop):
    """Compute a reflexive-transitive closure of some graph relation.

    in_prop: Name of node property storing relation (i.e.
             value of property should be id of another node).
    out_prop: Name of node property to store transitive closure
              of the relation.
    """

    for n, info in g.iter_nodes():
        recursive_relation(g, n, in_prop, out_prop, True)


def idom_to_sdom(g):
    transitive_closure(g, "idom", "sdom")


def idom_to_dom(g):
    reflexive_transitive_closure(g, "idom", "dom")


def idom_children(g, node):
    """Return children of idom node.

    The implementation here is very inefficient.
    """

    res = []
    for n, info in g.iter_nodes():
        if info["idom"] == node:
            res.append(n)
    return res


def idom_transitive_dom(g, node1, node2):
    "Check whether node1 dominates node2, by walking idom chain."
    while node2 is not None:
        if node1 == node2:
            return True
        node2 = g[node2]["idom"]
    return False


def compute_dom_frontier_cytron(g, node=None):
    """Compute dominance frontier of each node.

    Intuitively, dominance frontier of a node X is a set of
    successors of "last" nodes which X dominates. I.e., if
    X dominates A, but not its successor B, then B is in X's
    dominance frontier.

    Ref: Efficiently Computing Static Single Assignment Form and the Control
    Dependence Graph, Cytron, Ferrante, Rosen, Wegman, Zedeck
    Ref: Appel p.406.
    """

    if node is None:
        node = g.entry()

    df = set()

    for y in g.succ(node):
        if g[y]["idom"] != node:
            df.add(y)

    for z in idom_children(g, node):
        compute_dom_frontier_cytron(g, z)
        for y in g[z]["dom_front"]:
            if g[y]["idom"] != node:
                df.add(y)

    g[node]["dom_front"] = df
