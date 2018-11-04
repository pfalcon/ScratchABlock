// Graph props:
//  name: None
//  trailing_jumps: True

// Predecessors: []
// Node props:
//  dfsno: 9
//  dom: {'0'}
//  idom: None
0:
nop()
Exits: [(None, '1')]

// Predecessors: ['0', '3']
// Node props:
//  dfsno: 8
//  dom: {'0', '1'}
//  idom: 0
1:
if ($r0) goto 5
Exits: [(COND($r0), '5'), (None, '2')]

// Predecessors: ['1']
// Node props:
//  dfsno: 7
//  dom: {'0', '1', '2'}
//  idom: 1
2:
nop()
Exits: [(None, '3')]

// Predecessors: ['2', '7']
// Node props:
//  dfsno: 2
//  dom: {'0', '1', '3'}
//  idom: 1
3:
if ($r1) goto 1
Exits: [(COND($r1), '1'), (None, '4')]

// Predecessors: ['3']
// Node props:
//  dfsno: 1
//  dom: {'0', '1', '3', '4'}
//  idom: 3
4:
return
Exits: []

// Predecessors: ['1']
// Node props:
//  dfsno: 6
//  dom: {'0', '1', '5'}
//  idom: 1
5:
if ($r2) goto 8
Exits: [(COND($r2), '8'), (None, '6')]

// Predecessors: ['5']
// Node props:
//  dfsno: 5
//  dom: {'0', '1', '5', '6'}
//  idom: 5
6:
nop()
Exits: [(None, '7')]

// Predecessors: ['6', '8']
// Node props:
//  dfsno: 3
//  dom: {'0', '1', '5', '7'}
//  idom: 5
7:
if ($r3) goto 3
Exits: [(COND($r3), '3'), (None, '8')]

// Predecessors: ['5', '7']
// Node props:
//  dfsno: 4
//  dom: {'0', '1', '5', '8'}
//  idom: 5
8:
goto 7
Exits: [(None, '7')]
