# Minimal processing required to collect calls addresses (and
# indirect function references) for call graph generation.
from xform import *

def apply(cfg):
    # Various algos below don't work with no explicit entry in CFG
    cfg_single_entry(cfg)
    # Also don't work with >1 entries
    remove_unreachable_entries(cfg)
    # Also don't work unless there's a single exit
#    cfg_single_exit(cfg)

    analyze_reach_defs(cfg)
    const_propagation(cfg)
    #copy_propagation(cfg)
    #mem_propagation(cfg)
    #expr_propagation(cfg)

    collect_calls(cfg)
    collect_func_refs(cfg)
