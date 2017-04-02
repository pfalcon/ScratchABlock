#!/usr/bin/env python3
import sys
import argparse

import yaml

from utils import maybesorted


argp = argparse.ArgumentParser(description="Render function database as various graphs")
argp.add_argument("file", help="Input file (YAML)")
argp.add_argument("-o", "--output", help="Output file (default stdout)")
argp.add_argument("--func", help="Start from this function")
argp.add_argument("--no-refs", action="store_true", help="Show only direct calls, not refs to other functions "
    "(otherwise shown as dashed lines)")
argp.add_argument("--group", action="append", default=[], help="Group some functions together, GROUP is name=file.txt, "
    "if name is '_ignore_', don't graph these functions")
argp.add_argument("--each-call", action="store_true", help="Show multiple edges for each call site")
args = argp.parse_args()

IGNORE = set()
GROUPS = {}


def read_func_list(fname):
    res = []
    with open(fname) as f:
        for l in f:
            l = l.strip()
            if not l or l[0] == "#":
                continue
            res.append(l)
    return res


for g in args.group:
    name, fname = g.split("=", 1)
    funcs = read_func_list(fname)
    if name == "_ignore_":
        IGNORE.update(funcs)
    else:
        GROUPS[name] = set(funcs)


FUNC_DB = yaml.load(open(args.file))

if args.output:
    out = open(args.output, "w")
else:
    out = sys.stdout


dup_set = set()


def index_by_name(db):
    for addr, props in list(db.items()):
        db[props["label"]] = props


def get_group(funcname):
    if funcname in IGNORE:
        return "_ignore_"
    for name, funcs in GROUPS.items():
        if funcname in funcs:
            return name


def map_group(funcname):
    return get_group(funcname) or funcname


def dump_level(func, props):
    if get_group(props["label"]):
        return
    for propname in ("calls", "func_refs"):
        if propname == "func_refs" and args.no_refs:
            continue
        for callee in maybesorted(props.get(propname, [])):
            if callee in IGNORE:
                continue
            callee = map_group(callee)

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
