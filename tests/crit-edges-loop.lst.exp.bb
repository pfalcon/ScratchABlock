// Graph props:
//  name: None
//  trailing_jumps: True

// Predecessors: []
05:
$a2 = 1
Exits: [(None, '10')]

// Predecessors: ['05', '10.crite']
10:
$a3 = 1
if ($a1) goto 10
Exits: [(COND($a1), '10.crite'), (None, '80')]

// Predecessors: ['10']
10.crite:
Exits: [(None, '10')]

// Predecessors: ['10']
80:
return
Exits: []
