import logging
from collections import defaultdict

from graph import Graph
from core import *
from cfgutils import *
from dce import *
from xform_expr import *
from utils import set_union
import arch
import progdb

import copy


log = logging.getLogger(__name__)

# Apply tranformation while it's possible
def apply_iterative(func, args):
    cnt = 0
    while func(*args):
        cnt += 1
    print("Ran %s %d times" % (func, cnt))


def check_pass(cfg, prop_name, err_msg):
    entry_addr = cfg.entry()
    if prop_name not in cfg[entry_addr]:
        assert 0, err_msg


def remove_sfunc(bblock, name):
    for i, inst in enumerate(bblock.items):
        if inst.op == "SFUNC" and inst.args[0].args[0].name == name:
            dead = Inst(None, "DEAD", [])
            dead.addr = inst.addr
            bblock.items[i] = dead
            bblock.items[i].comments["org_inst"] = inst


def remove_trailing_jumps(cfg):
    remove_returns = False
    exits = cfg.exits()
    if len(exits) == 1:
        remove_returns = True

    foreach_bblock(cfg, remove_trailing_jumps_bblock, remove_returns=remove_returns)
    cfg.props["trailing_jumps"] = False


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


def remove_unreachable_entries(cfg):
    # Remove disconnected graph nodes.
    entries = cfg.entries()
    if len(entries) == 1:
        return
    for e in entries:
        if e == cfg.props["addr"]:
            continue

        def remove_component(e):
            if cfg.pred(e):
                return
            succ = cfg.succ(e)
            try:
                cfg.remove_node(e)
            except KeyError:
                # Already removed
                pass
            for e in succ:
                remove_component(e)

        remove_component(e)


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


def cfg_single_entry(cfg):
    first = cfg.first_node
    if cfg.pred(first):
        # First (== entry) node has a backedge
        entryb = BBlock("0entry")
        entryb.cfg = cfg
        cfg.add_node(entryb.addr, val=entryb)
        cfg.add_edge(entryb.addr, first)

    # Can still have multiple entries at this point
    assert len(cfg.entries()) >= 1


# Unconditionally add a new empty entry node, to hold anything needed later
def cfg_preheader(cfg):
    first = cfg.first_node
    if 1: #cfg.pred(first):
        entryb = BBlock("0entry")
        entryb.cfg = cfg
        cfg.add_node(entryb.addr, val=entryb)
        cfg.add_edge(entryb.addr, first)
        cfg.first_node = entryb.addr

    # Can still have multiple entries at this point
    assert len(cfg.entries()) >= 1


# Make sure that CFG has a single exit, as required for some algorithms.
# Note that this doesn't do anything to former individual exit BBlocks,
# so they likely still end with "return" instructions.
def cfg_single_exit(cfg):
    exits = cfg.exits()
    if len(exits) == 1:
        return

    # Capture entry node before we add unconnected single exit node
    entry_addr = cfg.entry()

    exitb = BBlock("single_exit")
    exitb.cfg = cfg
    exitb.add(Inst(None, "return", [], addr="single_exit"))
    cfg.add_node(exitb.addr, val=exitb)
    for e in exits:
        cfg.add_edge(e, exitb.addr)

    if not exits:
        # Infinite loop
        cfg.props["noreturn"] = True

        old_entry_node = cfg.node(entry_addr)

        # Duplicate the original entry node as "entry.real"
        new_entry_addr = entry_addr + ".real"
        cfg.add_node(new_entry_addr, val=old_entry_node["val"])
        cfg.move_succ(entry_addr, new_entry_addr)

        ifb = BBlock(entry_addr)
        ifb.cfg = cfg
        ifb.add(Inst(None, "if", [VALUE(0), ADDR(exitb.addr)]))
        ifb.add(Inst(None, "goto", [ADDR(new_entry_addr)]))
        old_entry_node["val"] = ifb

        cfg.add_edge(entry_addr, exitb.addr, cond=VALUE(0))
        cfg.add_edge(entry_addr, new_entry_addr)


