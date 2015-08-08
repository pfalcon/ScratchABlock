// Predecessors: []
10:
/* && */
Exits: [(CCond(($a2 == 0) || ($a3 != 0)), '50'), (None, '40')]

// Predecessors: ['10']
40:
$a4 = 0x4
Exits: [(None, '50')]

// Predecessors: ['10', '40']
50:
$a2 = 0x2
Exits: []
