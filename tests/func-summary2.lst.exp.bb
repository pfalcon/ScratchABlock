// Graph props:
//  addr: 10
//  estimated_args: {$a2}
//  modifieds: {$a2, $a3}
//  name: func
//  preserveds: set()
//  reach_exit: {$a2, $a3}
//  trailing_jumps: True

// Predecessors: []
// Node props:
//  live_gen: {$a2_0}
//  live_in: {$a2_0}
//  live_kill: {$a2, $a3}
//  live_out: set()
//  reachdef_gen: {($a2, '10'), ($a3, '10')}
//  reachdef_in: {($a2, None), ($a3, None)}
//  reachdef_kill: {($a2, '10'), ($a2, None), ($a3, '10'), ($a3, None)}
//  reachdef_out: {($a2, '10'), ($a3, '10')}
// BBlock props:
//  state_out: {$a2=10, $a3=$a2_0 + 1}
10:
$a2 = $a2_0
$a3 = $a2_0 + 1
$a2 = 10
return
Exits: []
