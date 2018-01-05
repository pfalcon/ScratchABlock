#!/usr/bin/env python3
import sys
import re


start_addr = None
out_f = None


with open(sys.argv[1]) as f:
    for l in f:
        addr = int(l[:8], 16)
        l = l[8:]

        if start_addr is None:
            start_addr = addr
            out_f = open("fun_%08x.lst" % (~start_addr & 0xffffffff), "w")

        def repl(m):
            return m.group(1) + "%08x" % (int(m.group(2), 16) - start_addr)

        l = re.sub(r"(loc_)([0-9A-Fa-f]{8})", repl, l)

        addr -= start_addr
        out_f.write("%08x%s" % (addr, l))
