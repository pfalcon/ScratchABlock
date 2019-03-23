#!/usr/bin/env python3
#
# This script requires a callgraph, which should be constructed
# e.g. with make_callgraph.sh.
#
import sys
import os
import glob
import collections
import copy

import core
from parser import Parser
from core import CFGPrinter, is_addr
import xform_inter
import progdb
import arch
import dot
from cfgutils import save_cfg
import utils

from utils import maybesorted


core.Inst.annotate_calls = True


def save_cfg_layer(cfg_layer, suffix):
    for name, cfg in cfg_layer.items():
        save_cfg(cfg, suffix)


progdb.load_funcdb(sys.argv[1] + "/funcdb.yaml")
# Load binary data
import bindata
bindata.init(sys.argv[1])
# Load symtab
if os.path.exists(sys.argv[1] + "/symtab.txt"):
    progdb.load_symtab(sys.argv[1] + "/symtab.txt")

callgraph = xform_inter.build_callgraph()

with open("cg-current.dot", "w") as out:
    dot.dot(callgraph, out, is_cfg=False)

#for func in callgraph.iter_rev_postorder():
#    print(func, callgraph[func])

CFG_MAP = collections.defaultdict(dict)

import script_i_prepare

for full_name in glob.glob(sys.argv[1] + "/*.lst"):
    p = Parser(full_name)
    cfg = p.parse()
    cfg.parser = p
    #print("Loading:", cfg.props["name"])
    CFG_MAP["org"][cfg.props["name"]] = cfg

    cfg2 = cfg.copy()
    script_i_prepare.apply(cfg2)
    CFG_MAP["pre"][cfg2.props["name"]] = cfg2

    save_cfg(cfg2, ".pre")


#print(CFG_MAP)

#save_cfg_layer(CFG_MAP["pre"], ".1")

subiter_cnt = 0
update_cnt = 0

def process_one(cg, func, xform_pass):
    global subiter_cnt, update_cnt
    upward_queue = [func]
    downward_queue = []
    cnt = 0

    cur_queue = upward_queue
    while upward_queue or downward_queue:
        subiter_cnt += 1
        cnt += 1
        if not cur_queue:
            if cur_queue is upward_queue:
                cur_queue = downward_queue
            else:
                cur_queue = upward_queue
        func = cur_queue.pop(0)

        print("--- Next to process: %s ---" % func)
        progdb.clear_updated()

        cfg = CFG_MAP["pre"][func].copy()

        call_lo_union = xform_inter.calc_callsites_live_out(cg, func)
        progdb.update_cfg_prop(cfg, "callsites_live_out", call_lo_union)
        print("%s: callsites_live_out set to %s" % (func, utils.repr_stable(call_lo_union)))
        if "modifieds" in progdb.FUNC_DB[func]:
            progdb.FUNC_DB[func]["returns"] = arch.ret_filter(progdb.FUNC_DB[func]["modifieds"] & call_lo_union)
        else:
            print("%s: doesn't yet have modifieds!" % func)

        xform_pass.apply(cfg)

        if progdb.UPDATED_FUNCS:
            assert len(progdb.UPDATED_FUNCS) == 1, repr(progdb.UPDATED_FUNCS)
            func2 = progdb.UPDATED_FUNCS.pop()
            assert func2 == func
            update_cnt += 1

            progdb.update_funcdb(cfg)
            save_cfg(cfg, ".1")
            dot.save_dot(cfg, ".1")
            CFG_MAP["pre"][func].props = cfg.props

            upward_queue.extend(maybesorted(cg.pred(func)))

            for callee in maybesorted(cg.succ(func)):
                print("! updating callee", callee)
                if callee not in downward_queue:
                    downward_queue.insert(0, callee)

            print("--- Finished processing: %s ---" % func)
            print("# New up (caller) queue:", upward_queue)
            print("# New down (callee) queue:", downward_queue)
        else:
            print("%s not updated" % func)
            # Maybe funcdb properties not updated, but bblocks props can very well be
            save_cfg(cfg, ".1")
            dot.save_dot(cfg, ".1")

    print("Subiters:", cnt)


import script_i_func_params_returns

iter_cnt = 1

while True:
    print("=== Iteration %d ===" % iter_cnt)
    old_funcdb = copy.deepcopy(progdb.FUNC_DB)
    progdb.clear_updated()

    # We start with some leaf node (then eventually with all the rest of
    # leafs). With leaf (call-less) function, we can know everything about
    # its parameters. So, we learn that, and then propagate this information
    # to all its callers, then to callers of its callers. We go in this
    # upward fashion (propagating parameter information) until we can, and
    # then we start downward motion, hoping to collect as much information
    # as possible about function live-outs, i.e. returns. We go in this
    # zig-zag fashion, until there's something to update.
    for e in maybesorted(callgraph.exits()):
        print("Processing leaf", e)
        process_one(callgraph, e, script_i_func_params_returns)

    progdb.save_funcdb(sys.argv[1] + "/funcdb.yaml.out%d" % iter_cnt)

    if progdb.FUNC_DB == old_funcdb:
        break

    iter_cnt += 1
#    if iter_cnt > 3:
#        break


print("Done in %d iterations, %d sub-iterations, %d updates" % (iter_cnt, subiter_cnt, update_cnt))
