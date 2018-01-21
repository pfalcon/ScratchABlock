import sys
import re

from core import BBlock
from decomp import IfElse, While


show_insts = False


def write_indented(out, level, s):
    out.write("  " * level + s)


def out_bblock_node(obj, out, level):
        addr = obj.addr
        if obj is not None:
            typ = type(obj).__name__
            label = "%s: %s" % (addr, typ)
        else:
            label = addr

        if show_insts:
            for inst in obj:
                label += "\n" + str(inst)
        write_indented(out, level, '"%s" [label="%s"]\n' % (addr, label))

        return (addr, addr)


def subgraph(obj, out, level=0):
    if type(obj) is BBlock:
        return out_bblock_node(obj, out, level)
    else:
        uniq_sfx = "%d_%s" % (level, obj.addr)
        write_indented(out, level, 'subgraph "cluster_%s" {\n' % uniq_sfx)
        write_indented(out, level+1, "label=%s\n" % type(obj).__name__)
        my_first_n = None
        prev_n = None

        if isinstance(obj, IfElse):
            my_first_n, prev_n = subgraph(obj.header, out, level + 1)
            landing = "landing_%s" % uniq_sfx
            for cond, block in obj.branches:
                if block is None:
                    write_indented(out, level+1, '"%s" -> "%s" [label="else"]\n' % (prev_n, landing))
                else:
                    first_n, last_n = subgraph(block, out, level + 1)
                    if cond is None:
                        cond = "else"
                    write_indented(out, level+1, '"%s" -> "%s" [label="%s"]\n' % (prev_n, first_n, cond))
                    write_indented(out, level+1, '"%s" -> "%s"\n' % (last_n, landing))
            write_indented(out, level+1, '"%s" [shape=point label=""]\n' % landing)
            prev_n = landing
        elif isinstance(obj, While):
            write_indented(out, level+1, '"%s" [shape=circle width=0.3 fixedsize=true label="%s"]\n' % (obj.addr, obj.addr))
            first_n, last_n = subgraph(obj.items[0], out, level + 1)
            write_indented(out, level+1, '"%s" -> "%s"\n' % (obj.addr, first_n))
            write_indented(out, level+1, '"%s" -> "%s"\n' % (last_n, obj.addr))
            prev_n = last_n

            # We render a simplified While representation using above, because
            # trying to add more edges below for fully faithful representation
            # doesn't work well, subgraph gets crowded and with rendering artifacts.
            #landing = "landing_%d_%s" % (level, obj.addr)
            #write_indented(out, level+1, '"%s" [shape=point label=""]\n' % landing)
            #write_indented(out, level+1, '"%s" -> "%s"\n' % (obj.addr, landing))
            #write_indented(out, level+1, '"%s" -> "%s" [style="invis" weight=100]\n' % (last_n, landing))
            #prev_n = obj.addr
            #prev_n = landing
        else:
          for o in obj.subblocks():
            first_n, last_n = subgraph(o, out, level + 1)

            if my_first_n is None:
                my_first_n = first_n

            if prev_n:
                write_indented(out, level+1, '"%s" -> "%s"\n' % (prev_n, first_n))
            prev_n = last_n

        write_indented(out, level, "}\n")
        return (my_first_n, prev_n)


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
    out.write("node [shape=box]\n")
    if is_cfg:
        entries = graph.entries()
        if entries and (len(entries) > 1 or entries[0] != ".ENTRY"):
            for e in sorted(entries):
                out.write('"%s" %s "%s"\n' % ("ENTRY", edge, e))

    block_end_map = {}

    for addr, info in graph.iter_sorted_nodes():
        obj = info.get("val")
        if obj is not None:
            typ = type(obj).__name__
            label = "%s: %s" % (addr, typ)
        else:
            label = addr
        if "dfsno" in info:
            label += "(#%s)" % info["dfsno"]
        if info.get("dfsno_exit"):
            label += "(e#%s)" % info["dfsno_exit"]
        if "idom" in info:
            label += "\nidom: %s" % info["idom"]

        if type(obj) is BBlock:
            if show_insts:
                for inst in obj:
                    label += "\n" + str(inst)
            out.write('"%s" [label="%s"]\n' % (addr, label))
            block_end_map[addr] = addr
        else:
            first, last = subgraph(obj, out)
            block_end_map[addr] = last

    for (fr, to), data in sorted(graph.iter_edges()):
        label = data.get("cond")
        succ = graph.succ(fr)
        if is_cfg and label is None and len(succ) == 2:
            label = "else"
        if label:
            out.write('"%s" %s "%s" [label="%s"]\n' % (block_end_map[fr], edge, to, label))
        else:
            out.write('"%s" %s "%s"\n' % (block_end_map[fr], edge, to))
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
