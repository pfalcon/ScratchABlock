// Graph props:
//  addr: 10
//  estimated_params: {$a2}
//  modifieds: {$a2, $a3}
//  name: func
//  preserveds: set()
//  reach_exit: {$a2, $a3}
//  trailing_jumps: True

// Predecessors: []
// Node props:
//  live_gen: set()
//  live_in: {$a2_0}
//  live_kill: set()
//  live_out: {$a2_0}
//  reachdef_gen: {($a2, '0entry')}
//  reachdef_in: {($a2, None), ($a3, None)}
//  reachdef_kill: {($a2, '0entry'), ($a2, '10'), ($a2, None)}
//  reachdef_out: {($a2, '0entry'), ($a3, None)}
// BBlock props:
//  state_out: {$a2=$a2_0}
0entry:
// $a2 = $a2_0 (dead)
Exits: [(None, '10')]

// Predecessors: ['0entry']
// Node props:
//  live_gen: {$a2_0}
//  live_in: {$a2_0}
//  live_kill: {$a2, $a3}
//  live_out: {$a2, $a3}
//  reachdef_gen: {($a2, '10'), ($a3, '10')}
//  reachdef_in: {($a2, '0entry'), ($a3, None)}
//  reachdef_kill: {($a2, '0entry'), ($a2, '10'), ($a2, None), ($a3, '10'), ($a3, None)}
//  reachdef_out: {($a2, '10'), ($a3, '10')}
// BBlock props:
//  state_in: {$a2=$a2_0}
//  state_out: {$a2=10, $a3=$a2_0 + 1}
10:
$a3 = $a2_0 + 1
$a2 = 10
return
Exits: [(None, '_EXIT_')]

// Predecessors: ['10']
// Node props:
//  live_gen: set()
//  live_in: {$a2, $a3}
//  live_kill: set()
//  live_out: {$a2, $a3}
//  reachdef_gen: set()
//  reachdef_in: {($a2, '10'), ($a3, '10')}
//  reachdef_kill: set()
//  reachdef_out: {($a2, '10'), ($a3, '10')}
// BBlock props:
//  state_in: {$a2=10, $a3=$a2_0 + 1}
//  state_out: {$a2=10, $a3=$a2_0 + 1}
_EXIT_:
return
Exits: []
