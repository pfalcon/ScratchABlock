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


### Virtual registers

Start with `$` (chosen because some C compilers, like GCC, allow `$` to
be part of an identifier), followed by a normal identifer. Examples:

```c
$a0, $a1, $r, $eax, $long_virtual_reg
```

Virtual registers are effectively "variables" of a PseudoC program, and
may be sometimes called as such in the documentation/code. But generally,
this should be avoided, to not confuse them with C-level variables.
Currently, registers are assumed to be unsigned. Where for a particular
operation it's important that register's contents are interpreted as a
signed value, it's explicitly cast just for that operation (see below).


### Types

PseudoC uses a very simple type system, consisting of signed and unsigned
integers, represented in a form contracted from `<stdint.h>`:

* Unsigned: `u8`, `u16`, `u32`, `u64`, etc.
* Signed: `i8`, `i16`, `i32`, `i64`, etc.

The sizes of types (in bits) are generally expected to be powers of 2,
up to word length of a CPU, but syntax allows arbitrary sizes.

For memory references (see below), there can be pointers to the types
above, e.g. `u8*`.

Types appear in few places in PseudoC program:

* Declaring types of CPU registers (tentative).
* When access memory, to cast numeric value in a register into a pointer
  to a type of needed size.
* To mark places where signed variants of operations are needed (or
  vice-versa, unsigned). In this usage, l-values remain l-values after
  cast, unlike C. E.g. `(i32)$r0 >>= 1` performs arithmetic shift right
  on a register `$r0`.
* For narrowing or widening values, where this usage has normal C
  semantics, e.g. `$r32 = (i16)$r32`, assuming `$r32` is 32-bit, will
  truncate it to 16 bits, then sign-extend the value to full 32 bits.


### Symbolic addresses

Addresses of memory locations are represented by an identifier. The
value of this identifier is a memory address. In other words, symbol's
value is an address constant. Note that in general, there're no numeric
addresses in a correct PseudoC program - i.e., PseudoC already assumes
that numeric data / addresses were already properly classified.


### Numeric constants

PseudoC supports decimal constants (consisting of all digits) and
hexadical constants (starting with `0x`). As mentioned above, numeric data
is assumed to be such - any address would be replaced by a symbol, e.g.
if `0x406ef` is an address, it should be represented as e.g. `data_406ef`.
A constant may be prefixed with `-` to signify that it's negative. PseudoC
assumes two's complement representation of negative numbers (and may
convert negative number to unsigned representation if needed).


### Operators

The C syntax and precedence rules are used for operators, including
compound assignments for "two address instruction" form. The following
operators are supported: `-` (unary minus), `!` (logical not), `(<type>)`
(type cast), `*` (unary, pointer dereference, must be followed by explicit
cast to a pointer type), `*`, `/`, `%` (modulo), `+`, `-`, `<<`, `>>`,
`<`, `<=`, `>=`, `>`, `==`, `!=`, `&`, `^`, `|`, `&&`, `||`.

The following C operators are not supported by PseudoC:

* `++` and `--` - use `$var += 1` and `$var -= 1` instead.
* Unary `&` - in assemebler (and thus PseudoC), there's no concept of
  "memory variable", just an address and way to access (dereference) it.
  Thus, unary `&` isn't needed either. (Unary `&` might appear in lifted
  PseudoC.)
* `=` and compound assignments - these are supported in PseudoC, but are
  statements, not operators. In other words, syntax like
  `$r0 = $r1 = $r2 + 1` is not supported (should be 2 separate stamenents,
  `$r1 = $r2 + 1` and `$r0 = $r1`). *Future*: If an actual CPU architecture
  is found with "multiple assignments", this syntax could be support as
  "macro-like extension" (see below).
* `.`, `->` - As there are no structures in PseudoC, there are no operators
  for field access. `.` actually can be a part of identifier in ScratchABlock
  (not formally part of PseudoC).
* `?:` - ternary operator is not supported, explicit `if` statement should be
  used instead.
* `,` - sequential operator not supported. *Future*: as alternative, multiple
  `;`-separated statements on the same line could be allowed.

Example of operators (used as part of assignment statements):

```c
$a0 = $a1 + $a2
$eax += $ebx
```

Operations like `*`, `/`, `%`, `>>` may have different forms for signed and
unsigned cases. As mentioned above, PseudoC currently defaults to
unsigned operations. Where signed operations are performed, arguments
should be cast to a signed type. E.g.:

```c
$a0 = (i32)$a1 * (i32)$a2
$eax = (i32)$eax >> 2
```


### Jumps

Unconditional jumps are represented by:

```c
goto label
```

Where `label` is address symbol.

Conditional jumps:

```c
if (condition) goto label
```

A condition can be (among other things):

* `$Z == 0` (Z flag is zero)
* `$S == 1 && $V == 0` (a combination of flags)
* `$a0 == $a1` (direct register comparison, typical for RISC)

Note that a comparison is another case when signed casts may be required:

