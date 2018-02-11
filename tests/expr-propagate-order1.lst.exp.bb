// Graph props:
//  addr: 10
//  name: func1
//  trailing_jumps: True

// Predecessors: []
// Node props:
//  live_gen: set()
//  live_in: {$a2, $a3}
//  live_kill: set()
//  live_out: {$a2, $a3}
//  reachdef_gen: {($a2, '.ENTRY'), ($a3, '.ENTRY')}
//  reachdef_in: {($a2, None), ($a3, None), ($a4, None), ($a13, None)}
//  reachdef_kill: {($a2, '30'), ($a2, '.ENTRY'), ($a2, None), ($a3, '.ENTRY'), ($a3, None)}
//  reachdef_out: {($a2, '.ENTRY'), ($a3, '.ENTRY'), ($a4, None), ($a13, None)}
// BBlock props:
//  state_out: {$a2=$a2_0, $a3=$a3_0}
.ENTRY:
$a2 = $a2_0
$a3 = $a3_0
Exits: [(None, '10')]

// Predecessors: ['.ENTRY']
// Node props:
//  live_gen: {$a2, $a3}
//  live_in: {$a2, $a3}
//  live_kill: {$a13}
//  live_out: {$a13}
//  reachdef_gen: {($a13, '10')}
//  reachdef_in: {($a2, '.ENTRY'), ($a3, '.ENTRY'), ($a4, None), ($a13, None)}
//  reachdef_kill: {($a13, '10'), ($a13, None)}
//  reachdef_out: {($a2, '.ENTRY'), ($a3, '.ENTRY'), ($a4, None), ($a13, '10')}
// BBlock props:
//  state_in: {$a2=$a2_0, $a3=$a3_0}
//  state_out: {$a2=$a2_0, $a3=$a3_0, $a13=$a2_0 + 0x100}
10:
$a13 = $a2_0 + 0x100
if ($a3_0 != 0) goto 40
Exits: [(COND(EXPR(!=[$a3_0, 0])), '40'), (None, '30')]

// Predecessors: ['10']
// Node props:
//  live_gen: set()
//  live_in: {$a13}
//  live_kill: {$a2}
//  live_out: {$a13}
//  reachdef_gen: {($a2, '30')}
//  reachdef_in: {($a2, '.ENTRY'), ($a3, '.ENTRY'), ($a4, None), ($a13, '10')}
//  reachdef_kill: {($a2, '30'), ($a2, '.ENTRY'), ($a2, None)}
//  reachdef_out: {($a2, '30'), ($a3, '.ENTRY'), ($a4, None), ($a13, '10')}
// BBlock props:
//  state_in: {$a2=$a2_0, $a3=$a3_0, $a13=$a2_0 + 0x100}
//  state_out: {$a2=0x1, $a3=$a3_0, $a13=$a2_0 + 0x100}
30:
$a2 = 0x1
Exits: [(None, '40')]

// Predecessors: ['10', '30']
// Node props:
//  live_gen: {$a13}
//  live_in: {$a13}
//  live_kill: {$a4}
//  live_out: set()
//  reachdef_gen: {($a4, '40')}
//  reachdef_in: {($a2, '30'), ($a2, '.ENTRY'), ($a3, '.ENTRY'), ($a4, None), ($a13, '10')}
//  reachdef_kill: {($a4, '40'), ($a4, None)}
//  reachdef_out: {($a2, '30'), ($a2, '.ENTRY'), ($a3, '.ENTRY'), ($a4, '40'), ($a13, '10')}
// BBlock props:
//  state_in: {$a3=$a3_0, $a13=$a2_0 + 0x100}
//  state_out: {$a3=$a3_0, $a4=*(u32*)($a2_0 + 0x100), $a13=$a2_0 + 0x100}
40:
$a4 = *(u32*)($a2_0 + 0x100)
if (0x10 < *(u32*)($a2_0 + 0x100)) goto 70
Exits: [(COND(EXPR(<[0x10, *(u32*)EXPR(+[$a2_0, 0x100])])), '70')]

// Predecessors: ['40']
// Node props:
//  live_gen: set()
//  live_in: set()
//  live_kill: set()
//  live_out: set()
//  reachdef_gen: set()
//  reachdef_in: {($a2, '30'), ($a2, '.ENTRY'), ($a3, '.ENTRY'), ($a4, '40'), ($a13, '10')}
//  reachdef_kill: set()
//  reachdef_out: {($a2, '30'), ($a2, '.ENTRY'), ($a3, '.ENTRY'), ($a4, '40'), ($a13, '10')}
// BBlock props:
//  state_in: {$a3=$a3_0, $a4=*(u32*)($a2_0 + 0x100), $a13=$a2_0 + 0x100}
//  state_out: {$a3=$a3_0, $a4=*(u32*)($a2_0 + 0x100), $a13=$a2_0 + 0x100}
70:
return
Exits: [(None, '_EXIT_')]

// Predecessors: ['70']
// Node props:
//  live_gen: set()
//  live_in: set()
//  live_kill: set()
//  live_out: set()
//  reachdef_gen: set()
//  reachdef_in: {($a2, '30'), ($a2, '.ENTRY'), ($a3, '.ENTRY'), ($a4, '40'), ($a13, '10')}
//  reachdef_kill: set()
//  reachdef_out: {($a2, '30'), ($a2, '.ENTRY'), ($a3, '.ENTRY'), ($a4, '40'), ($a13, '10')}
// BBlock props:
//  state_in: {$a3=$a3_0, $a4=*(u32*)($a2_0 + 0x100), $a13=$a2_0 + 0x100}
//  state_out: {$a3=$a3_0, $a4=*(u32*)($a2_0 + 0x100), $a13=$a2_0 + 0x100}
_EXIT_:
return
Exits: []
