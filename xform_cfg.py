# Copyright (c) 2015-2018 Paul Sokolovsky
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""Transformation passes on CFG"""

import logging
from collections import defaultdict

from core import *
from cfgutils import *
from dce import *
from xform_expr import *
from xform_inst import *
from xform_bblock import *
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
    log.info("Ran %s %d times" % (func, cnt))
    return cnt


def check_prop(cfg, prop_name, err_msg):
    entry_addr = cfg.entry()
    if prop_name not in cfg[entry_addr]:
        assert 0, err_msg


def number_postorder(cfg):
    cfg.number_postorder()


def number_postorder_from_exit(cfg):
    cfg.number_postorder_from_exit("_EXIT_")


def remove_trailing_jumps(cfg):
    remove_returns = False
    exits = cfg.exits()
    if len(exits) == 1:
        remove_returns = True

    foreach_bblock(cfg, remove_trailing_jumps_bblock, remove_returns=remove_returns)
    cfg.props["trailing_jumps"] = False


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


def remove_unreachable_nodes(cfg):
    "Remove CFG nodes not reachable from entry."
    assert "dfsno" in cfg[cfg.first_node], "Need number_postorder"

    for node, info in list(cfg.iter_nodes()):
        if info["dfsno"] is None:
            cfg.remove_node(node)


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
            log.info("jump_over_jump: removed node: %s", v)
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
            log.info("loop_single_entry: node: %s", v)
            log.info("back_preds: %s", back_preds)
            back_jumps = list(filter(lambda x: cfg.degree_out(x) == 1, back_preds))
            log.info("back_jumps: %s", back_jumps)
            # find existing landing site
            landing_site = None
            for p in back_jumps:
                b = cfg.node(p)["val"]
                if not b.items:
                    landing_site = p
            if not landing_site:
                farthest = max(back_preds)
                log.info("farthest: %s", farthest)
                newb = BBlock(farthest + "_1")
                cfg.add_node(newb.addr, val=newb)
                cfg.add_edge(newb.addr, v)
                landing_site = newb.addr
            log.info("landing_site: %s", landing_site)
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
        entryb = BBlock(".ENTRY")
        entryb.cfg = cfg
        cfg.add_node(entryb.addr, val=entryb)
        cfg.add_edge(entryb.addr, first)

    # Can still have multiple entries at this point
    assert len(cfg.entries()) >= 1


# Unconditionally add a new empty entry node, to hold anything needed later
def cfg_preheader(cfg):
    first = cfg.first_node
    if 1: #cfg.pred(first):
        entryb = BBlock(".ENTRY")
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

    exitb = BBlock("_EXIT_")
    exitb.cfg = cfg
    exitb.add(Inst(None, "return", [], addr=exitb.addr))
    cfg.add_node(exitb.addr, val=exitb)
    for e in exits:
        cfg.add_edge(e, exitb.addr)

    if not exits:
        # Infinite loop
        cfg.props["noreturn"] = True


# This pass finds infinite loops, and adds virtual exit edges from
# them (effectively turning infinite loops into "do {...} while (1)"
# loops) to a special "_DEADEND_" node, which in turn is connected to
# the single exit node. Using intermediate deadend node will allow
# later to remove these virtual edges easily, and also to have a
# single adhoc rule for live var analysis, that live-out of DEADEND
# is empty.
def cfg_infloops_exit(cfg):

    deadend_nodes = []

    for addr, info in cfg.iter_nodes():
        # We're interested only in nodes unreachable from exit
        if info["dfsno_exit"]:
            continue

        succ = cfg.succ(addr)
        if not succ:
            continue
        my_dfs = info["dfsno"]
        deadend = True
        for s in succ:
            if cfg[s]["dfsno"] < my_dfs:
                deadend = False
                break
        if deadend:
            #print("deadend:", addr)
            deadend_nodes.append(addr)

    if deadend_nodes:
        if not cfg.props.get("noreturn"):
             cfg.props["has_infloops"] = True

        # Add intermediate node, so later we can remove it, and all
        # extra edges are gone
        bb = BBlock("_DEADEND_")
        bb.cfg = cfg
        cfg.add_node("_DEADEND_", val=bb)
        cfg.add_edge("_DEADEND_", "_EXIT_", cond=VALUE(0, 10))
        for d in deadend_nodes:
            cfg.add_edge(d, "_DEADEND_", cond=VALUE(0, 10))

        # Graph was modified
        return True


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


def propagate(cfg, bblock_propagator):
    check_prop(cfg, "reachdef_in", "This pass requires reaching defs information")
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
    check_prop(cfg, "live_in", "This pass requires live variable information")
    used_regs = cfg[entry_addr]["live_in"]
    first_bblock = cfg[entry_addr]["val"]
    for i, r in enumerate(sorted(list(used_regs))):
        first_bblock.items.insert(i, Inst(r, "=", [REG(r.name + "_0")], addr=entry_addr + ".init%d" % i))


def insert_params(cfg):
    entry_addr = cfg.entry()
    first_bblock = cfg[entry_addr]["val"]
    for i, reg in enumerate(sorted(list(arch.call_params(cfg.props["name"])))):
        first_bblock.items.insert(i, Inst(reg, "=", [REG("arg_" + reg.name)], addr=entry_addr + ".arg%d" % i))


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
    progdb.update_cfg_prop(cfg, "preserveds", preserveds)


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
    if "reachdef_out" in cfg.node(exit):
        all_defs2 = set(x[0] for x in cfg.node(exit)["reachdef_out"])
        assert all_defs1 == all_defs2, "%r vs %r" % (all_defs1, all_defs2)
    progdb.update_cfg_prop(cfg, "reach_exit", all_defs1)
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

    if mod_maybe or "reach_exit_maybe" in cfg.props:
        progdb.update_cfg_prop(cfg, "reach_exit_maybe", mod_maybe)


import dataflow
def analyze_live_vars(cfg, **kwargs):
    ana = dataflow.LiveVarAnalysis(cfg, **kwargs)
    ana.solve()

def analyze_reach_defs(cfg):
    ana = dataflow.ReachDefAnalysis(cfg)
    ana.solve()

def analyze_dom(cfg):
    ana = dataflow.DominatorAnalysis(cfg)
    ana.solve()


# Regs in live_in set on function entry are estimated params
# (may miss something, e.g. if value in a reg is passed thru
# (without referencing it) to another function).
def estimate_params(cfg):
    #ana = dataflow.LiveVarAnalysis(cfg, skip_calls=True)
    #ana.solve()
    check_prop(cfg, "live_in", "This pass requires live variable information")
    func_addr = cfg.entry()
    assert func_addr == ".ENTRY", "cfg_preheader pass required"
    real_entry = cfg.succ(func_addr)
    assert len(real_entry) == 1
    real_entry = real_entry[0]
    e = cfg[real_entry]
    args = set(REG(r.name[:-2] if r.name.endswith("_0") else r.name) for r in e["live_in"])
    args -= set([REG("sp")])
    progdb.update_cfg_prop(cfg, "estimated_params", args)


# Precisely compute func params
def collect_params(cfg):
    func_addr = cfg.entry()
    e = cfg[func_addr]
    args = set(REG(r.name[:-2] if r.name.endswith("_0") else r.name) for r in e["live_in"])
    args = arch.param_filter(args)
    progdb.update_cfg_prop(cfg, "params", args)


# Kind of "AI" telling why this or that reg has got into "params" list.
# The explanations are approximate, e.g. a register may be "modified only
# along some paths" (especially if overestimated as modified in the
# presense of unknown functions), and still be a genuine param.
def annotate_params(cfg):
    res = {}
    for reg in cfg.props["params"]:
        if reg in cfg.props.get("estimated_params", ()):
            res[reg] = "100% genuine param"
        elif reg == REG("sp"):
            res[reg] = "Param because address of object on stack is taken"
        elif reg in cfg.props.get("reach_exit_maybe", ()):
            res[reg] = "Param because modified only along some paths (and maybe param to some callee)"
        else:
            res[reg] = "Likely param passed down to some callee"

    cfg.props["params_why"] = res
    #progdb.update_cfg_prop(cfg, "params_why", res)


# Collect regs which are live after each function call within current
# function. Triples of (bblock_addr, func, live_out) are stored in CFG's
# "calls_live_out" property (to be later further unioned and stored in
# funcdb). This corresponds to Van Emmerik's callsite use collector.
def collect_call_live_out(cfg):

    calls_live_out = []
    def collect(node):
        bb = node["val"]
        if bb.items and bb[-1].op == "call":
            inst = bb[-1]
            arg = inst.args[0]
            # TODO: Perhaps filter in the real regs?
            regs = {r for r in node["live_out"] if not r.name.endswith("_0")}
            calls_live_out.append((bb.addr, arg, regs))

    foreach_node(cfg, collect)
    progdb.update_cfg_prop(cfg, "calls_live_out", calls_live_out)


def repr_output(cfg):
    import core
    core.SimpleExpr.simple_repr = False
