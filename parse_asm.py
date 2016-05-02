#!/usr/bin/env python3
import sys
import argparse
from parser import *
import core
import dot
from xform import foreach_inst


argp = argparse.ArgumentParser(description="Parse and dump PseudoC program")
argp.add_argument("file", help="Input file in PseudoC format")
argp.add_argument("--repr", action="store_true", help="Dump __repr__ format of instructions")
argp.add_argument("--roundtrip", action="store_true", help="Dump PseudoC asm")
args = argp.parse_args()

p = Parser(args.file)
cfg = p.parse()
cfg.parser = p

class RoundtripPrinter(CFGPrinter):

    def __init__(self, cfg):
        super().__init__(cfg)
        self.inst_printer = self.print_with_addr
        self.referenced_labels = set()
        self.get_jump_labels()

    def get_jump_labels(self):
        def collect_labels(inst):
            addr = inst.jump_addr()
            if addr is not None:
                self.referenced_labels.add(addr)
        foreach_inst(self.cfg, collect_labels)

    @staticmethod
    def print_with_addr(inst):
        return "%-12s " % inst.addr + str(inst)

    def resolve_label(self, addr):
        return self.cfg.parser.label_from_addr(addr)

    def print_label(self):
        # If there was symbolic label originally, print it
        # otherwise, skip it if it's not referenced by insts
        # (like bblock start labels).
        label = self.cfg.parser.label_from_addr(self.addr)
        if label == self.addr:
            if self.addr not in self.referenced_labels:
                return
        print("%-8s %s:" % (self.addr, label), file=self.stream)

    def print_header(self):
        pass
    def print_separator(self):
        pass
    def print_trailer(self):
        pass

    def print(self):
        core.ADDR.resolver = self.resolve_label
        super().print()


if args.roundtrip:
    p = RoundtripPrinter(cfg)
    p.print()
    sys.exit()

print("Labels:", p.labels)
if args.repr:
    core.SimpleExpr.simple_repr = False

print("Basic blocks:")
dump_bblocks(cfg, printer=repr if args.repr else str)

with open(sys.argv[1] + ".0.dot", "w") as f: dot.dot(cfg, f)
