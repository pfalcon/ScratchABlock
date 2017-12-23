from xform import *
from dataflow import *

import script_i_preserveds

def apply(cfg):
    script_i_preserveds.apply(cfg)
    collect_params(cfg)
    collect_call_live_out(cfg)
