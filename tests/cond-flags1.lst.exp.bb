// Graph props:
//  name: None
//  trailing_jumps: True

// Predecessors: []
// Node props:
//  live_gen: {$eax, $ebx}
//  live_in: {$eax, $ebx}
//  live_kill: {$C, $Z}
//  live_out: set()
// BBlock props:
//  state_out: {$C=$eax < $ebx, $Z=$eax == $ebx}
10:
// $Z = $eax == $ebx (dead)
// $C = $eax < $ebx (dead)
if ($eax == $ebx) goto 40
Exits: [(COND(EXPR(==[$eax, $ebx])), '40'), (None, '30')]

// Predecessors: ['10']
// Node props:
//  live_gen: set()
//  live_in: set()
//  live_kill: {$ecx}
//  live_out: set()
// BBlock props:
//  state_out: {$ecx=1}
30:
// $ecx = 1 (dead)
Exits: [(None, '40')]

// Predecessors: ['10', '30']
// Node props:
//  live_gen: set()
//  live_in: set()
//  live_kill: set()
//  live_out: set()
// BBlock props:
//  state_out: {}
40:
return
Exits: []
