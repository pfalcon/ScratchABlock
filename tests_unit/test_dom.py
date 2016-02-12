import dataflow
import graph
import dot


def test_cooper_9_2_1():
    g = graph.Graph()
    [g.add_node(i) for i in range(8 + 1)]
    for e in [(0, 1), (1, 2), (1, 5), (2, 3), (3, 4), (3, 1), (5, 6), (5, 8), (6, 7), (7, 3), (8, 7)]:
        g.add_edge(*e)

    #dot.dot(g)

    #g.print_nodes()
    analysis = dataflow.DominatorAnalysis(g)
    analysis.solve()
    #g.print_nodes()

    DOM = [
    {0},
    {0, 1},
    {0, 1, 2},
    {0, 1, 3},
    {0, 1, 3, 4},
    {0, 1, 5},
    {0, 1, 5, 6},
    {0, 1, 5, 7},
    {0, 1, 5, 8},
    ]

    for i, info in g.iter_sorted_nodes():
        assert info["dom"] == DOM[i]
