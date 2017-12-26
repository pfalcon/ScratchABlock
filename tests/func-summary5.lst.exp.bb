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
//  live_gen: {$a4_0, $a5_0, $a6_0, $a7_0}
//  live_in: {$a2_0, $a4_0, $a5_0, $a6_0, $a7_0}
//  live_kill: {$a4, $a5, $a6, $a7}
//  live_out: {$a2_0, $a4, $a5, $a6, $a7}
//  reachdef_gen: {($a2, '.ENTRY'), ($a4, '.ENTRY'), ($a5, '.ENTRY'), ($a6, '.ENTRY'), ($a7, '.ENTRY'), ($sp, '.ENTRY')}
//  reachdef_in: {($a0, None), ($a2, None), ($a3, None), ($a4, None), ($a5, None), ($a6, None), ($a7, None), ($a8, None), ($a9, None), ($a10, None), ($a11, None), ($loc_16_u32, None), ($sp, None)}
//  reachdef_kill: {($a2, '11'), ($a2, '35'), ($a2, '45'), ($a2, '.ENTRY'), ($a2, None), ($a4, '11'), ($a4, '35'), ($a4, '.ENTRY'), ($a4, None), ($a5, '11'), ($a5, '35'), ($a5, '.ENTRY'), ($a5, None), ($a6, '11'), ($a6, '35'), ($a6, '.ENTRY'), ($a6, None), ($a7, '11'), ($a7, '35'), ($a7, '.ENTRY'), ($a7, None), ($sp, '11'), ($sp, '45'), ($sp, '.ENTRY'), ($sp, None)}
//  reachdef_out: {($a0, None), ($a2, '.ENTRY'), ($a3, None), ($a4, '.ENTRY'), ($a5, '.ENTRY'), ($a6, '.ENTRY'), ($a7, '.ENTRY'), ($a8, None), ($a9, None), ($a10, None), ($a11, None), ($loc_16_u32, None), ($sp, '.ENTRY')}
// BBlock props:
//  state_out: {$a2=$a2_0, $a4=$a4_0, $a5=$a5_0, $a6=$a6_0, $a7=$a7_0, $sp=$sp_0}
.ENTRY:
// $a2 = $a2_0 (dead)
$a4 = $a4_0
$a5 = $a5_0
$a6 = $a6_0
$a7 = $a7_0
// $sp = $sp_0 (dead)
Exits: [(None, '11')]

// Predecessors: ['.ENTRY']
// Node props:
//  live_gen: {$a2_0, $a4, $a5, $a6, $a7}
//  live_in: {$a2_0, $a4, $a5, $a6, $a7}
//  live_kill: {$a0, $a2, $a3, $a4, $a5, $a6, $a7, $a8, $a9, $a10, $a11}
//  live_out: {$a2, $a3, $a4, $a5, $a6, $a7}
//  reachdef_gen: {($a0, '11'), ($a2, '11'), ($a3, '11'), ($a4, '11'), ($a5, '11'), ($a6, '11'), ($a7, '11'), ($a8, '11'), ($a9, '11'), ($a10, '11'), ($a11, '11'), ($loc_16_u32, '11'), ($sp, '11')}
//  reachdef_in: {($a0, None), ($a2, '.ENTRY'), ($a3, None), ($a4, '.ENTRY'), ($a5, '.ENTRY'), ($a6, '.ENTRY'), ($a7, '.ENTRY'), ($a8, None), ($a9, None), ($a10, None), ($a11, None), ($loc_16_u32, None), ($sp, '.ENTRY')}
//  reachdef_kill: {($a0, '11'), ($a0, '35'), ($a0, None), ($a2, '11'), ($a2, '35'), ($a2, '45'), ($a2, '.ENTRY'), ($a2, None), ($a3, '11'), ($a3, '35'), ($a3, None), ($a4, '11'), ($a4, '35'), ($a4, '.ENTRY'), ($a4, None), ($a5, '11'), ($a5, '35'), ($a5, '.ENTRY'), ($a5, None), ($a6, '11'), ($a6, '35'), ($a6, '.ENTRY'), ($a6, None), ($a7, '11'), ($a7, '35'), ($a7, '.ENTRY'), ($a7, None), ($a8, '11'), ($a8, '35'), ($a8, None), ($a9, '11'), ($a9, '35'), ($a9, None), ($a10, '11'), ($a10, '35'), ($a10, None), ($a11, '11'), ($a11, '35'), ($a11, None), ($loc_16_u32, '11'), ($loc_16_u32, None), ($sp, '11'), ($sp, '45'), ($sp, '.ENTRY'), ($sp, None)}
//  reachdef_out: {($a0, '11'), ($a2, '11'), ($a3, '11'), ($a4, '11'), ($a5, '11'), ($a6, '11'), ($a7, '11'), ($a8, '11'), ($a9, '11'), ($a10, '11'), ($a11, '11'), ($loc_16_u32, '11'), ($sp, '11')}
// BBlock props:
//  state_in: {$a2=$a2_0, $a4=$a4_0, $a5=$a5_0, $a6=$a6_0, $a7=$a7_0, $sp=$sp_0}
//  state_out: {$loc_16_u32=$a2_0, $sp=$sp_0 - 0x10}
11:
// $sp = $sp_0 - 0x10 (dead)
// $loc_16_u32 = $a2_0 (dead)
$a3 = $a2_0 + 1
$a2 = 10
call foo // {'defs': [$a0, $a2, $a3, $a4, $a5, $a6, $a7, $a8, $a9, $a10, $a11], 'uses': [$a2, $a3, $a4, $a5, $a6, $a7]}
Exits: [(None, '35')]

