// Graph props:
//  name: None
//  trailing_jumps: True

// Predecessors: []
05:
$a2 = 1
Exits: [(None, '10')]

// Predecessors: ['05', '10.critn']
10:
Exits: [(None, '10.critn')]

// Predecessors: ['10']
10.critn:
$a3 = 1
if ($a1) goto 10
Exits: [(COND($a1), '10'), (None, '80')]

// Predecessors: ['10.critn']
80:
return
Exits: []
