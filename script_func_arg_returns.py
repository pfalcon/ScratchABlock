from xform import *
from dataflow import *

import script_preserveds

def init():
    clear_call_live_out()

def apply(cfg):
    script_preserveds.apply(cfg)
    collect_call_live_out(cfg)
    collect_returns()
    collect_args(cfg)
