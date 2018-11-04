from xform import *
from dataflow import *

def apply(cfg):
    # Various algos below don't work with no explicit entry in CFG
    cfg_preheader(cfg)
    # Also don't work with >1 entries
    remove_unreachable_entries(cfg)
    # Also don't work unless there's a single exit
    cfg_single_exit(cfg)

    foreach_inst(cfg, sub_const_to_add)

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
    foreach_inst(cfg, rewrite_stack_vars, rewrite_to=REG)

    # Now need to do second propagation phase, of stack vars
    analyze_reach_defs(cfg)
    expr_propagation(cfg)

    # Analyze and record preserved registers
    collect_preserveds(cfg)

    cfg.props["modifieds"] = cfg.props["reach_exit"] - cfg.props["preserveds"]

    #
    # Argument estimation part
    #

    # Reanalyze live vars for DCE
    analyze_live_vars(cfg)
    # Eliminate any preservation assignments, and thus liveness of preserved regs
    foreach_bblock(cfg, dead_code_elimination)

    # Reanalyze live vars for argument estimation
    analyze_live_vars(cfg)
    estimate_params(cfg)
