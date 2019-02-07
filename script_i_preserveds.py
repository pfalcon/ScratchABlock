from xform import *
from dataflow import *

def apply(cfg):
    # script_i_prepare was run before this

    analyze_reach_defs(cfg)
    # Need to do before DCE and even before insert_initial_regs
    collect_reach_exit(cfg)
    collect_reach_exit_maybe(cfg)

    # analyze_live_vars uses modifieds, so if preserveds is available, we need
    # to update modifieds for possible update in reach_exit, otherwise we'll
    # have positive feedback in propagation and bad flip-flop effect for preserveds
    # value.
    if "preserveds" in cfg.props:
        cfg.props["modifieds"] = cfg.props["reach_exit"] - cfg.props["preserveds"]

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
