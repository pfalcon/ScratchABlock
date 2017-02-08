import sys

from utils import pairwise
from cfgutils import swap_if_branches

no_dead = False

def find_used_labels(cfg):
    labels = set()
    for (addr, info), nxt in pairwise(cfg.iter_rev_postorder()):
        bblock = info["val"]
        succs = cfg.sorted_succ(addr)
        if len(succs) > 1 and nxt[0] == succs[0]:
            swap_if_branches(cfg, addr)
            succs = cfg.sorted_succ(addr)
        for succ in succs:
            cond = cfg.edge(addr, succ).get("cond")
            if not cond and nxt and succ == nxt[0]:
                continue
            labels.add(succ)
    return labels


def print_inst(inst):
    if inst.op == "DEAD" and no_dead:
        return
    return str(inst)

def dump_c(cfg):
    labels = find_used_labels(cfg)
    func_start = True
    for (addr, info), nxt in pairwise(cfg.iter_rev_postorder()):
        bblock = info["val"]
        if func_start:
            label = cfg.parser.label_from_addr(bblock.addr)
            if label[0].isdigit():
                label = "fun_" + label
            if ("estimated_args" in info):
                print("// Estimated arguments: %s" % sorted(list(info["estimated_args"])))
            print("void %s()\n{" % label)
            func_start = False
        if addr in labels:
            print("\nl%s:" % addr)
        bblock.dump(sys.stdout, indent=1, printer=print_inst)
        for succ in cfg.succ(addr):
            cond = cfg.edge(addr, succ).get("cond")
            if not cond and nxt and succ == nxt[0]:
                continue
            sys.stdout.write("  ")
            if cond:
                sys.stdout.write("if %s " % cond)
            print("goto l%s;" % succ)

    print("}")
