from graph import Graph
from core import *


# Apply tranformation while it's possible
def apply_iterative(func, args):
    cnt = 0
    while func(*args):
        cnt += 1
    print("Ran %s %d times" % (func, cnt))

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