// Predecessors: ['11']
// Node props:
//  live_gen: {$a2, $a3, $a4, $a5, $a6, $a7}
//  live_in: {$a2, $a3, $a4, $a5, $a6, $a7}
//  live_kill: {$a0, $a2, $a3, $a4, $a5, $a6, $a7, $a8, $a9, $a10, $a11}
//  live_out: {$a0, $a3, $a4, $a5, $a6, $a7, $a8, $a9, $a10, $a11}
//  reachdef_gen: {($a0, '35'), ($a2, '35'), ($a3, '35'), ($a4, '35'), ($a5, '35'), ($a6, '35'), ($a7, '35'), ($a8, '35'), ($a9, '35'), ($a10, '35'), ($a11, '35')}
//  reachdef_in: {($a0, '11'), ($a2, '11'), ($a3, '11'), ($a4, '11'), ($a5, '11'), ($a6, '11'), ($a7, '11'), ($a8, '11'), ($a9, '11'), ($a10, '11'), ($a11, '11'), ($loc_16_u32, '11'), ($sp, '11')}
//  reachdef_kill: {($a0, '11'), ($a0, '35'), ($a0, None), ($a2, '11'), ($a2, '35'), ($a2, '45'), ($a2, '.ENTRY'), ($a2, None), ($a3, '11'), ($a3, '35'), ($a3, None), ($a4, '11'), ($a4, '35'), ($a4, '.ENTRY'), ($a4, None), ($a5, '11'), ($a5, '35'), ($a5, '.ENTRY'), ($a5, None), ($a6, '11'), ($a6, '35'), ($a6, '.ENTRY'), ($a6, None), ($a7, '11'), ($a7, '35'), ($a7, '.ENTRY'), ($a7, None), ($a8, '11'), ($a8, '35'), ($a8, None), ($a9, '11'), ($a9, '35'), ($a9, None), ($a10, '11'), ($a10, '35'), ($a10, None), ($a11, '11'), ($a11, '35'), ($a11, None)}
//  reachdef_out: {($a0, '35'), ($a2, '35'), ($a3, '35'), ($a4, '35'), ($a5, '35'), ($a6, '35'), ($a7, '35'), ($a8, '35'), ($a9, '35'), ($a10, '35'), ($a11, '35'), ($loc_16_u32, '11'), ($sp, '11')}
// BBlock props:
//  state_in: {$loc_16_u32=$a2_0, $sp=$sp_0 - 0x10}
//  state_out: {$loc_16_u32=$a2_0, $sp=$sp_0 - 0x10}
35:
$a2 += 1
call bar // {'defs': [$a0, $a2, $a3, $a4, $a5, $a6, $a7, $a8, $a9, $a10, $a11], 'uses': [$a2, $a3, $a4, $a5, $a6, $a7]}
Exits: [(None, '45')]

// Predecessors: ['35']
// Node props:
//  live_gen: set()
//  live_in: {$a0, $a3, $a4, $a5, $a6, $a7, $a8, $a9, $a10, $a11}
//  live_kill: set()
//  live_out: {$a0, $a3, $a4, $a5, $a6, $a7, $a8, $a9, $a10, $a11}
//  reachdef_gen: {($a2, '45'), ($sp, '45')}
//  reachdef_in: {($a0, '35'), ($a2, '35'), ($a3, '35'), ($a4, '35'), ($a5, '35'), ($a6, '35'), ($a7, '35'), ($a8, '35'), ($a9, '35'), ($a10, '35'), ($a11, '35'), ($loc_16_u32, '11'), ($sp, '11')}
//  reachdef_kill: {($a2, '11'), ($a2, '35'), ($a2, '45'), ($a2, '.ENTRY'), ($a2, None), ($sp, '11'), ($sp, '45'), ($sp, '.ENTRY'), ($sp, None)}
//  reachdef_out: {($a0, '35'), ($a2, '45'), ($a3, '35'), ($a4, '35'), ($a5, '35'), ($a6, '35'), ($a7, '35'), ($a8, '35'), ($a9, '35'), ($a10, '35'), ($a11, '35'), ($loc_16_u32, '11'), ($sp, '45')}
// BBlock props:
//  state_in: {$loc_16_u32=$a2_0, $sp=$sp_0 - 0x10}
//  state_out: {$a2=$a2_0, $loc_16_u32=$a2_0, $sp=$sp_0}
45:
// $a2 = $a2_0 (dead)
// $sp = $sp_0 (dead)
return
Exits: [(None, '_EXIT_')]

// Predecessors: ['45']
// Node props:
//  live_gen: set()
//  live_in: {$a0, $a3, $a4, $a5, $a6, $a7, $a8, $a9, $a10, $a11}
//  live_kill: set()
//  live_out: {$a0, $a3, $a4, $a5, $a6, $a7, $a8, $a9, $a10, $a11}
//  reachdef_gen: set()
//  reachdef_in: {($a0, '35'), ($a2, '45'), ($a3, '35'), ($a4, '35'), ($a5, '35'), ($a6, '35'), ($a7, '35'), ($a8, '35'), ($a9, '35'), ($a10, '35'), ($a11, '35'), ($loc_16_u32, '11'), ($sp, '45')}
//  reachdef_kill: set()
//  reachdef_out: {($a0, '35'), ($a2, '45'), ($a3, '35'), ($a4, '35'), ($a5, '35'), ($a6, '35'), ($a7, '35'), ($a8, '35'), ($a9, '35'), ($a10, '35'), ($a11, '35'), ($loc_16_u32, '11'), ($sp, '45')}
// BBlock props:
//  state_in: {$a2=$a2_0, $loc_16_u32=$a2_0, $sp=$sp_0}
//  state_out: {$a2=$a2_0, $loc_16_u32=$a2_0, $sp=$sp_0}
_EXIT_:
return
Exits: []
