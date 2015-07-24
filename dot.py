import sys
import re

# Simple module to output graph as .dot file, which can be viewed
# with dot or xdot.py tools.
def dot(graph, out=sys.stdout, directed=None):
    if directed is None:
        directed = graph.directed
    if directed:
        header = "digraph"
        edge = "->"
    else:
        header = "graph"
        edge = "--"

    out.write("%s G {\n" % header)
    for e in graph.entries():
        out.write('"%s" %s "%s"\n' % ("ENTRY", edge, e))

    for addr, info in graph.iter_sorted_nodes():
        obj = info["val"]
        typ = type(obj).__name__
        out.write('"%s" [label="%s\\n%s"]\n' % (addr, typ, addr))

    for (fr, to), label in sorted(graph.iter_edges()):
        succ = graph.succ(fr)
        if label is None and len(succ) == 2:
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
