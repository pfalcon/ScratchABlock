#!/usr/bin/env python3
import sys
from parser import *
import dot
from core import *
from xform import *
import cprinter


p = Parser(sys.argv[1])
cfg = p.parse()
print("Labels:", p.labels)

cfg.parser = p
foreach_bblock(cfg, remove_trailing_jumps)
cfg.number_postorder()
Inst.trail = ";"

print("Basic blocks:")
dump_bblocks(cfg)

with open(sys.argv[1] + ".0.dot", "w") as f: dot.dot(cfg, f)

cprinter.dump_c(cfg)
