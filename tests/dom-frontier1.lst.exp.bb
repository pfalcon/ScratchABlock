// Graph props:
//  name: None
//  trailing_jumps: True

// Predecessors: []
// Node props:
//  dom_front: set()
//  idom: None
//  postno: 5
0A:
if ($r0) goto 0C
Exits: [(COND($r0), '0C'), (None, '0B')]

// Predecessors: ['0A']
// Node props:
//  dom_front: {'0D'}
//  idom: 0A
//  postno: 4
0B:
goto 0D
Exits: [(None, '0D')]

// Predecessors: ['0A', '0E']
// Node props:
//  dom_front: {'0C', '0D'}
//  idom: 0A
//  postno: 3
0C:
if ($r1) goto 0E
Exits: [(COND($r1), '0E'), (None, '0D')]

// Predecessors: ['0B', '0C']
// Node props:
//  dom_front: set()
//  idom: 0A
//  postno: 2
0D:
return
Exits: []

// Predecessors: ['0C']
// Node props:
//  dom_front: {'0C'}
//  idom: 0C
//  postno: 1
0E:
goto 0C
Exits: [(None, '0C')]
