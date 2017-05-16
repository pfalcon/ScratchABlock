from xform import *
from dataflow import *

def apply(cfg):
    # Various algos below require single-entry CFG
    remove_unreachable_entries(cfg)
    # And single exit
    cfg_single_exit(cfg)

    foreach_bblock(cfg, sub_const_to_add)

    # Need to do before DCE and even before insert_initial_regs
    collect_reach_exit(cfg)

    analyze_live_vars(cfg)
    insert_initial_regs(cfg)

    analyze_reach_defs(cfg)

    #const_propagation(cfg)
    #copy_propagation(cfg)
    #mem_propagation(cfg)
    # May infinite-loop without $sp_0, etc.
    expr_propagation(cfg)

    # To rewrite stack vars, we need to propagate $sp_0, hence all the above
    foreach_bblock(cfg, rewrite_stack_vars, rewrite_to=REG)

    # Now need to do second propagation phase, of stack vars
    analyze_reach_defs(cfg)
    expr_propagation(cfg)

    # Analyze and record preserved registers
    collect_preserveds(cfg)

    cfg.props["modifieds"] = cfg.props["reach_exit"] - cfg.props["preserveds"]

    analyze_live_vars(cfg)
    estimate_params(cfg)
