// Graph props:
//  addr: 01
//  estimated_params: {$a2}
//  modifieds: {$a3}
//  name: func
//  preserveds: {$a2, $sp}
//  reach_exit: {$a2, $a3, $sp}
//  trailing_jumps: True

// Predecessors: []
// Node props:
//  live_gen: {$a2_0, $sp_0}
//  live_in: {$a2_0, $sp_0}
//  live_kill: {$a2, $a3, $loc_16_u32, $sp}
//  live_out: set()
//  reachdef_gen: {($a2, '01'), ($a3, '01'), ($loc_16_u32, '01'), ($sp, '01')}
//  reachdef_in: {($a2, None), ($a3, None), ($loc_16_u32, None), ($sp, None)}
//  reachdef_kill: {($a2, '01'), ($a2, None), ($a3, '01'), ($a3, None), ($loc_16_u32, '01'), ($loc_16_u32, None), ($sp, '01'), ($sp, None)}
//  reachdef_out: {($a2, '01'), ($a3, '01'), ($loc_16_u32, '01'), ($sp, '01')}
// BBlock props:
//  state_out: {$a2=$a2_0, $a3=$a2_0 + 1, $loc_16_u32=$a2_0, $sp=$sp_0}
01:
$a2 = $a2_0
$sp = $sp_0
$sp = $sp_0 - 0x10
$loc_16_u32 = $a2_0
$a3 = $a2_0 + 1
$a2 = 10
$a2 = $a2_0
$sp = $sp_0
return
Exits: []
