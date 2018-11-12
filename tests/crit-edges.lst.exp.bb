// Graph props:
//  name: None
//  trailing_jumps: True

// Predecessors: []
10:
if ($a1) goto 30
Exits: [(COND($a1), '10.crite'), (None, '20')]

// Predecessors: ['10']
10.crite:
Exits: [(None, '30')]

// Predecessors: ['10']
20:
$a2 = 1
Exits: [(None, '30')]

// Predecessors: ['10.crite', '20']
30:
if ($a3) goto 50
Exits: [(COND($a3), '30.crite'), (None, '40')]

// Predecessors: ['30']
30.crite:
Exits: [(None, '50')]

// Predecessors: ['30']
40:
$a4 = 2
Exits: [(None, '50')]

// Predecessors: ['30.crite', '40']
50:
if ($a3) goto 70
Exits: [(COND($a3), '50.crite'), (None, '65')]

// Predecessors: ['50']
50.crite:
Exits: [(None, '70')]

// Predecessors: ['50']
65:
$a4 = 3
Exits: [(None, '70')]

// Predecessors: ['50.crite', '65']
70:
return
Exits: []
