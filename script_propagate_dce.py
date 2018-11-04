from xform import *
from dataflow import *


def apply(cfg):
    # Various algos below don't work with no explicit entry in CFG
    cfg_preheader(cfg)
    # Also don't work with >1 entries
    remove_unreachable_entries(cfg)
    # Various algos below require single-exit CFG
    cfg_single_exit(cfg)

    foreach_inst(cfg, sub_const_to_add)
    # Initial pass on simplifying expressions
    foreach_inst(cfg, simplify_inst)

    analyze_live_vars(cfg)
    insert_initial_regs(cfg)

    analyze_reach_defs(cfg)
    make_du_chains(cfg)
    #const_propagation(cfg)
    #copy_propagation(cfg)
    #mem_propagation(cfg)
    expr_propagation(cfg)

    analyze_live_vars(cfg)
    estimate_params(cfg)
    foreach_bblock(cfg, dead_code_elimination)

    collect_calls(cfg)
