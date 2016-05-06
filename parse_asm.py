#!/usr/bin/env python3
import sys
import argparse
from parser import *
import core
import dot
from xform import foreach_inst
from asmprinter import AsmPrinter


argp = argparse.ArgumentParser(description="Parse and dump PseudoC program")
argp.add_argument("file", help="Input file in PseudoC format")
argp.add_argument("--repr", action="store_true", help="Dump __repr__ format of instructions")
argp.add_argument("--roundtrip", action="store_true", help="Dump PseudoC asm")
argp.add_argument("--addr-width", type=int, default=8, help="Width of address field (%(default)d)")
argp.add_argument("--inst-indent", type=int, default=4, help="Indent of instructions (%(default)d)")
args = argp.parse_args()

p = Parser(args.file)
cfg = p.parse()
cfg.parser = p

if args.roundtrip:
    p = AsmPrinter(cfg)
    p.addr_width = args.addr_width
    p.inst_indent = args.inst_indent
    p.print()
    sys.exit()

print("Labels:", p.labels)
if args.repr:
    core.SimpleExpr.simple_repr = False

print("Basic blocks:")
dump_bblocks(cfg, printer=repr if args.repr else str)

with open(sys.argv[1] + ".0.dot", "w") as f: dot.dot(cfg, f)
