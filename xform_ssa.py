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

from core import *
import xform_cfg


def insert_phi_maximal(cfg):
    """Insert phi functions to produce maximal SSA form.

    Described e.g. in Appel 1998 "SSA is Functional Programming" (not named
    "maximal" there, but the name is quite obvious, especially if contrasted
    with well-known "minimal SSA form"):

    "A really crude approach is to split every variable at every basic-block
    boundary, and put φ-functions for every variable in every block"

    The algorithm below already contains an obvious optimization - phi
    functions are inserted only to blocks with multiple predecessors.
    """

    all_vars = sorted(xform_cfg.local_defines(cfg))

    for n, nprops in cfg.iter_nodes():
        if cfg.degree_in(n) > 1:
            bb = cfg[n]["val"]
            preds = cfg.pred(n)
            phi_no = 0
            for v in all_vars:
                inst = Inst(v, "=", [EXPR("SFUNC", [SFUNC("phi")] + [v] * len(preds))], addr=bb.addr + ".phi_%s" % v.name)
                bb.items.insert(phi_no, inst)
                phi_no += 1
