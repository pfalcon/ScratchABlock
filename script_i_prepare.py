from xform import *
from dataflow import *

def apply(cfg):
    # Various algos below don't work with no explicit entry in CFG
    cfg_preheader(cfg)

    # Also don't work with >1 entries
#    remove_unreachable_entries(cfg)

    number_postorder(cfg)
    remove_unreachable_nodes(cfg)

    # Also don't work unless there's a single exit
    cfg_single_exit(cfg)

    foreach_bblock(cfg, sub_const_to_add)

    # This can be done once, no need to refine afterwards,
    # as we're interested in the "maybe" aspect which depends
    # only on the control flow of a particular function.
    analyze_reach_defs(cfg)
    collect_reach_exit_maybe(cfg)
