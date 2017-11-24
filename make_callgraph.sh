#!/bin/sh
#
# Make a call graph in a .dot format for a number of functions
# in PseudoC assembler format, one function per a .lst file,
# put under the single directory.
#
# Usage: ./make_callgraph <directory_of_lsts>
#
# Generated callgraph will be in <directory_of_lsts>/callgraph.dot
#

set -e

DIR=$(dirname $0)

funcdir="$1"
shift

$DIR/correct_internal_entrypoint.py $funcdir
$DIR/apply_xform.py --script script_callgraph --format none $funcdir
$DIR/apply_xform.py --script script_callgraph_func_refs --format none $funcdir
$DIR/funcdb_dot.py $funcdir/funcdb.yaml -o $funcdir/callgraph.dot "$@"
$DIR/funcdb_util.py called_by $funcdir/funcdb.yaml
