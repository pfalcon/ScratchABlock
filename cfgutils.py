def swap_if_branches(cfg, node):
    "Assuming `node` is 'if' node, swap its branches and invert condition."
    succ = cfg.sorted_succ(node)
    print(succ, cfg[node, succ[0]])
    cond = cfg[node, succ[0]]["cond"]
    cfg[node, succ[0]]["cond"] = None
    cfg[node, succ[1]]["cond"] = cond.neg()
