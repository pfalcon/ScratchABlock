#!/usr/bin/env python3
import sys
import argparse

import yaml

from utils import maybesorted


argp = argparse.ArgumentParser(description="Render function database as various graphs")
argp.add_argument("file", help="Input file (YAML)")
argp.add_argument("-o", "--output", help="Output file (default stdout)")
argp.add_argument("--func", help="Start from this function")
argp.add_argument("--no-runtime", action="store_true", help="Don't show calls to 'runtime' functions")
argp.add_argument("--no-refs", action="store_true", help="Show only direct calls, not refs to other functions "
    "(otherwise shown as dashed lines)")
argp.add_argument("--each-call", action="store_true", help="Show multiple edges for each call site")
args = argp.parse_args()

FUNC_DB = yaml.load(open(args.file))

if args.output:
    out = open(args.output, "w")
else:
    out = sys.stdout


RUNTIME = {
    "ets_delay_us",
    "ets_memcpy",
    "ets_memset",
    "ets_bzero",
    "bzero",
    "memcpy__1",

    "ets_printf",
    "ets_vprintf",
    "eprintf",

    "ets_intr_lock",
    "ets_intr_unlock",
    "ets_isr_mask",
    "ets_isr_unmask",
}

dup_set = set()


def index_by_name(db):
    for addr, props in list(db.items()):
        db[props["label"]] = props


def is_runtime(funcname):
    if funcname in RUNTIME:
        return True
    if funcname.startswith("__"):
        return True


def dump_level(func, props):
    if props["label"] in RUNTIME:
        return
    for propname in ("calls", "func_refs"):
        if propname == "func_refs" and args.no_refs:
            continue
        for callee in maybesorted(props.get(propname, [])):
            if is_runtime(callee):
                if args.no_runtime:
                    continue
                callee = "RUNTIME"

            if not args.each_call:
                if (props["label"], callee) in dup_set:
                    continue
                dup_set.add((props["label"], callee))
            attrs = {"func_refs": " [style=dashed]"}.get(propname, "")
            out.write("%s -> %s%s\n" % (props["label"], callee, attrs))


out.write("digraph G {\n")

if args.func:
    index_by_name(FUNC_DB)
    todo = [args.func]
    done = set()
    while todo:
        f = todo.pop()
        props = FUNC_DB.get(f)
        if not props:
            continue
        dump_level(f, props)
        done.add(f)
        for callee in props["calls"]:
            if callee not in done:
                todo.append(callee)
else:
    for func, props in maybesorted(FUNC_DB.items()):
        dump_level(func, props)

out.write("}\n")
