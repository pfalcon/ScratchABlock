// Graph props:
//  addr: 10
//  name: 10
//  trailing_jumps: True

// Predecessors: ['20']
10:
Exits: [(None, '11'), (COND(EXPR(==[$a1, 0])), '20')]

// Predecessors: ['10']
11:
$a2 = 1
Exits: [(None, '20')]

// Predecessors: ['10', '11']
20:
Exits: [(None, '10')]
