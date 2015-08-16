// Predecessors: ['30_1']
10:
Exits: [(SCond($a1 != 0), '30'), (None, '20')]

// Predecessors: ['10']
20:
$a2 = 1
Exits: [(None, '30_1')]

// Predecessors: ['10']
30:
$a2 = 2
Exits: [(None, '30_1')]

// Predecessors: ['20', '30']
30_1:
Exits: [(None, '10')]
