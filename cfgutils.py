from core import BBlock


def swap_if_branches(cfg, node):
    "Assuming `node` is 'if' node, swap its branches and invert condition."
    succ = cfg.sorted_succ(node)
    print(succ, cfg[node, succ[0]])
    cond = cfg[node, succ[0]]["cond"]
    cfg[node, succ[0]]["cond"] = None
    cfg[node, succ[1]]["cond"] = cond.neg()


def detach_node(cfg, n):
    din = cfg.degree_in(n)
    dout = cfg.degree_out(n)
    assert din == 1 or dout == 1
    if din == 1:
        pred = cfg.pred(n)[0]
        cfg.move_succ(n, pred)
    else:
        succ = cfg.succ(n)[0]
        cfg.move_pred(n, succ)
    cfg.remove_node(n)


def foreach_node(cfg, func):
    """Call function for each node of graph, passing node's properties.
    """
    for addr, info in cfg.iter_sorted_nodes():
        func(info)


def foreach_bblock(cfg, func, join_func=lambda a, b: a or b, **kwargs):
    """Apply basic-block level transformation to each block in CFG.
    Return cumulative status (OR of each block's status).
    """
    res = Ellipsis
    for addr, info in cfg.iter_sorted_nodes():
        bblock = info["val"]
        r = func(bblock, **kwargs)
        if res is Ellipsis:
            res = r
        else:
            res = join_func(res, r)
    return res


def foreach_bblock_and_subblock(cfg, func):
    def apply(bblock, func):
        if type(bblock) is BBlock:
            func(bblock)
        else:
            for sub in bblock.subblocks():
                apply(sub, func)

    for addr, info in cfg.iter_sorted_nodes():
        bblock = info["val"]
        apply(bblock, func)


def foreach_inst(cfg, func):
    def inst_handler(bblock):
        for inst in bblock.items:
            func(inst)
    foreach_bblock(cfg, inst_handler)
