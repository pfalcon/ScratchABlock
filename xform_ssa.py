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

"""SSA related transformations"""

from collections import defaultdict
from core import *
import xform_expr
import xform_cfg


def is_phi(inst):
    return inst.op == "=" and is_sfunc(inst.args[0], "phi")


def insert_phi_maximal(cfg, fully_maximal=False):
    """Insert phi functions to produce maximal SSA form.

    Described e.g. in Appel 1998 "SSA is Functional Programming" (not named
    "maximal" there, but the name is quite obvious, especially if contrasted
    with well-known "minimal SSA form"):

    "A really crude approach is to split every variable at every basic-block
    boundary, and put φ-functions for every variable in every block"

    The algorithm below already contains an obvious optimization - phi
    functions are inserted only to blocks with multiple predecessors. Note
    that this requires rename function to process basic block from successors
    to predecessors, to correctly propagate renamings thru such phi-less
    blocks. (If on the other hand we inserted phi's to each block, we could
    process their renaming in arbitrary order, because each basic block would
    have its local definition for every variable).
    """

    if fully_maximal:
        min_preds = 1
    else:
        min_preds = 2

    all_vars = sorted(xform_cfg.local_defines(cfg))

    for n, nprops in cfg.iter_nodes():
        if cfg.degree_in(n) >= min_preds:
            bb = cfg[n]["val"]
            preds = cfg.pred(n)
            phi_no = 0
            for v in all_vars:
                inst = Inst(v, "=", [EXPR("SFUNC", [SFUNC("phi")] + [v] * len(preds))], addr=bb.addr + ".phi_%s" % v.name)
                bb.items.insert(phi_no, inst)
                phi_no += 1


def insert_phi_fully_maximal(cfg):
    insert_phi_maximal(cfg, fully_maximal=True)


def rename_ssa_vars(cfg, use_addrs=False):
    """Generic routine to rename registers to follow SSA form.

    This should be called after phi-insertion pass, and this routine will
    work with insertion algorithm (whether constructing maximal, minimal,
    pruned or whatever form). Can rename registers to use either sequential
    subscripts or instruction addresses where register is defined.
    """

    def rename_reg(e):
        if is_reg(e):
            return REG("%s_%s" % (e.name, var_map[e.name]))

    if use_addrs:
        var_map = defaultdict(lambda: "0")
    else:
        var_map = defaultdict(int)

    # Process basic blocks in such a way that we have renamings (if any!) for
    # current block, before we proceed to its successors.
    for n in cfg.iter_rev_postorder():
        bb = cfg[n]["val"]

        # Rename variables within basic block.
        for inst in bb:
            # Don't rename args of phi funcs, those names come from
            # predecessor blocks.
            if not is_phi(inst):
                for i, arg in enumerate(inst.args):
                    inst.args[i] = xform_expr.expr_xform(arg, rename_reg)

            # Rename destination
            if is_reg(inst.dest):
                # If it's a register, this defines a new register version
                if use_addrs:
                    if is_phi(inst):
                        suffix = bb.addr + "_phi"
                    else:
                        suffix = inst.addr
                    var_map[inst.dest.name] = suffix
                else:
                    var_map[inst.dest.name] += 1
                inst.dest = rename_reg(inst.dest)
            else:
                # Otherwise, it's more complex expression which may contain
                # reference to reg as a subexpression
                inst.dest = xform_expr.expr_xform(inst.dest, rename_reg)

        # Now rename arguments of phi functions in successor blocks, in the
        # position which correspond to the current block's predecessor edge
        for next_n in cfg.succ(n):
            my_pos = cfg.pred(next_n).index(n)
            next_bb = cfg[next_n]["val"]
            for inst in next_bb:
                if not is_phi(inst):
                    break
                # +1 because first arg is SFUNC("phi")
                new_reg = rename_reg(inst.args[0].args[my_pos + 1])
                inst.args[0].args[my_pos + 1] = new_reg


def rename_ssa_vars_fully_maximal(cfg, use_addrs=False):

    def rename_reg(e):
        if is_reg(e):
            return REG("%s_%s" % (e.name, var_map[e.name]))

    if use_addrs:
        var_map = defaultdict(lambda: "0")
    else:
        var_map = defaultdict(int)

    # This algorithm could process basic blocks in any order. But for human
    # consumption, it's better when variable are numbered from the start of
    # a function.
    for n in cfg.iter_rev_postorder():
        bb = cfg[n]["val"]

        # Rename variables within basic block.
        for inst in bb:
            # Don't rename args of phi funcs, those names come from
            # predecessor blocks.
            if not is_phi(inst):
                for i, arg in enumerate(inst.args):
                    inst.args[i] = xform_expr.expr_xform(arg, rename_reg)

            # Rename destination
            if is_reg(inst.dest):
                # If it's a register, this defines a new register version
                if use_addrs:
                    if is_phi(inst):
                        suffix = bb.addr + "_phi"
                    else:
                        suffix = inst.addr
                    var_map[inst.dest.name] = suffix
                else:
                    var_map[inst.dest.name] += 1
                inst.dest = rename_reg(inst.dest)
            else:
                # Otherwise, it's more complex expression which may contain
                # reference to reg as a subexpression
                inst.dest = xform_expr.expr_xform(inst.dest, rename_reg)

        # Now rename arguments of phi functions in successor blocks, in the
        # position which correspond to the current block's predecessor edge
        for next_n in cfg.succ(n):
            my_pos = cfg.pred(next_n).index(n)
            next_bb = cfg[next_n]["val"]
            for inst in next_bb:
                if not is_phi(inst):
                    break
                # +1 because first arg is SFUNC("phi")
                new_reg = rename_reg(inst.args[0].args[my_pos + 1])
                inst.args[0].args[my_pos + 1] = new_reg


def rename_ssa_vars_subscripts(cfg):
    rename_ssa_vars(cfg, False)


def rename_ssa_vars_addrs(cfg):
    rename_ssa_vars(cfg, True)
