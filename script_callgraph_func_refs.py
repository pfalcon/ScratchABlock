# Part to of call graph generation - collect indirect function references.
# We can't do this in script_callgraph.py, because we need to have all
# functions in FUNCDB for that, and that script adds them sequentially,
# so we need second pass.
from xform import *

def apply(cfg):
    collect_func_refs(cfg)
