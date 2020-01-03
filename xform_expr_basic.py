# ScratchABlock - Program analysis and decompilation framework
#
# Copyright (c) 2020 Paul Sokolovsky
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

from core import *


def expr_neg_if_possible(expr):
    if is_value(expr):
        return VALUE(-expr.val, expr.base)
    if is_expr(expr):
        if expr.op == "NEG":
            return expr.args[0]
        if expr.op == "+":
            new_args = [expr_neg(x) for x in expr.args]
            return EXPR("+", new_args)


def expr_neg(expr):
    new = expr_neg_if_possible(expr)
    if new:
        return new

    return EXPR("NEG", expr)
