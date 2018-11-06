// Graph props:
//  name: None
//  trailing_jumps: True

// Predecessors: []
// Node props:
//  dfsno: 5
//  dom_front: set()
//  idom: None
0A:
if ($r0) goto 0C
Exits: [(COND($r0), '0C'), (None, '0B')]

// Predecessors: ['0A']
// Node props:
//  dfsno: 4
//  dom_front: {'0D'}
//  idom: 0A
0B:
goto 0D
Exits: [(None, '0D')]

// Predecessors: ['0A', '0E']
// Node props:
//  dfsno: 3
//  dom_front: {'0C', '0D'}
//  idom: 0A
0C:
if ($r1) goto 0E
Exits: [(COND($r1), '0E'), (None, '0D')]

// Predecessors: ['0B', '0C']
// Node props:
//  dfsno: 2
//  dom_front: set()
//  idom: 0A
0D:
return
Exits: []

// Predecessors: ['0C']
// Node props:
//  dfsno: 1
//  dom_front: {'0C'}
//  idom: 0C
0E:
goto 0C
Exits: [(None, '0C')]
