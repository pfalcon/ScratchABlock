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

    def _(res):
        return 1 if res else 0

    cnt = 1
    while cnt:
        cnt = 0
        cnt += _(match_if(cfg))
        # Opportunity for applying match_if_else_unjumped arises after
        # match_if pass, and we should match all such cases, or they
        # will be consumed by match_seq instead.
        cnt += apply_iterative(match_if_else_unjumped, (cfg,))
        cnt += _(match_ifelse(cfg))
        cnt += _(match_if_else_inv_ladder(cfg))
        cnt += _(match_if_else_ladder(cfg))
        cnt += _(match_while(cfg))
        cnt += _(match_dowhile(cfg))
        cnt += _(match_if_dowhile(cfg))
        cnt += _(match_seq(cfg))


# Apply arch-specific transformations
def arch_specific(cfg):
    # Remove Xtensa memw instructions. TODO: should instead be used to
    # recover volatile types.
    foreach_bblock(cfg, remove_sfunc, name="memw")


def apply(cfg):
    #
    # Data flow
    #

    # Various algos below don't work with no explicit entry in CFG
    cfg_preheader(cfg)
    # Various algos below require single-exit CFG
    cfg_single_exit(cfg)

    foreach_bblock(cfg, sub_const_to_add)
    # Initial pass on simplifying expressions
    foreach_inst(cfg, simplify_inst)

    analyze_live_vars(cfg)
    insert_initial_regs(cfg)

    propagate(cfg)

    # Estimate args only at the beginning of processing
    analyze_live_vars(cfg)
    estimate_params(cfg)

    dce(cfg)

    #
    # Control flow
    #

    remove_trailing_jumps(cfg)
    remove_jump_over_jump(cfg)

    arch_specific(cfg)

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
