// Graph props:
//  addr: 20
//  name: 20
//  trailing_jumps: True

// Predecessors: []
// BBlock props:
//  state_out: {$a1=$a2 - 5}
05:
$a1 = $a2 - 5
if ($a2 == 5) goto 20
Exits: [(COND($a2 == 5), '20'), (None, '11')]

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
