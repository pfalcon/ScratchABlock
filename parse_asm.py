#!/usr/bin/env python3
import sys
from parser import *
import dot


p = Parser(sys.argv[1])
cfg = p.parse()
print("Labels:", p.labels)

print("Basic blocks:")
dump_bblocks(cfg)

with open(sys.argv[1] + ".0.dot", "w") as f: dot.dot(cfg, f)
