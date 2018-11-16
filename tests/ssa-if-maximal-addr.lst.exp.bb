// Graph props:
//  local_defines: {$a1, $a2}
//  name: None
//  trailing_jumps: True

// Predecessors: []
// Node props:
//  postno: 3
10:
if ($a0_0 + 1) goto 30
Exits: [(COND(EXPR(+[$a0_0, 1])), '30'), (None, '20')]

// Predecessors: ['10']
// Node props:
//  postno: 2
20:
$a1_20 = 2
Exits: [(None, '30')]

// Predecessors: ['10', '20']
// Node props:
//  postno: 1
30:
$a1_30_phi = phi($a1_0, $a1_20)
$a2_30_phi = phi($a2_0, $a2_0)
$a2_30 = 3
$a2_35 = 4
return
Exits: []
