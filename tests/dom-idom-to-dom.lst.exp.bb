// Graph props:
//  name: None
//  trailing_jumps: True

// Predecessors: []
// Node props:
//  dom: {'0'}
//  idom: None
//  postno: 9
0:
nop()
Exits: [(None, '1')]

// Predecessors: ['0', '3']
// Node props:
//  dom: {'0', '1'}
//  idom: 0
//  postno: 8
1:
if ($r0) goto 5
Exits: [(COND($r0), '5'), (None, '2')]

// Predecessors: ['1']
// Node props:
//  dom: {'0', '1', '2'}
//  idom: 1
//  postno: 7
2:
nop()
Exits: [(None, '3')]

// Predecessors: ['2', '7']
// Node props:
//  dom: {'0', '1', '3'}
//  idom: 1
//  postno: 2
3:
if ($r1) goto 1
Exits: [(COND($r1), '1'), (None, '4')]

// Predecessors: ['3']
// Node props:
//  dom: {'0', '1', '3', '4'}
//  idom: 3
//  postno: 1
4:
return
Exits: []

// Predecessors: ['1']
// Node props:
//  dom: {'0', '1', '5'}
//  idom: 1
//  postno: 6
5:
if ($r2) goto 8
Exits: [(COND($r2), '8'), (None, '6')]

// Predecessors: ['5']
// Node props:
//  dom: {'0', '1', '5', '6'}
//  idom: 5
//  postno: 5
6:
nop()
Exits: [(None, '7')]

// Predecessors: ['6', '8']
// Node props:
//  dom: {'0', '1', '5', '7'}
//  idom: 5
//  postno: 3
7:
if ($r3) goto 3
Exits: [(COND($r3), '3'), (None, '8')]

// Predecessors: ['5', '7']
// Node props:
//  dom: {'0', '1', '5', '8'}
//  idom: 5
//  postno: 4
8:
goto 7
Exits: [(None, '7')]
