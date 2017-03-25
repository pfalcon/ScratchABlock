from collections import defaultdict

from graph import Graph
from core import *
from cfgutils import *
from dce import *
from xform_expr import *
import arch


# Apply tranformation while it's possible
def apply_iterative(func, args):
    cnt = 0
    while func(*args):
        cnt += 1
    print("Ran %s %d times" % (func, cnt))


def remove_trailing_jumps(cfg):
    remove_returns = False
    exits = cfg.exits()
    if len(exits) == 1:
        remove_returns = True

    foreach_bblock(cfg, remove_trailing_jumps_bblock, remove_returns=remove_returns)
    cfg.trailing_jumps = False


def remove_trailing_jumps_bblock(bblock, remove_returns=False):
    """Trailing jumps are encoded as out edges of basic block, and
    superfluous for most deeper transformations (but useful for
    surface transformations which should maintain instruction
    correspondence to the original input). This pass removes them.
    """
    to_remove = ["goto", "if"]
    if remove_returns:
        to_remove.append("return")

    last_jump = None
    for i in range(len(bblock.items) -1, -1, -1):
        if bblock.items[i].op in to_remove:
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


# Make sure that CFG has a single exit, as required for some algorithms.
# Note that this doesn't do anything to former individual exit BBlocks,
# so they likely still end with "return" instructions.
def cfg_single_exit(cfg):
    exits = cfg.exits()
    if len(exits) == 1:
        return

    newb = BBlock("single_exit")
    newb.cfg = cfg
    newb.add(Inst(None, "return", [], "single_exit"))
    cfg.add_node(newb.addr, val=newb)
    for e in exits:
        cfg.add_edge(e, newb.addr)


def sub_const_to_add(bblock):
    "Replace all subtractions of constant with adds."

    for inst in bblock.items:
        inst.dest = expr_xform(inst.dest, expr_sub_to_add)
        for i, a in enumerate(inst.args):
            inst.args[i] = expr_xform(a, expr_sub_to_add)


def expr_subst(expr, subst_dict):

    if isinstance(expr, (VALUE, ADDR, SFUNC)):
        return None

    if isinstance(expr, REG):
        new = subst_dict.get(expr, expr)
        return new

    if isinstance(expr, MEM):
        new = expr_subst(expr.expr, subst_dict)
        if new:
            return MEM(expr.type, new)
        return

    if isinstance(expr, COND):
        # This performs substituations in-place, because the same
        # COND instance is referenced in inst (to be later removed
        # by remove_trailing_jumps) and in out edges in CFG.
        new1 = expr_subst(expr.arg1, subst_dict)
        if new1:
            expr.arg1 = new1
        new2 = expr_subst(expr.arg2, subst_dict)
        if new2:
            expr.arg2 = new2
        simplify_cond(expr)
        return

    if isinstance(expr, EXPR):
        new_args = []
        was_new = False
        for a in expr.args:
            new = expr_subst(a, subst_dict)
            if new is None:
                new = a
            else:
                was_new = True
            new_args.append(new)
        if not was_new:
            return None

        new_expr = EXPR(expr.op, new_args)
        new_expr = expr_xform(new_expr, expr_associative_add)
        new_expr = expr_xform(new_expr, expr_simplify_add)
        return new_expr

    assert 0, type(expr)


def kill_subst_uses(subst, kill_var):
    "Remove from subst dict any expressions involving kill_var"
    def not_used(var, expr):
        # Here we assume that expression can be at most reference to a var,
        # which is true for at most copy propagation, but to handle expr
        # propagation, need to do better
        return var not in expr
    subst = dict((k, v) for k, v in subst.items() if not_used(kill_var, v))
    # We of course should kill state for var itself
    subst.pop(kill_var, None)
    return subst


