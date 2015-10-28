from graph import *


def test_nodes_on_path_trivial():
    g = Graph()
    g.add_node("a")
    g.add_node("b")
    g.add_edge("a", "b")
    g.number_postorder()
    res = find_all_nodes_on_path(g, "a", "b")
    assert res == set(["a"]), res

def test_nodes_on_path_trivial_loop():
    g = Graph()
    g.add_node("a")
    g.add_edge("a", "a")
    g.number_postorder()
    res = find_all_nodes_on_path(g, "a", "a")
    assert res == set(["a"]), res

def test_nodes_on_path_disconnected():
    g = Graph()
    g.add_node("a")
    g.add_node("b")
    g.number_postorder()
    res = find_all_nodes_on_path(g, "a", "b")
    assert res == set()

def test_nodes_on_path():
    g = Graph()
    g.add_node("a")
    g.add_node("b")
    g.add_node("c")
    g.add_node("d")
    g.add_edge("a", "b")
    g.add_edge("a", "c")
    g.number_postorder()
    res = find_all_nodes_on_path(g, "a", "d")
    assert res == set(), res

    g.add_edge("b", "d")
    g.number_postorder()
    res = find_all_nodes_on_path(g, "a", "d")
    assert res == set(["a", "b"]), res

    g.add_edge("c", "d")
    g.number_postorder()
    res = find_all_nodes_on_path(g, "a", "d")
    assert res == set(["a", "b", "c"]), res

    g.add_edge("d", "a")
    g.number_postorder()
    res = find_all_nodes_on_path(g, "a", "d")
    assert res == set(["a", "b", "c"]), res

    res = find_all_nodes_on_path(g, "a", "a")
    assert res == set(["a", "b", "c", "d"]), res
