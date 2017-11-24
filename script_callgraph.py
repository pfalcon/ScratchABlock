# Minimal processing required to collect calls addresses for
# call graph generation.
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

    # Won't work here, because we might not have all funcs in funcdb,
    # need 2nd pass in script_callgraph_func_refs.py
    #collect_func_refs(cfg)
