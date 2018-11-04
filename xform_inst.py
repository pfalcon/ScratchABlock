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

"""Transformation passes on instructions"""

from xform_expr import *
import arch


def normalize_cond(inst):
    "Normalize conditions so constants are on the right side."
    if inst.op == "if":
        inst.args[0].normalize()


def booleanize_cond(inst):
    "Make conditions be of bool type (have bool operation)."
    if inst.op == "if":
        cond = inst.args[0]
        if not cond.is_relation():
            e = cond.expr
            if is_expr(e) and e.op == "!":
                new = EXPR("==", e.args[0], VALUE(0, 0))
            else:
                new = EXPR("!=", e, VALUE(0, 0))
            cond.expr = new


def sub_const_to_add(inst):
    "Replace subtractions of constant with adds."

    inst.dest = expr_xform(inst.dest, expr_sub_const_to_add)
    for i, a in enumerate(inst.args):
        inst.args[i] = expr_xform(a, expr_sub_const_to_add)


def simplify_inst(inst):
    if not (inst.dest and inst.op == "="):
        return
    assert len(inst.args) == 1
    inst.args[0] = simplify_expr(inst.args[0])


def struct_access_inst(inst):
    if not (inst.dest and inst.op == "="):
        return
    assert len(inst.args) == 1
    inst.args[0] = struct_access_expr(inst.args[0])


def rewrite_complex_dest(inst):
    "Rewrite casts and bitfield() on the left hand side of assignment."

    dest = inst.dest
    if not (inst.dest and inst.op == "="):
        return
    if not is_expr(inst.dest):
        return
    if dest.op == "CAST":
        lsb = 0
        size = dest.args[0].bitsize()
    elif dest.op == "SFUNC" and dest.args[0].name == "bitfield":
        assert is_value(dest.args[2]) and is_value(dest.args[3])
        lsb = dest.args[2].val
        size = dest.args[3].val
    else:
        assert 0

    inst.dest = dest.args[1]
    if lsb == 0 and size == arch.BITNESS:
        return

    all_ones = (1 << arch.BITNESS) - 1
    mask = (1 << size) - 1
    mask <<= lsb
    if lsb == 0:
        new_rhs = EXPR("&", inst.args[0], VALUE(mask))
    else:
        new_rhs = EXPR("&",
            EXPR("<<", inst.args[0], VALUE(lsb, 10)),
            VALUE(mask))

    inst.args[0] = EXPR("|",
        EXPR("&", inst.dest, VALUE(all_ones ^ mask)),
        new_rhs)


def rewrite_stack_vars(inst, rewrite_to=CVAR):
    "Rewrite memory references relative to sp0 to local variables."
    def mem2loc(m):
        if is_mem(m) and is_expr(m.expr) and set(m.expr.regs()) == {REG("sp_0")}:
            name = "loc" + str(m.expr.args[1].val).replace("-", "_") + "_" + str(m.type)
            return rewrite_to(name)

    if inst.dest:
        inst.dest = expr_xform(inst.dest, mem2loc)

    for arg_no, arg in enumerate(inst.args):
        inst.args[arg_no] = expr_xform(arg, mem2loc)
