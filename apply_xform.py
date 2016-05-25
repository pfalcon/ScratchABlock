#!/usr/bin/env python3
import sys
import argparse

import core
from parser import *
import dot
from xform import *
from decomp import *
from asmprinter import AsmPrinter
import cprinter


argp = argparse.ArgumentParser(description="Parse and dump PseudoC program")
argp.add_argument("file", help="Input file in PseudoC format")
argp.add_argument("--script", help="Apply script from file")
argp.add_argument("--format", default="bblocks", help="Output format (none, bblocks, asm)")
argp.add_argument("--no-dead", action="store_true", help="Don't output DCE-eliminated instructions")
argp.add_argument("--repr", action="store_true", help="Dump __repr__ format of instructions")
argp.add_argument("--debug", action="store_true", help="Produce debug files")
args = argp.parse_args()

if args.repr:
    core.SimpleExpr.simple_repr = False

p = Parser(args.file)
cfg = p.parse()
cfg.parser = p

# If we want to get asm back, i.e. stay close to the input, don't remove
# trailing jumps. This will work OK for data flow algos, but will produce
# broken or confusing output for control flow algos (for which asm output
# shouldn't be used of course).
if args.format != "asm":
    foreach_bblock(cfg, remove_trailing_jumps)

if args.debug:
    with open(args.file + ".0.bb", "w") as f:
        dump_bblocks(cfg, f)
    with open(args.file + ".0.dot", "w") as f:
        dot.dot(cfg, f)

if args.script:
    mod = __import__(args.script)
    mod.apply(cfg)
elif hasattr(p, "script"):
    for (type, xform) in p.script:
        func = globals()[xform]
        if type == "xform:":
            func(cfg)
        elif type == "xform_bblock:":
            foreach_bblock(cfg, func)
        else:
            assert 0

if args.format == "bblocks":
    dump_bblocks(cfg, printer=repr if args.repr else str)
elif args.format == "asm":
    p = AsmPrinter(cfg)
    p.no_dead = args.no_dead
    p.print()
elif args.format == "c":
    #foreach_bblock(cfg, remove_trailing_jumps)
    Inst.trail = ";"
    cprinter.no_dead = args.no_dead
    cprinter.dump_c(cfg)


if args.debug:
    with open(args.file + ".out.bb", "w") as f:
        dump_bblocks(cfg, f)
    with open(args.file + ".out.dot", "w") as f:
        dot.dot(cfg, f)
