// Predecessors: []
// Node props:
//  reachdef_gen: {($a0, '10'), ($sp, '10')}
//  reachdef_in: {($a0, None), ($sp, None)}
//  reachdef_kill: {($a0, '10'), ($a0, None), ($sp, '10'), ($sp, None)}
//  reachdef_out: {($a0, '10'), ($sp, '10')}
// BBlock props:
//  state_out: {$a0=*(u32*)($sp0 - 0x10) $sp=$sp0 - 0x10 + 0x10}
10:
$sp = $sp0
$sp = $sp0 - 0x10
loc16_u32 = $a0
$a0 = 5
$a0 = loc16_u32
$sp = $sp0 - 0x10 + 0x10
return
Exits: []
