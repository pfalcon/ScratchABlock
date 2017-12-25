// Graph props:
//  name: None
//  trailing_jumps: True

// Predecessors: []
10:
if ($a1 != 0) goto 20
Exits: [(COND(EXPR(!=[$a1, 0])), '20'), (None, '11')]

// Predecessors: ['10']
11:
return
Exits: [(None, '_EXIT_')]

// Predecessors: ['10']
20:
if ($a1 != 1) goto 30
Exits: [(COND(EXPR(!=[$a1, 1])), '30'), (None, '22')]

// Predecessors: ['20']
22:
return
Exits: [(None, '_EXIT_')]

// Predecessors: ['20']
30:
return
Exits: [(None, '_EXIT_')]

// Predecessors: ['11', '22', '30']
_EXIT_:
return
Exits: []
