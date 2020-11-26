#!/usr/bin/env python3
import sys
import argparse
import os.path
import glob

import yaml

import core
from parser import *
import dot
from dataflow import *
from xform import *
from xform_graph import *
from decomp import *
from asmprinter import AsmPrinter
import cprinter

# TODO: something above shadows "copy" otherwise
import copy


FUNC_DB = {}
FUNC_DB_ORG = {}


def parse_args():
    argp = argparse.ArgumentParser(description="Parse PseudoC program, apply transformations, and dump result in various formats")
    argp.add_argument("file", help="input file in PseudoC format, or directory of such files")
    argp.add_argument("-o", "--output", help="output file/dir (default stdout for single file, *.out for directory)")
    argp.add_argument("--script", help="apply script from file")
    argp.add_argument("--iter", action="store_true", help="apply transform iteratively until no changes to funcdb")
    argp.add_argument("--funcdb", help="function database file (default: funcdb.yaml in current/input dir)")
    argp.add_argument("--format", choices=["none", "bblocks", "asm", "c"], default="bblocks",
        help="output format (default: %(default)s)")
    argp.add_argument("--no-dead", action="store_true", help="don't output DCE-eliminated instructions")
    argp.add_argument("--no-graph-header", action="store_true", help="don't output graph properties")
    argp.add_argument("--repr", action="store_true", help="dump __repr__ format of instructions and other objects")
    argp.add_argument("--debug", action="store_true", help="produce debug files")
    args = argp.parse_args()

    if args.repr:
        core.SimpleExpr.simple_repr = False
    return args


def handle_file(args):
    try:
        handle_file_unprotected(args)
    except Exception as e:
        print("Error while processing file: " + args.file)
        raise e


def handle_file_unprotected(args):
    p = Parser(args.file)
    cfg = p.parse()
    cfg.parser = p

    # If we want to get asm back, i.e. stay close to the input, don't remove
    # trailing jumps. This will work OK for data flow algos, but will produce
    # broken or confusing output for control flow algos (for which asm output
    # shouldn't be used of course).
    # Update: it's unsafe to use this during dataflow analysis
    #if args.format != "asm":
    #    foreach_bblock(cfg, remove_trailing_jumps)

    if args.debug:
        with open(args.file + ".0.bb", "w") as f:
            dump_bblocks(cfg, f, no_graph_header=args.no_graph_header)
        with open(args.file + ".0.dot", "w") as f:
            dot.dot(cfg, f)

    if args.script:
        mod = __import__(args.script)
        mod.apply(cfg)
    elif hasattr(p, "script"):
        for op_type, op_name in p.script:
            if op_type == "xform:":
                func = globals()[op_name]
                func(cfg)
            elif op_type == "xform_bblock:":
                func = globals()[op_name]
                foreach_bblock(cfg, func)
            elif op_type == "xform_inst:":
                func = globals()[op_name]
                foreach_inst(cfg, func)
            elif op_type == "script:":
                mod = __import__(op_name)
                mod.apply(cfg)
            else:
                assert 0

    if args.debug:
        with open(args.file + ".out.bb", "w") as f:
            dump_bblocks(cfg, f, no_graph_header=args.no_graph_header)
        with open(args.file + ".out.dot", "w") as f:
            dot.dot(cfg, f)

    if args.output and args.format != "none":
        out = open(args.output, "w")
    else:
        out = sys.stdout

    if args.format == "bblocks":
        p = CFGPrinter(cfg, out)
        if args.no_graph_header:
            p.print_graph_header = lambda: None
        p.inst_printer = repr if args.repr else str
        p.no_dead = args.no_dead
        p.print()
    elif args.format == "asm":
        p = AsmPrinter(cfg, out)
        p.no_dead = args.no_dead
        p.print()
    elif args.format == "c":
        #foreach_bblock(cfg, remove_trailing_jumps)
        cfg.number_postorder()
        Inst.trail = ";"
        cprinter.no_dead = args.no_dead
        cprinter.dump_c(cfg, out)

    if out is not sys.stdout:
        out.close()

    update_funcdb(cfg)

    return cfg


def update_funcdb(cfg):
    "Aggregate data from each CFG processed into a function DB."
    if "addr" not in cfg.props:
        return
    func_props = FUNC_DB.setdefault(cfg.props["addr"], {})
    func_props["label"] = cfg.props["name"]

    for prop in ("estimated_args", "modifieds", "preserveds", "reach_exit"):
        if prop in cfg.props:
            func_props[prop] = cfg.props[prop]

    for prop in ("calls", "func_refs", "mmio_refs"):
        if prop in cfg.props:
            def ext_repr(x):
                if is_addr(x):
                    return x.addr
                if is_value(x):
                    return hex(x.val)
                if is_expr(x):
                    if x.op == "+" and len(x.args) == 2:
                        if is_value(x.args[1]):
                            x = EXPR("+", [x.args[1], x.args[0]])
                    return str(x)
                assert False, repr(x)
            func_props[prop] = sorted([ext_repr(x) for x in cfg.props[prop]])


REG_PROPS = [
    "callsites_live_out", "modifieds", "preserveds", "reach_exit", "args", "estimated_args",
    "returns",
]

def preprocess_funcdb(FUNC_DB):
    for addr, props in FUNC_DB.items():
        for prop in REG_PROPS:
            if prop in props:
                props[prop] = set(core.REG(x) for x in props[prop])


def postprocess_funcdb(FUNC_DB):
    for addr, props in FUNC_DB.items():
        for prop in REG_PROPS:
            if prop in props:
                props[prop] = sorted([x.name for x in props[prop]], key=core.natural_sort_key)


def one_iter(input, output):
    global FUNC_DB, FUNC_DB_ORG

    if os.path.exists(args.funcdb):
        with open(args.funcdb) as f:
            FUNC_DB = yaml.load(f)
            preprocess_funcdb(FUNC_DB)
            FUNC_DB_ORG = copy.deepcopy(FUNC_DB)
            import progdb
            progdb.set_funcdb(FUNC_DB)

    if os.path.isdir(input):
        if output and not os.path.isdir(output):
            os.makedirs(output)
        for full_name in glob.glob(input + "/*"):
            if full_name.endswith(".lst") and os.path.isfile(full_name):
                if args.debug:
                    print(full_name)
                args.file = full_name
                if output:
                    base_name = full_name.rsplit("/", 1)[-1]
                    args.output = output + "/" + base_name
                else:
                    args.output = full_name + ".out"
                handle_file(args)
    else:
        handle_file(args)


    changed = FUNC_DB != FUNC_DB_ORG
    if changed:
        postprocess_funcdb(FUNC_DB)
        if os.path.exists(args.funcdb):
            os.rename(args.funcdb, args.funcdb + ".bak")

        with open(args.funcdb, "w") as f:
            yaml.dump(FUNC_DB, f)

    return changed


if __name__ == "__main__":
    args = parse_args()

    if not args.funcdb:
        if os.path.isdir(args.file):
            # For an input as directory, use this *input* directory
            args.funcdb = args.file + "/funcdb.yaml"
        else:
            # For a single file, use *current* directory
            args.funcdb = "funcdb.yaml"

    input = args.file
    output = args.output

    while True:
        changed = one_iter(input, output)
        if not changed or not args.iter:
            break
        if args.debug:
            print("Another iteration")
