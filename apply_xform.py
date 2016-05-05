#!/usr/bin/env python3
import sys
import argparse

from parser import *
import dot
from xform import *
from decomp import *
from asmprinter import dump_asm


argp = argparse.ArgumentParser(description="Parse and dump PseudoC program")
argp.add_argument("file", help="Input file in PseudoC format")
argp.add_argument("--format", default="bblocks", help="Output format (none, bblocks, asm)")
argp.add_argument("--debug", action="store_true", help="Produce debug files")
args = argp.parse_args()

p = Parser(args.file)
cfg = p.parse()
cfg.parser = p
foreach_bblock(cfg, remove_trailing_jumps)

if args.debug:
    with open(args.file + ".0.bb", "w") as f:
        dump_bblocks(cfg, f)
    with open(args.file + ".0.dot", "w") as f:
        dot.dot(cfg, f)

if hasattr(p, "script"):
    for (type, xform) in p.script:
        func = globals()[xform]
        if type == "xform:":
            func(cfg)
        elif type == "xform_bblock:":
            foreach_bblock(cfg, func)
        else:
            assert 0

if args.format == "bblocks":
    dump_bblocks(cfg)
elif args.format == "asm":
    dump_asm(cfg)

if args.debug:
    with open(args.file + ".out.bb", "w") as f:
        dump_bblocks(cfg, f)
    with open(args.file + ".out.dot", "w") as f:
        dot.dot(cfg, f)
