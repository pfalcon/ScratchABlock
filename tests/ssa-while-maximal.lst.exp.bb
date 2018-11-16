// Graph props:
//  local_defines: {$x, $y}
//  name: None
//  trailing_jumps: True

// Predecessors: []
// Node props:
//  postno: 3
10:
if ($x_0 >= 100) goto 50
Exits: [(COND(EXPR(>=[$x_0, 100])), '50'), (None, '20')]

// Predecessors: ['10', '20']
// Node props:
//  postno: 2
20:
$x_1 = phi($x_0, $x_2)
$y_1 = phi($y_0, $y_2)
$x_2 = $x_1 + 1
$y_2 = $y_1 + $x_2
if ($x_2 < 100) goto 20
Exits: [(COND(EXPR(<[$x_2, 100])), '20'), (None, '50')]

// Predecessors: ['10', '20']
// Node props:
//  postno: 1
50:
$x_3 = phi($x_0, $x_2)
$y_3 = phi($y_0, $y_2)
return
Exits: []
