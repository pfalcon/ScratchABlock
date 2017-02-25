// Predecessors: []
// BBlock props:
//  state_out: {$a0=100}
05:
$a0 = 100
if ($a1 == 100) goto 20
Exits: [(COND($a1 == 100), '20'), (None, '11')]

// Predecessors: ['05']
// BBlock props:
//  state_out: {$a2=1}
11:
$a2 = 1
Exits: [(None, '20')]

// Predecessors: ['05', '11']
// BBlock props:
//  state_out: {$a3=3}
20:
$a3 = 3
Exits: []