```c
if ((i32)$a1 > (i32)$a2) goto less
```


### Special functions

Any CPU operation not representable by C-inspired operations above,
or any special operation in general, can be represented by a special
function. PseudoC defines inventory of generic special functions,
useful across different CPUs, and any particular CPU may define its
specific special functions. An example of generic special functions:

```c
// Rotate left
$a0 = rol($a0)
// Extract bitfield, with keyword-like arguments
$a0 = bitfield($a0, /*lsb*/0, /*sz*/5)
```

CPU specific special functions:

```c
// Maybe, disable interrupts
di()
// Maybe, read status register of coprocessor 2
$a0 = csr(2)
```

Note that this syntax is NOT used to represent calls to
functions/procedures defined in the PseudoC code.


### Accessing memory

The syntax is: `*(type*)expr`, i.e. a typical C pointer dereference,
with explicit cast of an expression to pointer type. Examples:

```c
$a0 = *(u32*)$a0
$a0 = *(u8*)($a1 + $a2)
$eax = *(u32*)($ebx + $ecx * 8 + 3)
```


### Calling functions/procedures

The syntax is similar to unconditional jumps: `call label` or `call expr`,
e.g.:

```c
call printf
call $eax
call *(u32*)($r0 + $r1 * 4)
```


Macro-like functionality
------------------------

PseudoC may support additional syntactic sugar, but generally, it's
expected that a parser may/will convert them to a number of individual
instructions from the repertoir above. Examples:

### Conditional instructions

Some pseudo-RISC CPUs support conditional instruction exection. PseudoC
allows syntax like:

```c
if (cond) operation
```

But it will be converted by the parser to:

```c
if (!cond) goto _skip
operation
_skip:
```


### Multiply-accumulate

Could be represented with:

```c
$bigreg += $small1 * $small2
```


### Macro-like special functions

(Not yet implemented.)

Special functions described above in general allow for concise
representation of cumbersome constructs, e.g.:

```c
// lt() hides flag combination for signed less
if (lt()) goto label
```

### Conditional flags

(Macros and pragmas are not yet implemented.)

The idea of dealing with conditional flags as use in conditional jump
instructions used in many architectures is to maintain and assign
explicitly to virtual registers representing conditinal flags. For
example, x86's Z flag can be named ``$Z``, ``$z``, ``$flags_z``, etc.
Potentially, it can be named even ``$flags.Z`` (i.e. structure field
syntax, likely, bitfield).

As an example, x86 ``cmp eax, ebx`` instruction's effect on Z flag could
be represented as:

```c
$cmp = $eax - $ebx
$Z = $cmp == 0
```

Of course, this instruction sets more flags, e.g. effect on Z, C, and S
flags could be represented as:

```c
$cmp = $eax - $ebx
$Z = $eax == $ebx
$C = $eax < $ebx
$S = (i32)$cmp < 0
```

An instruction which sets flags may overwrite a source register, but its
original value may be needed to properly calculate flags, so it may need
to be preserved, e.g. for ``sub eax, ebx``:

```c
$eax_ = $eax
$ebx_ = $ebx
$eax = $eax - $ebx
$Z = $eax_ == $ebx_
$C = $eax_ < $ebx_
$S = (i32)$eax < 0
```

As can be seen, such conversion can lead to quite verbose PseudoC
instruction sequences. Many superfluous assignments will be removed
by further processing (expression propagation and dead code elimination),
but input PseudoC is still very verbose. As human-readability is one
of the main goals of the format, there are still further ideas how
to make it less verbose:

1. Implicit macros. Perhaps, these would be activated by "pragma", and
could automatically add assignments to save original contents of the
registers, e.g.:

```c
#pragma save_org_regs
$eax = $eax - $ebx
$ecx = $eax + $ebx
```

would translate (during parsing) to:

```c
$eax_ = $eax
$ebx_ = $ebx
$eax = $eax - $ebx
$eax_ = $eax
$ebx_ = $ebx
$ecx = $eax + $ebx
```

2. Macro to set flags, e.g. x86 ``sub eax, ebx`` and ``add ecx, edx``
could be converted to:

```c
#pragma save_org_regs
SUBFLAGS($eax, $ebx)
$eax = $eax - $ebx
ADDFLAGS($ecx, $edx)
$ecx = $ecx + $edx
```

Instruction addresses (interpreted symbolically)
------------------------------------------------

For a particular PseudoC program, each line may be prefixed by an
address. This address is interpreted symbolically, not numerically.
This is to facilitate insertion of new statements in a program.
Addresses are compared lexicographically, not numerically, so for
proper operation they should be e.g. of the same width. If an
explicit addresses are not given, an implicit address is assigned,
based on the line number of the instruction.


Example of PseudoC program:

```c
// if-else
10  if (!$a1) goto l30
20  $a2 = 1
21  goto l40
30 l30:
20  $a2 = 2
40 l40:
40  $a3 = 0
```