def bblock_propagation(bblock, propagated_types):
    state = bblock.props.get("state_in", {})
    for i, inst in enumerate(bblock.items):

        if isinstance(inst.dest, MEM):
            new = expr_subst(inst.dest, state)
            if new:
                inst.dest = new

        args = inst.args

        all_args_const = True
        for arg_no, arg in enumerate(args):
            repl = expr_subst(arg, state)
            if repl:
                args[arg_no] = repl
            if not isinstance(args[arg_no], VALUE):
                all_args_const = False

        if inst.dest:
            # Calling kill_subst_uses isn't really needed for const propagation
            # (as variables aren't propagated), but needed for copy propagation
            # and higher.
            state = kill_subst_uses(state, inst.dest)
            if inst.op == "=" and isinstance(inst.args[0], propagated_types):
                state[inst.dest] = inst.args[0]

    bblock.props["state_out"] = state


def bblock_const_propagation(bblock):
    "Propagate only constant values"
    bblock_propagation(bblock, (VALUE, ADDR))

def bblock_copy_propagation(bblock):
    "Propagate constants and register copies"
    bblock_propagation(bblock, (VALUE, ADDR, REG))

def bblock_mem_propagation(bblock):
    "Propagate constants and register copies"
    bblock_propagation(bblock, (VALUE, ADDR, REG, MEM))

def bblock_expr_propagation(bblock):
    "Propagate constants and register copies"
    bblock_propagation(bblock, (VALUE, ADDR, REG, MEM, EXPR))


def collect_state_in(cfg):
    # This is pretty backwards actually. It uses ReachDef information,
    # but post-processes it pretty heavily, and instead should be done
    # as a dataflow analysis itself.
    changed = False
    for bblock_addr, node_props in cfg.iter_sorted_nodes():
        org_state = node_props["val"].props.get("state_in", {})
        state = org_state.copy()
        by_var = defaultdict(set)
        for reg, from_bblock in node_props["reachdef_in"]:
            by_var[reg].add(from_bblock)
        #print(bblock_addr, by_var)
        for var, from_bblocks in by_var.items():
            val_set = set()
            for bb in from_bblocks:
                val = None
                if bb is not None:
                    val = cfg[bb]["val"].props["state_out"].get(var)
                if val is None:
                    val_set = set()
                    break
                val_set.add(val)
            if len(val_set) == 1:
                state[var] = val_set.pop()
            elif len(val_set) > 1:
                print("Warning: %s: in value set for %s are: %s" % (bblock_addr, var, val_set))
        if state != org_state:
            node_props["val"].props["state_in"] = state
            changed = True

    return changed


def propagate(cfg, bblock_propagator):
    while True:
        foreach_bblock(cfg, bblock_propagator)
        if not collect_state_in(cfg):
            break


def const_propagation(cfg):
    propagate(cfg, bblock_const_propagation)

def copy_propagation(cfg):
    propagate(cfg, bblock_copy_propagation)

def mem_propagation(cfg):
    propagate(cfg, bblock_mem_propagation)

def expr_propagation(cfg):
    propagate(cfg, bblock_expr_propagation)


def insert_sp0(cfg):
    entry_addr = cfg.entry()
    first_bblock = cfg[entry_addr]["val"]
    first_bblock.items.insert(0, Inst(REG("sp"), "=", [REG("sp0")], addr=entry_addr + ".sp0"))


def rewrite_stack_vars(bblock):
    "Rewrite memory references relative to sp0 to local variables."
    def mem2loc(m):
        if is_mem(m) and set(m.regs()) == {REG("sp0")}:
            name = "loc" + str(m.expr.args[1].val).replace("-", "_") + "_" + str(m.type)
            return CVAR(name)

    for i, inst in enumerate(bblock.items):
        if inst.dest:
            inst.dest = mem2loc(inst.dest) or inst.dest

        for arg_no, arg in enumerate(inst.args):
            inst.args[arg_no] = expr_xform(arg, mem2loc)


import dataflow
def analyze_live_vars(cfg):
    ana = dataflow.LiveVarAnalysis(cfg)
    ana.solve()

def analyze_reach_defs(cfg):
    ana = dataflow.ReachDefAnalysis(cfg)
    ana.solve()


def estimate_args(cfg):
    ana = dataflow.LiveVarAnalysis(cfg, skip_calls=True)
    ana.solve()
    func_addr = cfg.entry()
    e = cfg[func_addr]
    import arch
    e["estimated_args"] = e["live_in"] & arch.call_args(func_addr)


def repr_output(cfg):
    import core
    core.SimpleExpr.simple_repr = False
