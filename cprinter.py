import sys


def pairwise(iterable):
    prev = Ellipsis
    for it in iterable:
        if prev is not Ellipsis:
            yield (prev, it)
        prev = it
    yield (it, None)


def find_used_labels(cfg):
    labels = set()
    for (addr, info), nxt in pairwise(cfg.iter_rev_postorder()):
        bblock = info["val"]
        for succ in cfg.succ(addr):
            cond = cfg.edge(addr, succ).get("cond")
            if not cond and nxt and succ == nxt[0]:
                continue
            labels.add(succ)
    return labels


def dump_c(cfg):
    labels = find_used_labels(cfg)
    func_start = True
    for (addr, info), nxt in pairwise(cfg.iter_rev_postorder()):
        bblock = info["val"]
        if func_start:
            print("void %s()\n{" % cfg.parser.label_from_addr(bblock.addr))
            func_start = False
        if addr in labels:
            print("\nl%s:" % addr)
        bblock.dump(sys.stdout, indent=1)
        for succ in cfg.succ(addr):
            cond = cfg.edge(addr, succ).get("cond")
            if not cond and nxt and succ == nxt[0]:
                continue
            sys.stdout.write("  ")
            if cond:
                sys.stdout.write("if %s " % cond)
            print("goto l%s;" % succ)

    print("}")
