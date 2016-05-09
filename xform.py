from graph import Graph
from core import *
from cfgutils import *
from dce import *
import arch


# Apply tranformation while it's possible
def apply_iterative(func, args):
    cnt = 0
    while func(*args):
        cnt += 1
    print("Ran %s %d times" % (func, cnt))


def remove_trailing_jumps(bblock):
    """Trailing jumps are encoded as out edges of basic block, and
    superfluous for most deeper transformations (but useful for
    surface transformations which should maintain instruction
    correspondence to the original input). This pass removes them.
    """
    last_jump = None
    for i in range(len(bblock.items) -1, -1, -1):
        if bblock.items[i].op in ("goto", "if"):
            last_jump = i
        else:
            break
    if last_jump is not None:
        #print("Removing: ", bblock.items[last_jump:])
        del bblock.items[last_jump:]


# Remove any jumps to jumps, replacing destination of first jump
# to be destination of 2nd.
# This "simplifies" graph, but makes it irregular. This is useful
# transformation for generating machine code, but for decompilation,
# it actually makes sense to add extra jump landing sites to make
# loops irregular.
#
# http://en.wikipedia.org/wiki/Jump_threading
#
def remove_jump_over_jump(cfg):
    for v, _ in cfg.iter_nodes():
        # If node is not entry, has a single exit and empty
        if cfg.degree_in(v) > 0 and cfg.degree_out(v) == 1 and not cfg.node(v)["val"].items:
            cfg.move_pred(v, cfg.succ(v)[0])
            cfg.remove_node(v)
            print("jump_over_jump: removed node:", v)
            return True

# If possible, make a single back-edge to a loop header, by introducing
# intermediate jump landing nodes.
def loop_single_entry(cfg):
    for v, _ in cfg.iter_nodes():
        if cfg.degree_in(v) >= 2:
            preds = cfg.pred(v)
            back_preds = list(filter(lambda x: v <= x, preds))
            if len(back_preds) < 2:
                continue
            print("loop_single_entry: node:", v)
            print("back_preds:", back_preds)
            back_jumps = list(filter(lambda x: cfg.degree_out(x) == 1, back_preds))
            print("back_jumps:", back_jumps)
            # find existing landing site
            landing_site = None
            for p in back_jumps:
                b = cfg.node(p)["val"]
                if not b.items:
                    landing_site = p
            if not landing_site:
                farthest = max(back_preds)
                print("farthest", farthest)
                newb = BBlock(farthest + "_1")
                cfg.add_node(newb.addr, val=newb)
                cfg.add_edge(newb.addr, v)
                landing_site = newb.addr
            print("landing_site:", landing_site)
            for p in back_preds:
                if p != landing_site:
                    e = cfg.edge(p, v).get("cond")
                    cfg.remove_edge(p, v)
                    cfg.add_edge(p, landing_site, cond=e)
            return True


def bblock_const_propagation(bblock):
    subst = {}
    for i, inst in enumerate(bblock.items):

        all_args_const = True
        for arg_no, arg in enumerate(inst.args):
            if arg in subst:
                arg = subst[arg]
                inst.args[arg_no] = arg
            if not isinstance(inst.args[arg_no], VALUE):
                all_args_const = False

        if all_args_const:
            res = None
            base = 10
            if inst.op == "+":
                res = (inst.args[0].val + inst.args[1].val) % 2**arch.BITNESS
                base = max([a.base for a in inst.args])

            if res is not None:
                inst.op = "="
                inst.args = [VALUE(res, base)]

        if inst.op == "=" and isinstance(inst.args[0], (VALUE, ADDR)):
            subst[inst.dest] = inst.args[0]


import dataflow
def analyze_live_vars(cfg):
    ana = dataflow.LiveVarAnalysis(cfg)
    ana.solve()
