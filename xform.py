from graph import Graph


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
    for v, b in cfg.iter_nodes():
        # If node is not entry, has a single exit and empty
        if cfg.degree_in(v) > 0 and cfg.degree_out(v) == 1 and not cfg.node(v).l:
            cfg.move_pred(v, cfg.succ(v)[0])
            cfg.remove_node(v)
            print("jump_over_jump: removed node:", v)
            return True