def sub_const_to_add(bblock):
    "Replace all subtractions of constant with adds."

    for inst in bblock.items:
        inst.dest = expr_xform(inst.dest, expr_sub_to_add)
        for i, a in enumerate(inst.args):
            inst.args[i] = expr_xform(a, expr_sub_to_add)


def expr_subst(expr, subst_dict):

    if isinstance(expr, (VALUE, STR, ADDR, SFUNC, TYPE)):
        return None

    if isinstance(expr, REG):
        new = subst_dict.get(expr)
        if new and expr in new:
            log.debug("Trying to replace %s with recursively referring %s, not doing" % (expr, new))
            return None
        if new and len(new) > 10:
            log.warn("Trying to replace %s with complex [len=%d] %s, not doing" % (expr, len(new), new))
            return None
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
        new_expr = simplify_expr(new_expr)
        return new_expr

    assert 0, repr((expr, type(expr)))


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


def bblock_propagation(bblock, propagated_types, subst_insts=True):
    state = bblock.props.get("state_in", {})
    for i, inst in enumerate(bblock.items):

        n_dest = inst.dest
        if isinstance(n_dest, MEM):
            new = expr_subst(n_dest, state)
            if new:
                n_dest = new

        args = copy.deepcopy(inst.args)

        for arg_no, arg in enumerate(args):
            repl = expr_subst(arg, state)
            if repl:
                args[arg_no] = repl

        for dest in inst.defs():
            # Calling kill_subst_uses isn't really needed for const propagation
            # (as variables aren't propagated), but needed for copy propagation
            # and higher.
            state = kill_subst_uses(state, dest)

        if inst.op == "=" and isinstance(args[0], propagated_types):
            assert n_dest
            state[n_dest] = args[0]

        if subst_insts:
            if inst.op == "if":
                # Replace in-place because of if statement/out-edges label shared COND
                assert is_cond(inst.args[0])
                inst.args[0].arg1 = args[0].arg1
                inst.args[0].op = args[0].op
                inst.args[0].arg2 = args[0].arg2
            else:
                inst.args = args
            inst.dest = n_dest

    bblock.props["state_out"] = state


def bblock_const_propagation(bblock, subst_insts=True):
    "Propagate only constant values"
    bblock_propagation(bblock, (VALUE, ADDR), subst_insts)

def bblock_copy_propagation(bblock, subst_insts=True):
    "Propagate constants and register copies"
    bblock_propagation(bblock, (VALUE, ADDR, REG), subst_insts)

def bblock_mem_propagation(bblock, subst_insts=True):
    "Propagate constants and register copies"
    bblock_propagation(bblock, (VALUE, ADDR, REG, MEM), subst_insts)

def bblock_expr_propagation(bblock, subst_insts=True):
    "Propagate constants and register copies"
    bblock_propagation(bblock, (VALUE, ADDR, REG, MEM, EXPR), subst_insts)


def simplify_inst(inst):
    if not (inst.dest and inst.op == "="):
        return
    assert len(inst.args) == 1
    inst.args[0] = simplify_expr(inst.args[0])


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
                log.debug("%s: in value set for %s are: %s" % (bblock_addr, var, val_set))
        if state != org_state:
            log.debug("CHANGED: %s: %r ==VS== %r" % (node_props["val"], org_state, state))
            node_props["val"].props["state_in"] = state
            changed = True

    return changed


def normalize_cond(cfg):
    "Normalize conditions so constants were on the right side."

    def norm(inst):
        if inst.op == "if":
            inst.args[0].normalize()

    foreach_inst(cfg, norm)


def propagate(cfg, bblock_propagator):
    check_pass(cfg, "reachdef_in", "This pass requires reaching defs information")
    while True:
        foreach_bblock(cfg, lambda bb: bblock_propagator(bb, False))
        if not collect_state_in(cfg):
            break
    foreach_bblock(cfg, lambda bb: bblock_propagator(bb, True))


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
    first_bblock.items.insert(0, Inst(REG("sp"), "=", [REG("sp_0")], addr=entry_addr + ".init0"))


