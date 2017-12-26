import sys
import re

# Simple module to output graph as .dot file, which can be viewed
# with dot or xdot.py tools.
def dot(graph, out=sys.stdout, directed=None, is_cfg=True):
    if directed is None:
        directed = graph.directed
    if directed:
        header = "digraph"
        edge = "->"
    else:
        header = "graph"
        edge = "--"

    out.write("%s G {\n" % header)
    if is_cfg:
        entries = graph.entries()
        if entries and (len(entries) > 1 or entries[0] != ".ENTRY"):
            for e in sorted(entries):
                out.write('"%s" %s "%s"\n' % ("ENTRY", edge, e))

    for addr, info in graph.iter_sorted_nodes():
        obj = info.get("val")
        if obj is not None:
            typ = type(obj).__name__
            label = "%s\\n%s" % (typ, addr)
        else:
            label = addr
        if "dfsno" in info:
            label += "(#%s)" % info["dfsno"]
        if info.get("dfsno_exit"):
            label += "(e#%s)" % info["dfsno_exit"]
        if "idom" in info:
            label += "\nidom: %s" % info["idom"]
        out.write('"%s" [label="%s"]\n' % (addr, label))

    for (fr, to), data in sorted(graph.iter_edges()):
        label = data.get("cond")
        succ = graph.succ(fr)
        if is_cfg and label is None and len(succ) == 2:
            label = "else"
        if label:
            out.write('"%s" %s "%s" [label="%s"]\n' % (fr, edge, to, label))
        else:
            out.write('"%s" %s "%s"\n' % (fr, edge, to))
    out.write("}\n")


def unquote(s):
    if s[0] == '"' and s[-1] == '"':
        return s[1:-1]
    return s


def parse(f, graph):
    l = f.readline()
    assert l.startswith("graph") or l.startswith("digraph")
    for l in f:
        if l.strip() == "}":
            break
        fields = re.split(r"-[->]", l, 1)
        fields = [x.strip() for x in fields]
        graph.add_edge(unquote(fields[0]), unquote(fields[1]))
    return graph



cnt = 1


def save_dot(cfg, suffix):
    with open(cfg.filename + ".dot" + suffix, "w") as out:
        dot(cfg, out)


def debug_dot(g):
    global cnt
    with open("_graph.%02d.dot" % cnt, "w") as f:
        dot(g, f)
    cnt += 1
