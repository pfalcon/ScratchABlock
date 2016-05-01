#!/usr/bin/env python3
import sys
import argparse
from parser import *
import core
import dot


argp = argparse.ArgumentParser(description="Parse and dump PseudoC program")
argp.add_argument("file", help="Input file in PseudoC format")
argp.add_argument("--repr", action="store_true", help="Dump __repr__ format of instructions")
args = argp.parse_args()

p = Parser(args.file)
cfg = p.parse()
print("Labels:", p.labels)

if args.repr:
    core.SimpleExpr.simple_repr = False

print("Basic blocks:")
dump_bblocks(cfg, printer=repr if args.repr else str)

with open(sys.argv[1] + ".0.dot", "w") as f: dot.dot(cfg, f)
