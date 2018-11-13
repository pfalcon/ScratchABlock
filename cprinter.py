import sys

from utils import pairwise, natural_sort_key
from cfgutils import swap_if_branches
import progdb

no_dead = False

def find_used_labels(cfg):
    labels = set()
    for addr, nxt in pairwise(cfg.iter_rev_postorder()):
        info = cfg[addr]
        bblock = info["val"]
        succs = cfg.sorted_succ(addr)
        if len(succs) > 1 and nxt == succs[0]:
            swap_if_branches(cfg, addr)
            succs = cfg.sorted_succ(addr)
        for succ in succs:
            cond = cfg.edge(addr, succ).get("cond")
            if not cond and nxt and succ == nxt:
                continue
            labels.add(succ)
    return labels


def print_inst(inst):
    if inst.op == "DEAD" and no_dead:
        return
    return str(inst)

def dump_c(cfg, stream=sys.stdout):
    labels = find_used_labels(cfg)
    func_start = True
    for addr, nxt in pairwise(cfg.iter_rev_postorder()):
        info = cfg[addr]
        bblock = info["val"]
        if func_start:
            label = cfg.props["name"]
            if not label:
                label = cfg.parser.label_from_addr(bblock.addr)
            if label[0].isdigit():
                label = "fun_" + label
            if ("estimated_params" in cfg.props):
                print("// Estimated params: %s" % sorted(list(cfg.props["estimated_params"])), file=stream)
            if cfg.props["trailing_jumps"]:
                print("// Trailing jumps not removed, not rendering CFG edges as jumps", file=stream)

            func_props = progdb.FUNC_DB.get(label, {})
            params = ""
            if "params" in func_props:
                params = sorted(func_props["params"], key=natural_sort_key)
                params = ", ".join(["u32 " + str(r) + "_0" for r in params])
            print("void %s(%s)\n{" % (label, params), file=stream)
            func_start = False
        if addr in labels:
            print("\nl%s:" % addr, file=stream)
        bblock.dump(stream, indent=1, printer=print_inst)
        if not cfg.props["trailing_jumps"]:
          for succ in cfg.succ(addr):
            cond = cfg.edge(addr, succ).get("cond")
            if not cond and nxt and succ == nxt:
                continue
            stream.write("  ")
            if cond:
                stream.write("if %s " % cond)
            print("goto l%s;" % succ, file=stream)

    print("}", file=stream)
