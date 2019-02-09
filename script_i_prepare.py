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
    number_postorder_from_exit(cfg)
    number_postorder(cfg)
    cfg_infloops_exit(cfg)

    foreach_inst(cfg, sub_const_to_add)
