// Graph props:
//  addr: 15
//  estimated_params: {$a2}
//  modifieds: {$a3, $save}
//  name: func
//  preserveds: {$a2}
//  reach_exit: {$a2, $a3, $save}
//  trailing_jumps: True

// Predecessors: []
// Node props:
//  live_gen: {$a2_0}
//  live_in: {$a2_0}
//  live_kill: {$a2, $a3, $save}
//  live_out: set()
//  reachdef_gen: {($a2, '15'), ($a3, '15'), ($save, '15')}
//  reachdef_in: {($a2, None), ($a3, None), ($save, None)}
//  reachdef_kill: {($a2, '15'), ($a2, None), ($a3, '15'), ($a3, None), ($save, '15'), ($save, None)}
//  reachdef_out: {($a2, '15'), ($a3, '15'), ($save, '15')}
// BBlock props:
//  state_out: {$a2=$a2_0, $a3=$a2_0 + 1, $save=$a2_0}
15:
$a2 = $a2_0
$save = $a2_0
$a3 = $a2_0 + 1
$a2 = 10
$a2 = $a2_0
return
Exits: []
