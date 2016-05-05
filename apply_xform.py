#!/usr/bin/env python3
import sys
import argparse

from parser import *
import dot
from xform import *
from decomp import *


argp = argparse.ArgumentParser(description="Parse and dump PseudoC program")
argp.add_argument("file", help="Input file in PseudoC format")
argp.add_argument("--debug", action="store_true", help="Produce debug files")
args = argp.parse_args()

p = Parser(args.file)
cfg = p.parse()
foreach_bblock(cfg, remove_trailing_jumps)

if args.debug:
    with open(args.file + ".0.bb", "w") as f:
        dump_bblocks(cfg, f)
    with open(args.file + ".0.dot", "w") as f:
        dot.dot(cfg, f)

if hasattr(p, "script"):
    for xform in p.script:
        globals()[xform](cfg)

dump_bblocks(cfg)

if args.debug:
    with open(args.file + ".out.bb", "w") as f:
        dump_bblocks(cfg, f)
    with open(args.file + ".out.dot", "w") as f:
        dot.dot(cfg, f)
