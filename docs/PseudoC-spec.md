PseudoC assembly language
=========================

ScratchABlock uses PseudoC as its Intermediate Representation (IR)
language. PseudoC uses familiar, C-like syntax to represent a generic
RISC-like assembler. Following were requirements for choosing such
IR:

* Syntax should be automagically understood by any (qualified)
  programmer, what can be more familiar than C?
* A typical RISC assembler should map almost statement to statement
  to IR, to ensure human readability. (Situation is not so bright with
  CISC, but that's it - CISC.)

Basic syntactic elements of PseudoC are:



Virtual registers:

Start with "$" (chosen because some C compilers, like GCC, allow $ to
be part of identifier), followed by a normal identifer. Examples:

$a0, $a1, $r, $eax, $long_virtual_reg

Virtual registers are effectively "variables" of PseudoC program, and
may be sometimes called as such in the documentation/code. But generally,
this should be avoided, to not confuse them with C-level variables.
Currently, registers are assumed to be unsigned. Where for a particular
operation it's important that register's contents are interpreted as a
signed value, it's explicitly cast just for that operation (see below).


Symbolic addresses:

Addresses of memory locations are represented by an identifier. The
value of this identifier is a memory address. In other words, symbol's
value is an address constant. Note that in general, there're no numeric
addresses in a correct PseudoC program - i.e., PsuedoC already assumes
that numeric data / addresses were already properly classified.


Numeric constants:

PseudoC supports decimal constants (all digits) and hexadical constants
(starting with 0x). As mentioned above, numeric data is assumed to be
such - any address would be replaced by a symbol, e.g. if 0x406ef is an
address, it should be represented as e.g. data_406ef. A constant may be
prefixed with "-" to signify that it's negative. PseudoC assumes two's
complement representation of negative numbers (and may convert negative
number to unsigned representation if needed).


Operators:

C syntax is used for operators, including "two address" form. Otherwise,
syntax is normally "three address form". +, -, *, /, %, <<, >> operators
are supported. Note that ++ and -- aren't supported. Examples:

$a0 = $a1 + $a2
$eax += $ebx

Operations like *, /, %, >> may have different forms for signed and
unsigned case. As mentioned above, PseudoC currently defaults to
unsigned operations. Where signed operations is performed, arguments
should be cast to signed type. E.g.:

$a0 = (i32)$a1 * (i32)$a2
$eax = (i32)$eax >> 2


Jumps:

Unconditional jumps are represented by:

goto label

Where "label" is symbol.

Conditional jumps:

if (condition) goto label

Condition can be "$Z == 0" (Z flag is zero), "$S == 1 && $V == 0"
(combination of flags) "$a0 == $a1" (direct register comparison,
typical for RISC). Note that comparisons is another case when signed
casts may be required:

if ((i32)$a1 > (i32)$a2) goto less


Special functions:

Any CPU operation not representable by C-inspired operations above,
or any special operation in general, can be represented by a special
function. PseudoC defines inventory of generic special functions,
useful across different CPUs, and any particular CPU may define its
specific. Example of generic special functions:

// Rotate left
$a0 = rol($a0)
// Extract bitfield, with keyword-like arguments
$a0 = bitfield($a0, /*lsb*/0, /*sz*/5)

CPU specific special functions:

// Maybe, disable interrupts
di()
// Maybe, read status register of coprocessor 2
$a0 = csr(2)

Note that this syntax is NOT used to represent calls to functions/
procedures defined in the PsuedoC code.


Accessing memory

The syntax is: *(type*)expr. Examples:

$a0 = *(u32*)$a0
$a0 = *(u8*)($a1 + $a2)
$eax = *(u32*)($ebx + $ecx * 8 + 3)


Calling functions/procedures

The syntax is similar to unconditional jumps:

call label or call expr, e.g.

call printf
call $eax


Macro-like functionality
------------------------
PseudoC may support additional syntactic sugar, but generally, it's
expected that a parser may/will convert them to a number of individual
instructions from the repertoir above. Examples:

Conditional instructions

Some pseudo-RISC CPUs support conditional instruction exection. PseudoC
allows syntax like:

if (cond) operation

But it will be converted to:

if (!cond) goto _skip
operation
_skip:


Multiply-accumulate

Could be represented with:

$bigreg += $small1 * $small2


Special functions described above in general allow for concise
representation of cumbersome constructs, e.g.:

// lt() hides flag combination for signed less
if (lt()) goto label



Instruction addresses (interpreted symbolically):

For a particular PseudoC program, each line may be prefixed by an
address. This address is interpreted symbolically, not numerically.
This is to facilitate insertion of new statements in a program.
Addresses are compared lexicographically, not numerically, so for
proper operation should e.g. be of the same width. If explicit
addresses are not given, an implicit address is assigned, based
on the line number of the instruction.


Example of PseudoC program:

// if-else
10  if (!$a1) goto l30
20  $a2 = 1
21  goto l40
30 l30:
20  $a2 = 2
40 l40:
40  $a3 = 0
