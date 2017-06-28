// Graph props:
//  addr: 20
//  name: 20
//  trailing_jumps: True

// Predecessors: []
10:
if ($a1 > 5) goto 20
Exits: [(COND($a1 > 5), '20'), (None, '11')]

// Predecessors: ['10']
11:
$a2 = 1
Exits: [(None, '20')]

// Predecessors: ['10', '11']
20:
$a3 = 3
Exits: []
