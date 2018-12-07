"Adhoc/optimized routines for dominators."

def intersect(g, i, j):
    finger1 = i
    finger2 = j
    while finger1 != finger2:
        while -g[finger1]["postno"] > -g[finger2]["postno"]:
            finger1 = g[finger1]["idom"]
        while -g[finger2]["postno"] > -g[finger1]["postno"]:
            finger2 = g[finger2]["idom"]
    return finger1


# Cooper 9.5.2
def compute_idom(g):
    for n, info in g.nodes_props():
        info["idom"] = None

    entry = g.entry()
    g[entry]["idom"] = entry
    changed = True
    while changed:
        changed = False
        it = iter(g.iter_rev_postorder())
        # Skip root
        next(it)
        for n in it:
            preds_rpo = sorted([(-g[p]["postno"], p) for p in g.pred(n)])
            new_idom = preds_rpo[0][1]
            for _, p in preds_rpo[1:]:
                if g[p]["idom"] is not None:
                    new_idom = intersect(g, p, new_idom)
            if g[n]["idom"] != new_idom:
                g[n]["idom"] = new_idom
                changed = True

    g[entry]["idom"] = None