# Generalization of insert_sp0
# For each register live on entry to function, insert to function pre-header
# assignment of $r = $r_0, where $r_0 represents an input register, whereas $r
# is a work register. Overall, this implements poor-man's (but very practical)
# SSA subset.
# Requires analyze_live_vars
def insert_initial_regs(cfg):
    entry_addr = cfg.entry()
#    used_regs = reversed(sorted([x[0] for x in cfg[entry_addr]["reachdef_in"]]))
    check_pass(cfg, "live_in", "This pass requires live variable information")
    used_regs = cfg[entry_addr]["live_in"]
    first_bblock = cfg[entry_addr]["val"]
    for i, r in enumerate(sorted(list(used_regs))):
        first_bblock.items.insert(i, Inst(r, "=", [REG(r.name + "_0")], addr=entry_addr + ".init%d" % i))


def insert_params(cfg):
    entry_addr = cfg.entry()
    first_bblock = cfg[entry_addr]["val"]
    for i, reg in enumerate(sorted(list(arch.call_params(cfg.props["name"])))):
        first_bblock.items.insert(i, Inst(reg, "=", [REG("arg_" + reg.name)], addr=entry_addr + ".arg%d" % i))


def rewrite_stack_vars(bblock, rewrite_to=CVAR):
    "Rewrite memory references relative to sp0 to local variables."
    def mem2loc(m):
        if is_mem(m) and is_expr(m.expr) and set(m.expr.regs()) == {REG("sp_0")}:
            name = "loc" + str(m.expr.args[1].val).replace("-", "_") + "_" + str(m.type)
            return rewrite_to(name)

    for i, inst in enumerate(bblock.items):
        if inst.dest:
            inst.dest = expr_xform(inst.dest, mem2loc)

        for arg_no, arg in enumerate(inst.args):
            inst.args[arg_no] = expr_xform(arg, mem2loc)


# Requires insert_initial_regs pass followed by expr_propagation passes
# (normal, then stack vars propagation), and should be run before DCE.
def collect_preserveds(cfg):
    exit_addr = cfg.exit()
    exit_bblock = cfg[exit_addr]["val"]
    state_out = exit_bblock.props["state_out"]
    preserveds = set()
    for k, v in state_out.items():
        if is_reg(k) and is_reg(v):
            if v.name == k.name + "_0":
                preserveds.add(k)
    cfg.props["preserveds"] = preserveds


# Requires expr_propagation
def collect_calls(cfg):
    calls = []
    calls_indir = []

    def collect(inst):
        if inst.op == "call":
            arg = inst.args[0]
            if is_addr(arg):
                calls.append(arg)
            else:
                calls_indir.append(arg)

    foreach_inst(cfg, collect)
    cfg.props["calls"] = calls
    if calls_indir:
        cfg.props["calls_indir"] = calls_indir


# While collect_calls collects direct calls, this pass
# collects function references by address. Requires
# funcdb to know what address is a function.
def collect_func_refs(cfg):
    refs = []

    def collect(inst):
        if inst.op == "=":
            arg = inst.args[0]
            if is_addr(arg):
                import progdb
                if arg.addr in progdb.FUNC_DB:
                    refs.append(arg)

    foreach_inst(cfg, collect)
    cfg.props["func_refs"] = refs


