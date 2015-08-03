#!/usr/bin/env python3
import sys
from parser import *
import dot
from xform import *
from decomp import *


p = Parser(sys.argv[1])
cfg = p.parse()
foreach_bblock(cfg, remove_trailing_jumps)

with open(sys.argv[1] + ".0.bb", "w") as f:
    dump_bblocks(cfg, f)
with open(sys.argv[1] + ".0.dot", "w") as f:
    dot.dot(cfg, f)

if hasattr(p, "script"):
    for xform in p.script:
        globals()[xform](cfg)

with open(sys.argv[1] + ".out.bb", "w") as f:
    dump_bblocks(cfg, f)
with open(sys.argv[1] + ".out.dot", "w") as f:
    dot.dot(cfg, f)
