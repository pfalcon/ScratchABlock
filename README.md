[![Build Status](https://travis-ci.org/pfalcon/ScratchABlock.png?branch=master)](https://travis-ci.org/pfalcon/ScratchABlock)

**Q**: Why is there a need for yet another decompiler, especially a
crippled one?

**A**: A sad truth is that most decompilers out there are crippled. Many
aren't able to decompile trivial constructs, others can't decompile more
advanced, those which seemingly can deal with them, are crippled by
supporting only the boring architectures and OSes. And almost every
written in such a way that tweaking it or adding a new architecture is
complicated. A decompiler is a tool for reverse engineering, but ironically,
if you want to use a typical decompiler productively or make it suit your
needs, first you will need to reverse-engineer the decompiler itself, and
that can easily take months (or years).

How ScratchABlock is different?
-------------------------------

The central part of a decompiler (and any program transformation framework)
is Intermediate Representation (IR). A decompiler should work on IR, and
should take it as an input, and conversion of a particular architecture's
assembler to this IR should be well decoupled from a decompiler, or
otherwise it takes extraordinary effort to add support for another
architecture (which in turn limits userbase of a decompiler).

Decompilation is a complex task, so there should be easy insight into the
decompilation process. This means that IR used by a decompiler should be
human-friendly, for example use a syntax familiar to programmers, map as
directly as possible to a typical machine assembler, etc.

The requirements above should be quite obvious on their own. If not, they
can be learnt from the books on the matter, e.g.:

> "The compiler writer also needs mechanisms that let humans examine the IR
> program easily and directly. Self-interest should ensure that compiler
> writers pay heed to this last point."
>
> (Keith Cooper, Linda Torczon, "Engineering a Compiler")

However, decompiler projects, including OpenSource ones, routinely violate
these requirements: they are tightly coupled with specific machine
architectures, don't allow to feed IR in, and oftentimes don't expose or
document it to user at all.

ScratchABlock is an attempt to say "no" to such practices and develop a
decompilation framework based on the requirements above. Note that
ScratchABlock can be considered a learning/research project, and beyond
good intentions and criticism of other projects, may not offer too much
to a casual user - currently, or possibly at all. It can certainly be
criticised in many aspects too.


Down to Earth part
------------------

ScratchABlock is released under the terms of GNU General Public License v3
(GPLv3).

ScratchABlock is written in Python3 language, and tested with version 3.3
and up, though may work with 3.2 or lower too (won't work with legacy
Python2 versions). There're a few dependencies:

* PyYAML, https://pypi.python.org/pypi/PyYAML
* nose-tests, https://pypi.python.org/pypi/nose (required only for unit
  tests).

On Debian/Ubuntu Linux, these can be installed with
`sudo apt-get install python3-yaml python3-nose`. Alternatively, you can
install these via Python's own `pip` package manager with (should work for
any OS): `pip3 install -r requirements.txt`.

ScratchABlock uses the *PseudoC* assembler as its IR. It is an assembler
language expressed as much as possible using the familiar C language
syntax. The idea is that any C programmer would understand it intuitively
([example](tests/ifelse2.lst)), but there is an ongoing effort to
[document PseudoC more formally](docs/PseudoC-spec.md).

Source code and interfacing scripts are in the root of the repository.
The most important scripts are:

* `apply_xform.py` - A central driver, allows to apply a sequence of
transformations (or in general, high-level analysis/transformation
scripts) to a single file or a directory of files ("project directory").

* `inter_dataflow.py` - Interprocedural (global) dataflow analysis driver
  (WIP).

* `script_*.py` - High-level analysis/transformation scripts for
   `apply_xform.py` (`--script` switch).

* `script_i_*.py` - Analysis scripts for `inter_dataflow.py`.

* `run_tests` - The regregression testsuite runner. The majority of
testsuite is high-level, consisting of running apply_xform.py with
different passes on file(s) and checking the expected results.

Other subdirectories of the repository:

* `tests_unit` - Classical unit tests for Python modules, written in
Python.

* `tests` - The main testsuite. While integrational in the nature, it
usually tests one pass on one simple file, so follows the unit testing
philosophy. Tests are represented as PseudoC input files, while
expected results - as PseudoC with basic blocks annotation and (where
applicable) CFG in .dot format. Looking at these testcases, trying
to modify them and seeing the outcome is the best way to learn how
ScratchABlock works.

* `docs` - A growing collection of documentation. For example, there's a
[specification](docs/PseudoC-spec.md) of the PseudoC assembler language
serving as the intermediate representation (IR) for ScratchABlock and
a [survey](docs/ir-why-not.md) why another existing IR was not selected.

The current approach of ScratchABlock is to grow a collection of
relatively loosely-coupled algorithms for program analysis and
transformation, have them covered with tests, and allow easy user
access to them. The magic of decompilation consists of applying these
algorithms in the rights order and right number of times. Then, to
improve the performance of decompilation, these passes usually require
more tight coupling. Exploring those directions is the next
priority after implementing the inventory of passes as described
above.

Algorithms and transformations implemented by ScratchABlock:

* Graph algorithms:
  * Construction and querying (predecessors, successors, etc.)
  * Traversal (depth first search (DFS), postorder)
  * Dominator tree
  * Node splitting

* Data flow analysis:
  * Generic iterative dataflow algorithm framework
  * Dominator tree
  * Reaching definitions
  * Live variables
  * Building def-use chains

* Propagation:
  * Constant
  * Copy
  * Memory references
  * Expressions

* Dead code elimination (DCE)

* Rewriting:
  * Of stack variables
  * Of structure fields (TODO)
  * Devirtualization (TODO)

* Control flow structuring:
  * Removal of jumps-over-jumps
  * Single exit
  * Loop single landing site
  * if/if-else/if-elif-else ladders
  * Control-flow "and" (if (a && b))
  * Abnormal selection via node splitting
  * while/do-while/infinite loops
  * Generic loop structuring (TODO)
  * Unreachable basic blocks elimination (TODO)

* Output formats:
  * PseudoC
  * PseudoC with annotated basic blocks
  * C
  * .dot (for control flow (CFGs) and other graphs)
  * YAML (for function properties database)

ScratchABlock's partner tool is [ScratchABit](https://github.com/pfalcon/ScratchABit),
which is an interactive disassemler intended to perform the lowest-level
tasks of decompilation process, like separation of code from data, and
identifying function boundaries. ScratchABit produces a PseudoC output
(subject to plugin availability for a particular CPU architecture),
which can serve as input to ScratchABlock.
