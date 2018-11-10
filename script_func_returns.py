from xform import *
from dataflow import *
import xform_inter

import script_preserveds

cg = None


def init():
    global cg
    cg = xform_inter.build_callgraph()


def apply(cfg):
    script_preserveds.apply(cfg)
    collect_call_live_out(cfg)

    xform_inter.calc_callsites_live_out(cg, cfg.props["name"])
    xform_inter.collect_returns()
