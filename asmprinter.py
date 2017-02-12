import sys
import argparse
from parser import *
import core
import dot
from xform import foreach_inst


class AsmPrinter(CFGPrinter):

    def __init__(self, cfg):
        super().__init__(cfg)
        self.addr_width = 8
        self.inst_indent = 4
        self.no_dead = False

        self.inst_printer = self.print_with_addr
        self.referenced_labels = set()
        self.get_jump_labels()

    def format_addr(self, addr, extra=0):
        return addr.ljust(self.addr_width + extra)

    def get_jump_labels(self):
        def collect_labels(inst):
            addr = inst.jump_addr()
            if addr is not None:
                self.referenced_labels.add(addr)
        foreach_inst(self.cfg, collect_labels)

    def print_with_addr(self, inst):
        if inst.op == "DEAD" and self.no_dead:
            return
        addr = inst.addr
        if addr is None:
            addr = "?"
        return self.format_addr(addr, self.inst_indent) + " " + str(inst)

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
        print("%s %s:" % (self.format_addr(self.addr), label), file=self.stream)

    def print_header(self):
        pass
    def print_separator(self):
        pass
    def print_trailer(self):
        pass

    def print(self):
        core.ADDR.resolver = self.resolve_label
        super().print()


def dump_asm(cfg):
    p = AsmPrinter(cfg)
    p.print()
