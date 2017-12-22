import graph
import dot
from core import *
import dataflow


def make_inst(g, addr, dest, op, *args):
    def make_arg(a):
        if a is None:
            return None
        if isinstance(a, int):
            return VALUE(a)
        if isinstance(a, str):
            return REG(a)
        return a
    b = BBlock(addr)
    args = [make_arg(a) for a in args]
    b.add(Inst(make_arg(dest), op, args, addr))
    g.add_node(addr, val=b)

def test_nielson_2_1_4():
    g = graph.Graph()
    make_inst(g, 1, "x", "=", 2)
    make_inst(g, 2, "y", "=", 4)
    make_inst(g, 3, "x", "=", 1)
    make_inst(g, 4, None, "if", COND(EXPR(">", REG("x"), REG("y"))))
    make_inst(g, 5, "z", "=", REG("y"))
    make_inst(g, 6, "z", "*", REG("y"), REG("y"))
    make_inst(g, 7, "x", "=", REG("z"))
    g.add_edge(1, 2)
    g.add_edge(2, 3)
    g.add_edge(3, 4)

    g.add_edge(4, 5)
    g.add_edge(4, 6)
    g.add_edge(5, 7)
    g.add_edge(6, 7)

    #dot.dot(g)
    #ana = dataflow.LiveVarAnalysis(g)
    #ana.init()
    #g.print_nodes()
    #print("===")

    ana = dataflow.LiveVarAnalysis(g)
    ana.solve()
    #g.print_nodes()

    LV_entry = {
        1: set(),
        2: set(),
        3: {REG("y")},
        4: {REG("x"), REG("y")},
        5: {REG("y")},
        6: {REG("y")},
        7: {REG("z")},
    }

    LV_exit = {
        1: set(),
        2: {REG("y")},
        3: {REG("x"), REG("y")},
        4: {REG("y")},
        5: {REG("z")},
        6: {REG("z")},
        7: set(),
    }

    GEN_LV = {
        1: set(),
        2: set(),
        3: set(),
        4: {REG("x"), REG("y")},
        5: {REG("y")},
        6: {REG("y")},
        7: {REG("z")},
    }

    KILL_LV = {
        1: {REG("x")},
        2: {REG("y")},
        3: {REG("x")},
        4: set(),
        5: {REG("z")},
        6: {REG("z")},
        7: {REG("x")},
    }

    for i, info in g.iter_sorted_nodes():
        assert info["live_gen"] == GEN_LV[i]
        assert info["live_kill"] == KILL_LV[i]
        assert info["live_in"] == LV_entry[i], (info["live_in"], LV_entry[i])
        assert info["live_out"] == LV_exit[i]
