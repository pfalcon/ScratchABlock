def swap_if_branches(cfg, node):
    "Assuming `node` is 'if' node, swap its branches and invert condition."
    succ = cfg.sorted_succ(node)
    print(succ, cfg[node, succ[0]])
    cond = cfg[node, succ[0]]["cond"]
    cfg[node, succ[0]]["cond"] = None
    cfg[node, succ[1]]["cond"] = cond.neg()


def foreach_bblock(cfg, func, join_func=lambda a, b: a or b):
    """Apply basic-block level transformation to each block in CFG.
    Return cumulative status (OR of each block's status).
    """
    res = Ellipsis
    for addr, info in cfg.iter_sorted_nodes():
        bblock = info["val"]
        r = func(bblock)
        if res is Ellipsis:
            res = r
        else:
            res = join_func(res, r)
    return res


def foreach_inst(cfg, func):
    def inst_handler(bblock):
        for inst in bblock.items:
            func(inst)
    foreach_bblock(cfg, inst_handler)
