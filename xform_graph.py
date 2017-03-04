import dot


cnt = 1

def debug_out(g):
    global cnt
    with open("_graph.%02d.dot" % cnt, "w") as f:
        dot.dot(g, f)
    cnt += 1


def t1_transform(g, node):
    if g.has_edge(node, node):
        print("t1: yes", node)
        g.remove_edge(node, node)
        debug_out(g)
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
        debug_out(g)
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
