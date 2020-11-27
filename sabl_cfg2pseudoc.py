#!/usr/bin/env python3
import sys
import re
from collections import defaultdict

from graph import Graph
from utils import pairwise, natural_sort_key


def node_name_strip(s):
    s = s.strip()
    if s[0] == '"' and s[-1] == '"':
        s = s[1:-1]
    return s


def parse_dot(f):
    cfg = Graph()

    for l in f:
        l = l.strip()
        if l.startswith("digraph"):
            continue
        if l == "}":
            break
        l = re.sub(r"\[.+\]$", "", l)
        if "->" not in l:
            continue
        nodes = [node_name_strip(n) for n in l.split("->")]

        for from_n, to_n in pairwise(nodes, trailing=False):
            cfg.add_edge(from_n, to_n)

    return cfg


def __main__():
    with open(sys.argv[1]) as f:
        cfg = parse_dot(f)

    all_nodes = sorted(cfg.nodes(), key=natural_sort_key)

    for n, next_n in pairwise(all_nodes):
        print("%s:" % n)
        print("  nop()")
        succ = cfg.succ(n)
        if len(succ) == 0:
            print("  return")
        elif len(succ) == 1:
            if succ[0] != next_n:
                print("  goto %s" % succ[0])
        else:
            old_len = len(succ)
            succ = [x for x in succ if x != next_n]
            else_node = None
            if len(succ) == old_len:
                # next_n wasn't in succ
                else_node = succ[-1]
                succ = succ[:-1]
            s = ", ".join(["($cond) goto %s" % x for x in succ])
            if else_node:
                s += ", else goto %s" % else_node
            print("  if " + s)


if __name__ == "__main__":
    __main__()
