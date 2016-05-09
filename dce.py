from core import *


def dead_code_elimination(bblock):
    def make_dead(insts, idx):
        org_inst = insts[idx]
        if org_inst.side_effect():
            org_inst.dest = None
        else:
            insts[idx] = Inst(None, "DEAD", [])
            insts[idx].comments["org_inst"] = org_inst

    vars = bblock.defs()
    for v in vars:
        last = None
        for i, inst in enumerate(bblock.items):
            if v in inst.args:
                last = None
            if inst.dest == v:
                if last is not None:
                    make_dead(bblock.items, last)
                last = i
        node = bblock.cfg[bblock.addr]
        live_out = node.get("live_out")
        if last is not None and live_out is not None:
            if v not in live_out:
                make_dead(bblock.items, last)
