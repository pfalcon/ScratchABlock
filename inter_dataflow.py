#!/usr/bin/env python3
import sys
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
import utils

from utils import maybesorted


core.Inst.annotate_calls = True

progdb.load_funcdb(sys.argv[1] + "/funcdb.yaml")

callgraph = xform_inter.build_callgraph()

with open("cg-current.dot", "w") as out:
    dot.dot(callgraph, out, is_cfg=False)

#for func, props in callgraph.iter_rev_postorder():
#    print(func, props)

CFG_MAP = collections.defaultdict(dict)

import script_i_prepare

for full_name in glob.glob(sys.argv[1] + "/*.lst"):
    p = Parser(full_name)
    cfg = p.parse()
    cfg.parser = p
    CFG_MAP["org"][cfg.props["name"]] = cfg

    cfg2 = cfg.copy()
    script_i_prepare.apply(cfg2)
    CFG_MAP["pre"][cfg2.props["name"]] = cfg2

#print(CFG_MAP)

def save_cfg(cfg, suffix):
    with open(cfg.filename + suffix, "w") as out:
        p = CFGPrinter(cfg, out)
        p.print()

def save_cfg_layer(cfg_layer, suffix):
    for name, cfg in cfg_layer.items():
        save_cfg(cfg, suffix)

#save_cfg_layer(CFG_MAP["pre"], ".1")


def calc_callsites_live_out(cg, callee):
    callers = maybesorted(cg.pred(callee))
    # If there're no callers, will return empty set, which
    # is formally correct - if there're no callers, the
    # function is dead. However, realistically that means
    # that callers aren't known, and we should treat that
    # specially.
    call_lo_union = set()
    for c in callers:
        clo = progdb.FUNC_DB[c].get("calls_live_out", [])
        print("%s: calls_live_out: %s" % (c, utils.repr_stable(clo)))
        for bbaddr, callee_expr, live_out in clo:
            if is_addr(callee_expr) and callee_expr.addr == callee:
                call_lo_union.update(live_out)
    return call_lo_union


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

        print("Next to process:", func)
        progdb.clear_updated()

        cfg = CFG_MAP["pre"][func].copy()

        xform_pass.apply(cfg)

        if progdb.UPDATED_FUNCS:
            assert len(progdb.UPDATED_FUNCS) == 1, repr(progdb.UPDATED_FUNCS)
            func2 = progdb.UPDATED_FUNCS.pop()
            assert func2 == func
            update_cnt += 1

            progdb.update_funcdb(cfg)
            save_cfg(cfg, ".1")
            CFG_MAP["pre"][func].props = cfg.props

            upward_queue.extend(maybesorted(cg.pred(func)))

            for callee in maybesorted(cg.succ(func)):
                print("! updating callee", callee)
                if callee not in downward_queue:
                    downward_queue.insert(0, callee)

                call_lo_union = calc_callsites_live_out(cg, callee)
                progdb.FUNC_DB[callee]["callsites_live_out"] = call_lo_union
                print("callsites_live_out for %s set to %s" % (callee, call_lo_union))
                if "modifieds" in progdb.FUNC_DB[callee]:
                    progdb.FUNC_DB[callee]["returns"] = arch.ret_filter(progdb.FUNC_DB[callee]["modifieds"] & call_lo_union)

            print("New up queue:", upward_queue)
            print("New down queue:", downward_queue)
        else:
            print("%s not updated" % func)

    print("Subiters:", cnt)


import script_i_func_args_returns

iter_cnt = 1

while True:
    print("=== Iteration %d ===" % iter_cnt)
    old_funcdb = copy.deepcopy(progdb.FUNC_DB)
    progdb.clear_updated()

    for e in maybesorted(callgraph.exits()):
        print("Processing leaf", e)
        process_one(callgraph, e, script_i_func_args_returns)

    progdb.save_funcdb(sys.argv[1] + "/funcdb.yaml.out%d" % iter_cnt)

    if progdb.FUNC_DB == old_funcdb:
        break

    iter_cnt += 1
#    if iter_cnt > 3:
#        break


print("Done in %d iterations, %d sub-iterations, %d updates" % (iter_cnt, subiter_cnt, update_cnt))
