from xform import *

def apply(cfg):
    # Various algos below require single-exit CFG
    cfg_single_exit(cfg)

    foreach_bblock(cfg, sub_const_to_add)

    analyze_live_vars(cfg)
    insert_initial_regs(cfg)

    analyze_reach_defs(cfg)
    #const_propagation(cfg)
    #copy_propagation(cfg)
    #mem_propagation(cfg)
    expr_propagation(cfg)

    analyze_live_vars(cfg)
    estimate_params(cfg)
    foreach_bblock(cfg, dead_code_elimination)

    collect_calls(cfg)
