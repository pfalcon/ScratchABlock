from xform import *
from dataflow import *

import script_i_preserveds

def apply(cfg):
    script_i_preserveds.apply(cfg)

    # Find out underestimated, but true params of function.
    # The problem is that correct analysis overestimates liveness,
    # We get a bunch of registers, and we don't even understand
    # how we ended up with such a bunch. Underestimate pass will
    # allow us to classify full param set into true-params and
    # maybe-params.
    analyze_live_vars(cfg, underestimate=True)
    estimate_params(cfg)

    analyze_live_vars(cfg)
    collect_params(cfg)
    collect_call_live_out(cfg)

    annotate_params(cfg)
