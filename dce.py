import logging
from core import *


log = logging.getLogger(__file__)


def make_dead(insts, idx):
    org_inst = insts[idx]
    if org_inst.op == "DEAD":
        return
    if org_inst.side_effect():
        org_inst.dest = None
    else:
        insts[idx] = Inst(None, "DEAD", [])
        insts[idx].comments["org_inst"] = org_inst


def dead_code_elimination_forward(bblock):
    """Try to perform eliminations using forward flow. This is reverse
    to the natural direction, and requires multiple passing over
    bblock to stabilize. Don't use it, here only for comparison."""

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


def dead_code_elimination_backward(bblock):
    node = bblock.cfg[bblock.addr]
    live = node.get("live_out")
    if live is None:
        log.warn("BBlock %s: No live_out set, conservatively assuming all defined vars are live", bblock.addr)
        live = bblock.defs()
    live = live.copy()

    changes = False
    for i in range(len(bblock.items) - 1,  -1, -1):
        inst = bblock.items[i]
        if isinstance(inst.dest, REG):
            if inst.dest in live:
                live.remove(inst.dest)
            else:
                make_dead(bblock.items, i)
                changes = True
                inst = bblock.items[i]
        live |= inst.uses()

    return changes


dead_code_elimination = dead_code_elimination_backward
