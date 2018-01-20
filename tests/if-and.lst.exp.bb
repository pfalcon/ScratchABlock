// Graph props:
//  name: None
//  trailing_jumps: True

// Predecessors: []
10:
$a1 = 1
if ($a2 == 0 || $a3 != 0) goto 50
Exits: [(COND(EXPR(||[EXPR(==[$a2, 0]), EXPR(!=[$a3, 0])])), '50'), (None, '40')]

// Predecessors: ['10']
40:
$a4 = 4
Exits: [(None, '50')]

// Predecessors: ['10', '40']
50:
$a2 = 2
Exits: []
