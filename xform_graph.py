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
