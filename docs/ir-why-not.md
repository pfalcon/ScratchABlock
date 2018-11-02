Survey of Intermediate Representations/Languanges (IR/IL) for Decompilation
===========================================================================

ScratchABlock uses PseudoC, a machine-independent assembler with C-like
syntax,
[an idea inspired](https://radare.gitbooks.io/radare2book/content/visual_mode/visual_disassembly.html#asmpseudo-enable-pseudo-syntax)
by Radare2.

This documents why other existing compiler/decompiler IRs were not
chosen instead.

LLVM IR
-------

LLVM IR is by definition in SSA form, and converting normal code to SSA
form (and back) is a task on its own. Also, LLVM IR has obfuscation
features like implicit labels (https://llvm.org/bugs/show_bug.cgi?id=16043).
Finally, LLVM IR is strictly typed, with high-level types. These are
counter-productive for disassembly representation, where machine instruction
deal with simple, dynamic types.

BinNavi REIL, Valgrind VEX
--------------------------

All these decompiler IRs are designed with CISC X86 architecture in
mind, and take for granted that a single machine instructions will be
converted to several IR instructions. That alone makes them not
human-friendly, but they also feature over-explicit, verbose syntax.

VEX is [used by angr](https://docs.angr.io/docs/ir.html). They also
[explain](https://docs.angr.io/docs/faq.html#why-did-you-choose-vex-instead-of-another-ir-such-as-llvm-reil-bap-etc)
why they didn't choose LLVM IR, etc.

Radare2 ESIL
------------

https://github.com/radare/radare2/wiki/ESIL

"Forth-like representation for every opcode", which makes it a joke
of human-readability.

Bare Bones Backend IR
---------------------

https://webkit.org/docs/b3/

B3 IR wasn't known to the author when ScratchABlock was started. What's
insightful though is a quote from [this page](https://trac.webkit.org/wiki/FTLJIT):
"The FTL JIT started out as a marriage of the DFG and LLVM. We are phasing out LLVM
support [...]. We are moving the FTL JIT to use the B3 backend instead of LLVM.
B3 is WebKit's own creation. WebKit tends to perform better with the B3." So,
people tried LLIR and associated technologies, and figured they can do better
and less bloated on their own. Per the main page, "B3 comprises a
[C-like SSA IR](https://webkit.org/docs/b3/intermediate-representation.html)".
C-likeness in their terms mean: a) uses function call syntax to represent
operations; b) uses a simple type system (comparing to LLIR's). In this regard,
PseudoC is only further extension of this idea, using native C operators where
possible, and otherwise trying to stick to "real" C syntax. For example, B3 IR's

    Int32 @2 = Add(@0, @1)

corresponds to PseudoC's (assuming implicit size of regsiters to be 32):

    $r2 = $r0 + $r1

So, overall, B3 IR and PseudoC are very similar, and differences come from
different target usage (B3 IR is JIT IR, PseudoC is decompilation IR).

HHVM IR
-------

Another IR which wasn't known to the author when ScratchABlock was started.

Facebook's PHP HipHop VM (HHVM) uses own IR, HHIR. Just quoting
[slide 36](https://image.slidesharecdn.com/hhvmonaarch64-bud17-400k1-170320163554/95/hhvm-on-aarch64-bud17400k1-36-638.jpg?cb=1490027817)
of https://www.slideshare.net/linaroorg/hhvm-on-aarch64-bud17400k1:
"LLVM? Have you heard of it?" "Why don't you just use LLVM?" "We tried it:
a) No noticeable performance gains; b) LLVM's MCJIT is too heavyweight".

(No comparison of HHIR and PseudoC, HHIR is pretty much adhoc IR for HHVM
grounded in its PHP nature. The point is, oftentimes it's easier to use
something else, even if adhoc, than a bloated pseudo-standard like LLIR).

QBE IL
------

http://c9x.me/compile/doc/il.html

I watched QBE project for a while, but only recently figured that its
intermediate language is well documented.

Creton IL
---------

* https://cretonne.readthedocs.io/en/latest/langref.html
* https://cretonne.readthedocs.io/en/latest/compare-llvm.html

Didn't exist when ScratchABlock was started. Uses an interesting syntactic
sugar for Phi functions: instead of having them explicitly, it has "basic
block parameters", in a way very similar to function parameters, and
every jump specifies actual values for these "parameters".

C--
---

http://www.cs.tufts.edu/~nr/c--/
http://www.cs.tufts.edu/~nr/c--/extern/man2.pdf

Unlike many entries in this list with comments like "wasn't known to me
before ScratchABlock was started" or "didn't exist before ScratchABlock
was started", C-- was (remotely) known to me for a long-long time. Actually,
I heard about it yet when there was no Interwebs and the program exchange
was happening via floppy disks, i.e. at the end of 20th century, which,
checking the C-- timeline, was soon after C-- was initially appeared
(1997). Given this, I guess it's fair to say that C-- was a meta-mental
model of ScratchABlock IR, and ScratchABlock IR is the closest to C--.

C-- has different aims and purpose though, for example it supports garbage
collection interface, exception handling, etc. Overall, featureset and
usecases for C-- and ScratchABlock definitely overlap, but are different.

Miasm IR
--------

https://github.com/cea-sec/miasm

Miasm has its [own IR](https://github.com/cea-sec/miasm#intermediate-representation).

FalconRE IR
-----------

https://github.com/falconre/falcon

Just as everyone else, FalconRE has its [own IR](https://docs.rs/falcon/0.3.1/falcon/il/index.html),
at least this time "with strong influences from RREIL and Binary Ninja's LLIL".

This [blog post](http://reversing.io/posts/the-il-nop/) has insightful
comments about some other PRs:

> I have experienced the, “Joys,” of VEX IR in Angr’s pyvex, and
> the forever popular LLVM IR.

> With Falcon, I wanted to design a simple, expression-based IL. I originally
> arrived at five Operation types:
>  * Assign { dst: Scalar,       src: Expression }
>  * Store  { index: Expression, src: Expression }
>  * Load   { dst: Scalar,       src: Expression }
>  * Branch { target: Expression }
>  * Raise  { expr: Expression }

PseudoC doesn't even try to specifically distinguish loads and stores - for
it, they are assignments just the same. Of course, if for some analysis
they're useful, they can be easily separated: loads are just assignments
with memory reference on RHS, store - on LHS.

> ILs by readability
>
> Binary Ninja is the first IL I know of which made it a point to have a
> readable IL. If you haven’t spent a lot of time looking at ILs for
> reverse-engineering, the experience is typically like reading a computer
> program written by your friend’s nephew who is having trouble with their
> Introduction to Java course,  and is pretty sure their program to find the
> greatest number in an array is complete, but they’re having some trouble
> and here’s 300 lines of code and I guess they don’t teach whitespace
> anymore and all_the_variablesLookLike_THIS. It can be annoying.
>
> RREIL is not readable. VEX IR is not readable.

D'oh. Nuff said. I couldn't say better, and actually, I didn't, but quoted
Keith Cooper and Linda Torczon in ScratchABlock README instead.

> Falcon encodes intra-procedural direct branches, including conditional
> intra-procedural direct branches, implicitly as optionally guarded edges
> in the ControlFlowGraph.

Well, of course. In ScratchABlock, original instructions remain after
parsing, but most transformations start with removing them using
the `remove_trailing_jumps` pass.

> I ended up replacing the Raise operation with the much more verbose,
> and battle-ready, Intrinsic operation.

In PseudoC, "Intrinsic" is called "special function".

> If-Then-Else, or Ite Expression
> I originally left the Ite expression out of Falcon IL very consciously.
> After a while, I relented, and now Falcon has an Ite expression.

ScratchABlock/PseudoC approaches this problem differently, given that its
original usage is decompilation in the first place. So, besides "basic"
PseudoC form, there're also "lifted" forms of PseudoC with consecutively
higher and higher level control flow structures (like If-Then-Else). Granted,
there's [currently] no parser for such a form, but nonetheless it exists
in the CFG representation and can be processed and/or dumped.

References
----------
* http://indefinitestudies.org/2009/04/03/a-quick-survey-on-intermediate-representations-for-program-analysis/
* [angr FAQ: Why did you choose VEX instead of another IR (such as LLVM, REIL, BAP, etc)?](https://docs.angr.io/docs/faq.html#why-did-you-choose-vex-instead-of-another-ir-such-as-llvm-reil-bap-etc)
* [FalconRE: The IL Nop](http://reversing.io/posts/the-il-nop/)
