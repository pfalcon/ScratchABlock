from xform import *

def apply(cfg):
    # Various algos below require single-exit CFG
    cfg_single_exit(cfg)

    foreach_bblock(cfg, sub_const_to_add)
    insert_sp0(cfg)

    analyze_reach_defs(cfg)
    #const_propagation(cfg)
    #copy_propagation(cfg)
    #mem_propagation(cfg)
    expr_propagation(cfg)

    estimate_args(cfg)
    analyze_live_vars(cfg)
    foreach_bblock(cfg, dead_code_elimination)

    collect_calls(cfg)
