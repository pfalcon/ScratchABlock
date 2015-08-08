// Predecessors: []
00:
Exits: [(SCond($a1 == 0), '20'), (None, '30')]

// Predecessors: ['00']
20:
$a2 = 0x1
Exits: [(None, '30')]

// Predecessors: ['00', '20']
30:
$a3 = 0x5
Exits: []
