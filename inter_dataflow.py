#!/usr/bin/env python3
import sys
import glob
import collections
import copy

import core
from graph import Graph
from parser import Parser
from core import CFGPrinter
import progdb
import dot

core.Inst.annotate_calls = True

progdb.load_funcdb(sys.argv[1] + "/funcdb.yaml")

callgraph = Graph()

for addr, props in progdb.FUNC_DB_BY_ADDR.items():
    callgraph.add_node(props["label"])

for addr, props in progdb.FUNC_DB_BY_ADDR.items():
    for callee in props.get("calls", []):
        if callee in callgraph:
            callgraph.add_edge(props["label"], callee)

callgraph.number_postorder()
with open("cg-current.dot", "w") as out:
    dot.dot(callgraph, out, is_cfg=False)

#for func, props in callgraph.iter_rev_postorder():
#    print(func, props)

CFG_MAP = collections.defaultdict(dict)

import script_prepare

for full_name in glob.glob(sys.argv[1] + "/*.lst"):
    p = Parser(full_name)
    cfg = p.parse()
    cfg.parser = p
    CFG_MAP["org"][cfg.props["name"]] = cfg

    cfg2 = cfg.copy()
    script_prepare.apply(cfg2)
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


def process_postorder(cg, func, xform_pass):
    for callee in cg.succ(func):
        process_postorder(cg, callee, xform_pass)

    print("  post:", func)
    cfg = CFG_MAP["pre"][func].copy()
    xform_pass.apply(cfg)
    progdb.update_funcdb(cfg)
    save_cfg(cfg, ".1")


def process_preorder(cg, func, xform_pass):
    print("  pre:", func)
    cfg = CFG_MAP["pre"][func].copy()
    xform_pass.apply(cfg)
    progdb.update_funcdb(cfg)
    save_cfg(cfg, ".2")

    for callee in cg.succ(func):
        process_preorder(cg, callee, xform_pass)


import script_func_args
import script_func_returns

cnt = 1

while True:
    print("=== Iteration %d ===" % cnt)
    old_funcdb = copy.deepcopy(progdb.FUNC_DB)
    script_func_returns.init()

    for e in callgraph.entries():
        print("Processing root", e)
        process_postorder(callgraph, e, script_func_args)

    progdb.save_funcdb(sys.argv[1] + "/funcdb.yaml.out%d" % cnt)

    for e in callgraph.entries():
        print("Processing root", e)
        process_preorder(callgraph, e, script_func_returns)

    progdb.save_funcdb(sys.argv[1] + "/funcdb.yaml.out%d_" % cnt)

    if progdb.FUNC_DB == old_funcdb:
        break

    cnt += 1
#    break

print("Done in %d iterations" % cnt)
