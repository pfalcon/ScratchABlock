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

"""Interprocedural transformation passes"""

from graph import Graph
from core import is_addr
import progdb
from utils import maybesorted
import utils


def build_callgraph():
    "Build program callgraph from progdb."

    callgraph = Graph()

    for addr, props in progdb.FUNC_DB_BY_ADDR.items():
        callgraph.add_node(props["label"])

    for addr, props in progdb.FUNC_DB_BY_ADDR.items():
        for callee in props.get("calls", []):
            if callee in callgraph:
                callgraph.add_edge(props["label"], callee)

    callgraph.number_postorder_forest()

    return callgraph


def calc_callsites_live_out(cg, callee):
    """Calculate function's callsites_live_out property.

    Go thru function's callers (using callgraph), and union their
    calls_live_out information pertinent to this function.
    """

    callers = maybesorted(cg.pred(callee))
    # If there're no callers, will return empty set, which
    # is formally correct - if there're no callers, the
    # function is dead. However, realistically that means
    # that callers aren't known, and we should treat that
    # specially.
    call_lo_union = set()
    for c in callers:
        clo = progdb.FUNC_DB[c].get("calls_live_out", [])
        #print("  %s: calls_live_out: %s" % (c, utils.repr_stable(clo)))
        for bbaddr, callee_expr, live_out in clo:
            if is_addr(callee_expr) and callee_expr.addr == callee:
                print("  %s: calls_live_out[%s]: %s" % (c, callee, utils.repr_stable((bbaddr, callee_expr, live_out))))
                call_lo_union.update(live_out)

    progdb.FUNC_DB[callee]["callsites_live_out"] = call_lo_union

    return call_lo_union
