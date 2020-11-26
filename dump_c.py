#!/usr/bin/env python3
import sys
from parser import *
import dot
from core import *
from xform import *
import cprinter


def __main__():
    p = Parser(sys.argv[1])
    cfg = p.parse()
    #print("Labels:", p.labels)

    cfg.parser = p
    remove_trailing_jumps(cfg)
    cfg.number_postorder()
    Inst.trail = ";"

    #print("Basic blocks:")
    #dump_bblocks(cfg)

    #with open(sys.argv[1] + ".0.dot", "w") as f: dot.dot(cfg, f)

    cprinter.dump_c(cfg)


if __name__ == "__main__":
    __main__()
