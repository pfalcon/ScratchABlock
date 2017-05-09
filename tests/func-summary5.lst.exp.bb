// Graph props:
//  addr: 11
//  estimated_params: {$a2, $a4, $a5, $a6, $a7}
//  modifieds: {$a0, $a3, $a4, $a5, $a6, $a7, $a8, $a9, $a10, $a11}
//  name: func
//  preserveds: {$a2, $sp}
//  reach_exit: {$a0, $a2, $a3, $a4, $a5, $a6, $a7, $a8, $a9, $a10, $a11, $sp}
//  trailing_jumps: True

// Predecessors: []
// Node props:
//  live_gen: {$a2_0, $a4_0, $a5_0, $a6_0, $a7_0, $sp_0}
//  live_in: {$a2_0, $a4_0, $a5_0, $a6_0, $a7_0, $sp_0}
//  live_kill: {$a2, $a3, $a4, $a5, $a6, $a7, $loc_16_u32, $sp}
//  live_out: {$a2, $a2_0, $a3, $a4, $a5, $a6, $a7, $sp_0}
//  reachdef_gen: {($a0, '11'), ($a2, '11'), ($a3, '11'), ($a4, '11'), ($a5, '11'), ($a6, '11'), ($a7, '11'), ($a8, '11'), ($a9, '11'), ($a10, '11'), ($a11, '11'), ($loc_16_u32, '11'), ($sp, '11')}
//  reachdef_in: {($a0, None), ($a2, None), ($a3, None), ($a4, None), ($a5, None), ($a6, None), ($a7, None), ($a8, None), ($a9, None), ($a10, None), ($a11, None), ($loc_16_u32, None), ($sp, None)}
//  reachdef_kill: {($a0, '11'), ($a0, '35'), ($a0, None), ($a2, '11'), ($a2, '35'), ($a2, '45'), ($a2, None), ($a3, '11'), ($a3, '35'), ($a3, None), ($a4, '11'), ($a4, '35'), ($a4, None), ($a5, '11'), ($a5, '35'), ($a5, None), ($a6, '11'), ($a6, '35'), ($a6, None), ($a7, '11'), ($a7, '35'), ($a7, None), ($a8, '11'), ($a8, '35'), ($a8, None), ($a9, '11'), ($a9, '35'), ($a9, None), ($a10, '11'), ($a10, '35'), ($a10, None), ($a11, '11'), ($a11, '35'), ($a11, None), ($loc_16_u32, '11'), ($loc_16_u32, None), ($sp, '11'), ($sp, '45'), ($sp, None)}
//  reachdef_out: {($a0, '11'), ($a2, '11'), ($a3, '11'), ($a4, '11'), ($a5, '11'), ($a6, '11'), ($a7, '11'), ($a8, '11'), ($a9, '11'), ($a10, '11'), ($a11, '11'), ($loc_16_u32, '11'), ($sp, '11')}
// BBlock props:
//  state_out: {$loc_16_u32=$a2_0, $sp=$sp_0 - 0x10}
11:
$a2 = $a2_0
$a4 = $a4_0
$a5 = $a5_0
$a6 = $a6_0
$a7 = $a7_0
$sp = $sp_0
$sp = $sp_0 - 0x10
$loc_16_u32 = $a2_0
$a3 = $a2_0 + 1
$a2 = 10
call foo
Exits: [(None, '35')]

// Predecessors: ['11']
// Node props:
//  live_gen: {$a2, $a3, $a4, $a5, $a6, $a7}
//  live_in: {$a2, $a2_0, $a3, $a4, $a5, $a6, $a7, $sp_0}
//  live_kill: {$a2}
//  live_out: {$a2_0, $sp_0}
//  reachdef_gen: {($a0, '35'), ($a2, '35'), ($a3, '35'), ($a4, '35'), ($a5, '35'), ($a6, '35'), ($a7, '35'), ($a8, '35'), ($a9, '35'), ($a10, '35'), ($a11, '35')}
//  reachdef_in: {($a0, '11'), ($a2, '11'), ($a3, '11'), ($a4, '11'), ($a5, '11'), ($a6, '11'), ($a7, '11'), ($a8, '11'), ($a9, '11'), ($a10, '11'), ($a11, '11'), ($loc_16_u32, '11'), ($sp, '11')}
//  reachdef_kill: {($a0, '11'), ($a0, '35'), ($a0, None), ($a2, '11'), ($a2, '35'), ($a2, '45'), ($a2, None), ($a3, '11'), ($a3, '35'), ($a3, None), ($a4, '11'), ($a4, '35'), ($a4, None), ($a5, '11'), ($a5, '35'), ($a5, None), ($a6, '11'), ($a6, '35'), ($a6, None), ($a7, '11'), ($a7, '35'), ($a7, None), ($a8, '11'), ($a8, '35'), ($a8, None), ($a9, '11'), ($a9, '35'), ($a9, None), ($a10, '11'), ($a10, '35'), ($a10, None), ($a11, '11'), ($a11, '35'), ($a11, None)}
//  reachdef_out: {($a0, '35'), ($a2, '35'), ($a3, '35'), ($a4, '35'), ($a5, '35'), ($a6, '35'), ($a7, '35'), ($a8, '35'), ($a9, '35'), ($a10, '35'), ($a11, '35'), ($loc_16_u32, '11'), ($sp, '11')}
// BBlock props:
//  state_in: {$loc_16_u32=$a2_0, $sp=$sp_0 - 0x10}
//  state_out: {$loc_16_u32=$a2_0, $sp=$sp_0 - 0x10}
35:
$a2 += 1
call bar
Exits: [(None, '45')]

// Predecessors: ['35']
// Node props:
//  live_gen: {$a2_0, $sp_0}
//  live_in: {$a2_0, $sp_0}
//  live_kill: {$a2, $sp}
//  live_out: set()
//  reachdef_gen: {($a2, '45'), ($sp, '45')}
//  reachdef_in: {($a0, '35'), ($a2, '35'), ($a3, '35'), ($a4, '35'), ($a5, '35'), ($a6, '35'), ($a7, '35'), ($a8, '35'), ($a9, '35'), ($a10, '35'), ($a11, '35'), ($loc_16_u32, '11'), ($sp, '11')}
//  reachdef_kill: {($a2, '11'), ($a2, '35'), ($a2, '45'), ($a2, None), ($sp, '11'), ($sp, '45'), ($sp, None)}
//  reachdef_out: {($a0, '35'), ($a2, '45'), ($a3, '35'), ($a4, '35'), ($a5, '35'), ($a6, '35'), ($a7, '35'), ($a8, '35'), ($a9, '35'), ($a10, '35'), ($a11, '35'), ($loc_16_u32, '11'), ($sp, '45')}
// BBlock props:
//  state_in: {$loc_16_u32=$a2_0, $sp=$sp_0 - 0x10}
//  state_out: {$a2=$a2_0, $loc_16_u32=$a2_0, $sp=$sp_0}
45:
$a2 = $a2_0
$sp = $sp_0
return
Exits: []
