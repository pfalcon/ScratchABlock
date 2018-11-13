// Graph props:
//  name: None
//  trailing_jumps: True

// Predecessors: []
// Node props:
//  idom: None
//  postno: 9
//  sdom: set()
0:
nop()
Exits: [(None, '1')]

// Predecessors: ['0', '3']
// Node props:
//  idom: 0
//  postno: 8
//  sdom: {'0'}
1:
if ($r0) goto 5
Exits: [(COND($r0), '5'), (None, '2')]

// Predecessors: ['1']
// Node props:
//  idom: 1
//  postno: 7
//  sdom: {'0', '1'}
2:
nop()
Exits: [(None, '3')]

// Predecessors: ['2', '7']
// Node props:
//  idom: 1
//  postno: 2
//  sdom: {'0', '1'}
3:
if ($r1) goto 1
Exits: [(COND($r1), '1'), (None, '4')]

// Predecessors: ['3']
// Node props:
//  idom: 3
//  postno: 1
//  sdom: {'0', '1', '3'}
4:
return
Exits: []

// Predecessors: ['1']
// Node props:
//  idom: 1
//  postno: 6
//  sdom: {'0', '1'}
5:
if ($r2) goto 8
Exits: [(COND($r2), '8'), (None, '6')]

// Predecessors: ['5']
// Node props:
//  idom: 5
//  postno: 5
//  sdom: {'0', '1', '5'}
6:
nop()
Exits: [(None, '7')]

// Predecessors: ['6', '8']
// Node props:
//  idom: 5
//  postno: 3
//  sdom: {'0', '1', '5'}
7:
if ($r3) goto 3
Exits: [(COND($r3), '3'), (None, '8')]

// Predecessors: ['5', '7']
// Node props:
//  idom: 5
//  postno: 4
//  sdom: {'0', '1', '5'}
8:
goto 7
Exits: [(None, '7')]
