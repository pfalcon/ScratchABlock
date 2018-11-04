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

from core import Inst


def remove_sfunc(bblock, name):
    for i, inst in enumerate(bblock.items):
        if inst.op == "SFUNC" and inst.args[0].args[0].name == name:
            dead = Inst(None, "DEAD", [])
            dead.addr = inst.addr
            bblock.items[i] = dead
            bblock.items[i].comments["org_inst"] = inst
