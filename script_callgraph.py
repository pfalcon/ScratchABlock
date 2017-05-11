# Minimal processing required to collect calls addresses (and
# indirect function references) for call graph generation.
from xform import *

def apply(cfg):
    # Various algos below require single-exit CFG
#    cfg_single_exit(cfg)
    # And single entry
    remove_unreachable_entries(cfg)

    analyze_reach_defs(cfg)
    const_propagation(cfg)
    #copy_propagation(cfg)
    #mem_propagation(cfg)
    #expr_propagation(cfg)

    collect_calls(cfg)
    collect_func_refs(cfg)
