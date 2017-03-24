from dom import *
from dataflow import *
from xform import *
from decomp import *


def propagate(cfg):
    analyze_reach_defs(cfg)
    make_du_chains(cfg)

    # Choose one, expr_propagation is required for true decompilation
    #const_propagation(cfg)
    #copy_propagation(cfg)
    #mem_propagation(cfg)
    expr_propagation(cfg)


def dce(cfg):
    analyze_live_vars(cfg)
    foreach_bblock(cfg, dead_code_elimination)


def structure(cfg):
    apply_iterative(match_seq, (cfg,))
    apply_iterative(match_if, (cfg,))
    apply_iterative(match_ifelse, (cfg,))
    apply_iterative(match_seq, (cfg,))
    apply_iterative(match_ifelse, (cfg,))
    apply_iterative(match_if_else_inv_ladder, (cfg,))
    apply_iterative(match_if_else_ladder, (cfg,))


def apply(cfg):
    #
    # Data flow
    #

    # Various algos below require single-exit CFG
    cfg_single_exit(cfg)

    foreach_bblock(cfg, sub_const_to_add)
    insert_sp0(cfg)

    propagate(cfg)

    # Estimate args only at the beginning of processing
    estimate_args(cfg)

    dce(cfg)

    #
    # Control flow
    #

    foreach_bblock(cfg, remove_trailing_jumps, remove_returns=True)
    remove_jump_over_jump(cfg)

    cfg.number_postorder()
    compute_idom(cfg)
    structure(cfg)

    # match_abnormal_sel() requires updated DFS numbers
    cfg.number_postorder()
    # We can't know which node to split before we start control flow processing,
    # but splitting node changes data flow, so need to recompute it
    if match_abnormal_sel(cfg):

        propagate(cfg)
        dce(cfg)

        cfg.number_postorder()
        compute_idom(cfg)
        structure(cfg)

    #
    # Post-processing
    #

    foreach_bblock_and_subblock(cfg, rewrite_stack_vars)
