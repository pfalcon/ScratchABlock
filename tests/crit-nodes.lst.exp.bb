// Graph props:
//  name: None
//  trailing_jumps: True

// Predecessors: []
10:
if ($a1) goto 30
Exits: [(COND($a1), '30'), (None, '20')]

// Predecessors: ['10']
20:
$a2 = 1
Exits: [(None, '30')]

// Predecessors: ['10', '20']
30:
Exits: [(None, '30.critn')]

// Predecessors: ['30']
30.critn:
if ($a3) goto 50
Exits: [(COND($a3), '50'), (None, '40')]

// Predecessors: ['30.critn']
40:
$a4 = 2
Exits: [(None, '50')]

// Predecessors: ['30.critn', '40']
50:
Exits: [(None, '50.critn')]

// Predecessors: ['50']
50.critn:
if ($a3) goto 70
Exits: [(COND($a3), '70'), (None, '65')]

// Predecessors: ['50.critn']
65:
$a4 = 3
Exits: [(None, '70')]

// Predecessors: ['50.critn', '65']
70:
return
Exits: []
