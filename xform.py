from graph import Graph
from core import *
from cfgutils import *
from dce import *
import arch


# Apply tranformation while it's possible
def apply_iterative(func, args):
    cnt = 0
    while func(*args):
        cnt += 1
    print("Ran %s %d times" % (func, cnt))


def remove_trailing_jumps(bblock):
    """Trailing jumps are encoded as out edges of basic block, and
    superfluous for most deeper transformations (but useful for
    surface transformations which should maintain instruction
    correspondence to the original input). This pass removes them.
    """
    last_jump = None
    for i in range(len(bblock.items) -1, -1, -1):
        if bblock.items[i].op in ("goto", "if"):
            last_jump = i
        else:
            break
    if last_jump is not None:
        #print("Removing: ", bblock.items[last_jump:])
        del bblock.items[last_jump:]


# Remove any jumps to jumps, replacing destination of first jump
# to be destination of 2nd.
# This "simplifies" graph, but makes it irregular. This is useful
# transformation for generating machine code, but for decompilation,
# it actually makes sense to add extra jump landing sites to make
# loops irregular.
#
# http://en.wikipedia.org/wiki/Jump_threading
#
def remove_jump_over_jump(cfg):
    for v, _ in cfg.iter_nodes():
        # If node is not entry, has a single exit and empty
        if cfg.degree_in(v) > 0 and cfg.degree_out(v) == 1 and not cfg.node(v)["val"].items:
            cfg.move_pred(v, cfg.succ(v)[0])
            cfg.remove_node(v)
            print("jump_over_jump: removed node:", v)
            return True

# If possible, make a single back-edge to a loop header, by introducing
# intermediate jump landing nodes.
def loop_single_entry(cfg):
    for v, _ in cfg.iter_nodes():
        if cfg.degree_in(v) >= 2:
            preds = cfg.pred(v)
            back_preds = list(filter(lambda x: v <= x, preds))
            if len(back_preds) < 2:
                continue
            print("loop_single_entry: node:", v)
            print("back_preds:", back_preds)
            back_jumps = list(filter(lambda x: cfg.degree_out(x) == 1, back_preds))
            print("back_jumps:", back_jumps)
            # find existing landing site
            landing_site = None
            for p in back_jumps:
                b = cfg.node(p)["val"]
                if not b.items:
                    landing_site = p
            if not landing_site:
                farthest = max(back_preds)
                print("farthest", farthest)
                newb = BBlock(farthest + "_1")
                cfg.add_node(newb.addr, val=newb)
                cfg.add_edge(newb.addr, v)
                landing_site = newb.addr
            print("landing_site:", landing_site)
            for p in back_preds:
                if p != landing_site:
                    e = cfg.edge(p, v).get("cond")
                    cfg.remove_edge(p, v)
                    cfg.add_edge(p, landing_site, cond=e)
            return True


def expr_subst(expr, subst_dict):

    if isinstance(expr, REG):
        new = subst_dict.get(expr, expr)
        return new

    if isinstance(expr, MEM):
        if expr.base not in subst_dict:
            return
        new = subst_dict[expr.base]
        if isinstance(new, VALUE):
            return MEM(expr.type, VALUE(new.val + expr.offset))
        else:
            return MEM(expr.type, new, expr.offset)


def const_expr_simplify(expr):
    """Calculate numeric value of expression, if it's constant expression.
    expr can be an instruction too.
    """
    res = None
    base = 10
    if expr.op == "+":
        res = (expr.args[0].val + expr.args[1].val) % 2**arch.BITNESS
        base = max([a.base for a in expr.args])

    if res is not None:
        return VALUE(res, base)
    else:
        return None


def kill_subst_uses(subst, kill_var):
    "Remove from subst dict any expressions involving kill_var"
    def not_used(var, expr):
        # Here we assume that expression can be at most reference to a var,
        # which is true for at most copy propagation, but to handle expr
        # propagation, need to do better
        return var != expr
    subst = dict((k, v) for k, v in subst.items() if not_used(kill_var, v))
    return subst


def bblock_propagation(bblock, propagated_types):
    state = {}
    for i, inst in enumerate(bblock.items):

        all_args_const = True
        for arg_no, arg in enumerate(inst.args):
            repl = expr_subst(arg, state)
            if repl:
                inst.args[arg_no] = repl
            if not isinstance(inst.args[arg_no], VALUE):
                all_args_const = False

        if all_args_const:
            val = const_expr_simplify(inst)
            if val is not None:
                inst.op = "="
                inst.args = [val]

        if inst.op == "=" and isinstance(inst.args[0], propagated_types):
            # Calling kill_subst_uses isn't really needed for const propagation
            # (as variables aren't propagated), but needed for copy propagation
            # and higher.
            state = kill_subst_uses(state, inst.dest)
            state[inst.dest] = inst.args[0]


def bblock_const_propagation(bblock):
    "Propagate only constant values"
    bblock_propagation(bblock, (VALUE, ADDR))

def bblock_copy_propagation(bblock):
    "Propagate constants and register copies"
    bblock_propagation(bblock, (VALUE, ADDR, REG))


import dataflow
def analyze_live_vars(cfg):
    ana = dataflow.LiveVarAnalysis(cfg)
    ana.solve()
