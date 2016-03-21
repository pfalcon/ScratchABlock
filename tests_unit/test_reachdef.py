import graph
import dot
from core import *
import dataflow


def test_nielson_2_1_2():
    b1 = BBlock(1)
    b1.add(Inst("x", "=", [5], 1))
    b2 = BBlock(2)
    b2.add(Inst("y", "=", [1], 2))
    b3 = BBlock(3)
    b3.add(Inst(None, "while", ["x > 1"], 3))
    b4 = BBlock(4)
    b4.add(Inst("y", "add", ["x", "y"], 4))
    b5 = BBlock(5)
    b5.add(Inst("x", "sub", ["x", 1], 5))
    g = graph.Graph()
    g.add_node(1, b1)
    g.add_node(2, b2)
    g.add_node(3, b3)
    g.add_node(4, b4)
    g.add_node(5, b5)
    g.add_edge(1, 2)
    g.add_edge(2, 3)
    g.add_edge(3, 4)
    g.add_edge(4, 5)
    g.add_edge(5, 3)

    #dot.dot(g)
    #ana = ReachDefAnalysis()
    #ana.init(g)
    #g.print_nodes()
    #print("===")

    ana = dataflow.ReachDefAnalysis(g)
    ana.solve()
    #g.print_nodes()

    RD_entry = {
        1: {("x", None), ("y", None)},
        2: {("y", None), ("x", 1)},
        3: {("x", 1), ("y", 2), ("y", 4), ("x", 5)},
        4: {("x", 1), ("y", 2), ("y", 4), ("x", 5)},
        5: {("x", 1), ("y", 4), ("x", 5)},
    }

    RD_exit = {
        1: {("y", None), ("x", 1)},
        2: {("x", 1), ("y", 2)},
        3: {("x", 1), ("y", 2), ("y", 4), ("x", 5)},
        4: {("x", 1), ("y", 4), ("x", 5)},
        5: {("y", 4), ("x", 5)},
    }

    for i, info in g.iter_sorted_nodes():
        assert info["reachdef_in"] == RD_entry[i]
        assert info["reachdef_out"] == RD_exit[i]
