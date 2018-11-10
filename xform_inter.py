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
import progdb


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
