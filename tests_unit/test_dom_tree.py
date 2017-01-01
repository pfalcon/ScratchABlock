import graph
import dom


def test_idom():
    g = graph.Graph()
    [g.add_node(i) for i in range(8 + 1)]
    for e in [(0, 1), (1, 2), (1, 5), (2, 3), (3, 4), (3, 1), (5, 6), (5, 8), (6, 7), (7, 3), (8, 7)]:
        g.add_edge(*e)
    g.number_postorder()
    dom.compute_idom(g)
    #g.print_nodes()

    RES = [
        {'dfsno': 9, 'idom': None},
        {'dfsno': 8, 'idom': 0},
        {'dfsno': 7, 'idom': 1},
        {'dfsno': 2, 'idom': 1},
        {'dfsno': 1, 'idom': 3},
        {'dfsno': 6, 'idom': 1},
        {'dfsno': 5, 'idom': 5},
        {'dfsno': 3, 'idom': 5},
        {'dfsno': 4, 'idom': 5},
    ]

    assert [d[1] for d in g.iter_sorted_nodes()] == RES
