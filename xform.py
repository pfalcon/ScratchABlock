from graph import Graph
from core import *


# Apply tranformation while it's possible
def apply_iterative(func, args):
    cnt = 0
    while func(*args):
        cnt += 1
    print("Ran %s %d times" % (func, cnt))


def foreach_bblock(cfg, func):
    """Apply basic-block level transformation to each block in CFG.
    Return cumulative status (OR of each block's status).
    """
    res = False
    for addr, info in cfg.iter_sorted_nodes():
        bblock = info["val"]
        r = func(bblock)
        res = res or r
    return res


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
        if cfg.degree_in(v) > 0 and cfg.degree_out(v) == 1 and not cfg.node(v).items:
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
                b = cfg.node(p)
                if not b.items:
                    landing_site = p
            if not landing_site:
                farthest = max(back_preds)
                print("farthest", farthest)
                newb = BBlock(farthest + "_1")
                cfg.add_node(newb.addr, newb)
                cfg.add_edge(newb.addr, v)
                landing_site = newb.addr
            print("landing_site:", landing_site)
            for p in back_preds:
                if p != landing_site:
                    e = cfg.edge(p, v)
                    cfg.remove_edge(p, v)
                    cfg.add_edge(p, landing_site, e)
            return True