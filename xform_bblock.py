# ScratchABlock - Program analysis and decompilation framework
#
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

"""Transformation passes on basic blocks"""

from core import *
from xform_expr import expr_subst


def remove_sfunc(bblock, name):
    for i, inst in enumerate(bblock.items):
        if inst.op == "SFUNC" and inst.args[0].args[0].name == name:
            dead = Inst(None, "DEAD", [])
            dead.addr = inst.addr
            bblock.items[i] = dead
            bblock.items[i].comments["org_inst"] = inst


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


def bblock_propagation(bblock, propagated_types, subst_insts=True):

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

    state = bblock.props.get("state_in", {})
    for i, inst in enumerate(bblock.items):

        n_dest = inst.dest
        kill_n_dest = False
        if isinstance(n_dest, MEM):
            new = expr_subst(n_dest, state)
            if new:
                n_dest = new
                kill_n_dest = True

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

        if kill_n_dest:
            # Need to kill n_dest, which was MEM and could have been substituted
            # TODO: Propagating MEM references is in general not safe
            state = kill_subst_uses(state, n_dest)

        if inst.op == "=" and isinstance(args[0], propagated_types):
            # Don't propagate expressions with side effects
            if not inst.side_effect():
                assert n_dest
                state[n_dest] = args[0]

        if subst_insts:
            if inst.op == "if":
                # Replace in-place because of if statement/out-edges label shared COND
                inst.args[0].expr = args[0].expr
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
