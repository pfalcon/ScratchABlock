// Graph props:
//  addr: 11
//  estimated_params: {$a2}
//  modifieds: {$a3}
//  name: func
//  preserveds: {$a2, $sp}
//  reach_exit: {$a2, $a3, $sp}
//  trailing_jumps: True

// Predecessors: []
// Node props:
//  live_gen: set()
//  live_in: {$a2_0}
//  live_kill: set()
//  live_out: {$a2_0}
//  reachdef_gen: {($a2, '0entry'), ($sp, '0entry')}
//  reachdef_in: {($a2, None), ($a3, None), ($loc_16_u32, None), ($sp, None)}
//  reachdef_kill: {($a2, '0entry'), ($a2, '11'), ($a2, None), ($sp, '0entry'), ($sp, '11'), ($sp, None)}
//  reachdef_out: {($a2, '0entry'), ($a3, None), ($loc_16_u32, None), ($sp, '0entry')}
// BBlock props:
//  state_out: {$a2=$a2_0, $sp=$sp_0}
0entry:
// $a2 = $a2_0 (dead)
// $sp = $sp_0 (dead)
Exits: [(None, '11')]

// Predecessors: ['0entry']
// Node props:
//  live_gen: {$a2_0}
//  live_in: {$a2_0}
//  live_kill: {$a3}
//  live_out: {$a3}
//  reachdef_gen: {($a2, '11'), ($a3, '11'), ($loc_16_u32, '11'), ($sp, '11')}
//  reachdef_in: {($a2, '0entry'), ($a3, None), ($loc_16_u32, None), ($sp, '0entry')}
//  reachdef_kill: {($a2, '0entry'), ($a2, '11'), ($a2, None), ($a3, '11'), ($a3, None), ($loc_16_u32, '11'), ($loc_16_u32, None), ($sp, '0entry'), ($sp, '11'), ($sp, None)}
//  reachdef_out: {($a2, '11'), ($a3, '11'), ($loc_16_u32, '11'), ($sp, '11')}
// BBlock props:
//  state_in: {$a2=$a2_0, $sp=$sp_0}
//  state_out: {$a2=$a2_0, $a3=$a2_0 + 1, $loc_16_u32=$a2_0, $sp=$sp_0}
11:
// $sp = $sp_0 - 0x10 (dead)
// $loc_16_u32 = $a2_0 (dead)
$a3 = $a2_0 + 1
// $a2 = 10 (dead)
// $a2 = $a2_0 (dead)
// $sp = $sp_0 (dead)
return
Exits: [(None, '_EXIT_')]

// Predecessors: ['11']
// Node props:
//  live_gen: set()
//  live_in: {$a3}
//  live_kill: set()
//  live_out: {$a3}
//  reachdef_gen: set()
//  reachdef_in: {($a2, '11'), ($a3, '11'), ($loc_16_u32, '11'), ($sp, '11')}
//  reachdef_kill: set()
//  reachdef_out: {($a2, '11'), ($a3, '11'), ($loc_16_u32, '11'), ($sp, '11')}
// BBlock props:
//  state_in: {$a2=$a2_0, $a3=$a2_0 + 1, $loc_16_u32=$a2_0, $sp=$sp_0}
//  state_out: {$a2=$a2_0, $a3=$a2_0 + 1, $loc_16_u32=$a2_0, $sp=$sp_0}
_EXIT_:
return
Exits: []
