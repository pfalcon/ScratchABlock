// Graph props:
//  name: None
//  trailing_jumps: True

// Predecessors: []
// BBlock props:
//  state_out: {$a1=abs($a0), $a2=abs($a0) + 3, $a5=$a4 + 1}
10:
$a1 = abs($a0)
$a2 = abs($a0) + 3
$a4 = side_effect($a3)
$a5 = $a4 + 1
Exits: []
