from xform import *
from dataflow import *

import script_i_preserveds

def init():
    clear_call_live_out()

def apply(cfg):
    script_i_preserveds.apply(cfg)
    collect_args(cfg)
    collect_call_live_out(cfg)
    collect_returns()
