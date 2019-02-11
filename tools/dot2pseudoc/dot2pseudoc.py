import sys
import argparse

from dot_tools import parse
from dot_tools.dot_graph import SimpleGraph

class Block:
    def __init__(self, id):
        self.id = id
        self.fall_through = False # fall through to next node
        self.is_target = False    # smth jumps to this node
        self.edges = [] # outgoing edges except fall-through


def convert_graph(g, outf):
    blocks = []

    # build a lexically sorted list of target program blocks
    for node in sorted(g.nodes):
        if node == 'ENTRY':
            print("Skipping ENTRY node")
            continue

        block = Block(node)
        blocks.append(block)

    #print(blocks)

    # populate blocks list with edges (connections between blocks)
    for edge in g.edges:
        src = edge[0]
        dst = edge[1]
        #print("from %s to %s" % (src, dst))
        if src == 'ENTRY':
            print("Skipping ENTRY edge")
            continue

        src_blk = next((b for b in blocks if b.id == src), None)
        dst_blk = next((b for b in blocks if b.id == dst), None)
        src_idx = blocks.index(src_blk)
        dst_idx = blocks.index(dst_blk)

        if dst_idx == src_idx + 1:
            src_blk.fall_through = True
        else:
            src_blk.edges.append(dst_idx)
            dst_blk.is_target = True

    cond_reg = 0 # incremental condition register

    # generate target code
    for n,b in enumerate(blocks):
        if b.is_target: # create label
            outf.write("%s %s:\n" % (n, n))
        if len(b.edges) > 0:
            for i,edge in enumerate(b.edges):
                if not b.fall_through and i == len(b.edges) - 1:
                    outf.write("%s    goto %s\n" % (n, edge))
                else:
                    outf.write("%s    if ($r%s) goto %s\n" % (n, cond_reg, edge))
                    cond_reg += 1
        else:
            if b.fall_through: # there is a single fall-through edge
                outf.write("%s    nop()\n" % n)
            else: # no outgoing edges
                outf.write("%s    return\n" % n)


if __name__ == "__main__":
    argparser = argparse.ArgumentParser(
        description="Converts DOT graphs to PseudoC programs."
    )
    argparser.add_argument("infile", help='Input file in DOT format')
    argparser.add_argument("-o", "--output", help="output file (stdout by default)")

    args = argparser.parse_args()

    if args.output:
        outf = open(args.output, "w")
    else:
        outf = sys.stdout

    with open(args.infile, 'r') as f:
        dot_str = f.read()
        dot_ast = parse(dot_str)
        g = SimpleGraph.build(dot_ast.kid('Graph'))

    #print(g.nodes)
    #print(g.edges)

    convert_graph(g, outf)

    # close output file
    if outf is not sys.stdout:
        outf.close()