def collect_mem_refs(cfg, pred, prop_name="mem_refs"):
    """Collect references to non-symbolic memory address (ones represented
    by VALUE objects). This is useful e.g. to see which function accesses
    which MMIO addresses. Takes a predicate telling which addresses should
    be captured and property name to store summary.
    """
    refs = []

    def collect(inst):

        def collect_mmio(expr):
            if expr and is_mem(expr):
                mem = expr.expr
                if is_value(mem) and pred(mem.val):
                    refs.append(mem)
                elif is_expr(mem):
                    if mem.op != "+":
                        #print(mem.op, expr)
                        return
                    # TODO: This means that MMIO accessed as array
                    for a in mem.args:
                        if is_value(a) and pred(a.val):
                            #refs.append(a)
                            refs.append(mem)
                            break

        inst.foreach_subexpr(collect_mmio)

    foreach_inst(cfg, collect)
    if refs:
        #cfg.props[prop_name] = refs
        cfg.props[prop_name] = sorted(list(set(refs)))


def collect_reach_exit(cfg):
    all_defs1 = foreach_bblock(cfg, lambda b: b.defs(True), set_union)
    exit = cfg.exit()
    #all_defs2 = set(x[0] for x in cfg.node(exit)["reachdef_out"])
    #assert all_defs1 == all_defs2
    cfg.props["reach_exit"] = all_defs1
    return all_defs1


# Collect registers which may be either defined or not on the exit.
# These registers often represent parasitic arguments (as they
# may be either modified or not, the way to return the original value
# of the reg is take it as a param).
# Requires reachdef on raw CFG (before insert_initial_regs).
def collect_reach_exit_maybe(cfg):
    exit = cfg.exit()
    vardict = {}
    for var, addr in cfg.node(exit)["reachdef_out"]:
        vardict.setdefault(var, set()).add(addr)
    mod_maybe = set()

    for var, addrs in vardict.items():
        if len(addrs) > 1 and None in addrs:
            mod_maybe.add(var)

    if mod_maybe:
        cfg.props["reach_exit_maybe"] = mod_maybe


import dataflow
def analyze_live_vars(cfg):
    ana = dataflow.LiveVarAnalysis(cfg)
    ana.solve()

def analyze_reach_defs(cfg):
    ana = dataflow.ReachDefAnalysis(cfg)
    ana.solve()


# Regs in live_in set on function entry are estimated params
# (may miss something, e.g. if value in a reg is passed thru
# (without referencing it) to another function).
def estimate_params(cfg):
    #ana = dataflow.LiveVarAnalysis(cfg, skip_calls=True)
    #ana.solve()
    check_pass(cfg, "live_in", "This pass requires live variable information")
    func_addr = cfg.entry()
    e = cfg[func_addr]
    args = set(REG(r.name[:-2] if r.name.endswith("_0") else r.name) for r in e["live_in"])
    args -= set([REG("sp")])
    cfg.props["estimated_params"] = args


# Precisely compute func params
def collect_params(cfg):
    func_addr = cfg.entry()
    e = cfg[func_addr]
    args = set(REG(r.name[:-2] if r.name.endswith("_0") else r.name) for r in e["live_in"])
    progdb.update_cfg_prop(cfg, "params", args)


# Collect regs which are live after a function call. Intersection of
# this set with function's modifieds will be returns of a function.
def collect_call_live_out(cfg):
    import progdb

    def collect(node):
        bb = node["val"]
        if bb.items and bb[-1].op == "call":
            inst = bb[-1]
            arg = inst.args[0]
            if is_addr(arg):
                func = arg.addr
                regs = set(REG(r.name[:-2] if r.name.endswith("_0") else r.name) for r in node["live_out"])
                progdb.FUNC_DB.setdefault(func, {}).setdefault("callsites_live_out", set()).update(regs)

    foreach_node(cfg, collect)


def clear_call_live_out():
    import progdb
    for addr, props in progdb.FUNC_DB.items():
        if "callsites_live_out" in props:
            props["callsites_live_out"] = set()


def collect_returns():
    import progdb
    import arch
    for addr, props in progdb.FUNC_DB.items():
        if "modifieds" in props and "callsites_live_out" in props:
            props["returns"] = arch.ret_filter(set(props["modifieds"]) & set(props["callsites_live_out"]))


def repr_output(cfg):
    import core
    core.SimpleExpr.simple_repr = False
