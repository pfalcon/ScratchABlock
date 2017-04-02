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

$DIR/apply_xform.py --script script_callgraph --format none $1
$DIR/funcdb_dot.py $1/funcdb.yaml -o $1/callgraph.dot
