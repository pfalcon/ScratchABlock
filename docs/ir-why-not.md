ScratchABlock uses PseudoC, a machine-independent assembler with C-like
syntax, inspired by Radare2.

This documents why other existing compiler/decompiler IRs were not
choosen instead.

LLVM IR
-------

LLVM IR is by definition in SSA form, and converting normal code to SSA
form (and back) is a task on its own. Also, LLVM IR has obfuscation
features like implicit labels (TODO: ref ticket). Finally, LLVM IR
is strictly typed, with high-level types. These are counter-productive
for disassembly representation, where machine instruction deal with
simple, dynamic types.

BinNavi REIL, Valgrind VEX
--------------------------

All these decompiler IRs are designed with CISC X86 architecture in
mind, and take for granted that single machine instructions is
converted to number of IR instructions. That alone makes them not
human-friendly, but they also feature over-explicit, verbose syntax.

Radare2 ESIL
------------

https://github.com/radare/radare2/wiki/ESIL

"Forth-like representation for every opcode", which makes it a joke
of human-readability.


References
----------
* http://indefinitestudies.org/2009/04/03/a-quick-survey-on-intermediate-representations-for-program-analysis/
