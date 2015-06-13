from graph import Graph
from core import *


class Seq(BBlock):
    def __init__(self, b1, b2):
        self.addr = b1.addr
        self.items = [b1, b2]

    def __repr__(self):
        return "%s(%r, %r)" % (self.__class__.__name__, self.items[0], self.items[1])

    def dump(self, stream, indent=0):
        for b in self.items:
            b.dump(stream, indent)


def match_seq(cfg):
    for v, _ in cfg.iter_nodes():
        if cfg.degree_out(v) == 1:
            succ = cfg.succ(v)[0]
            if cfg.degree_in(succ) == 1:
                print("seq:", v, succ)
                newb = Seq(cfg.node(v), cfg.node(succ))
                cfg.add_node(v, newb)
                cfg.move_succ(succ, v)
                cfg.remove_node(succ)
                return True
