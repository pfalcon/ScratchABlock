// Graph props:
//  addr: 10
//  name: 10
//  trailing_jumps: True

// Predecessors: []
// Node props:
//  reachdef_gen: {($a0, '10'), ($a2, '10'), ($sp, '10')}
//  reachdef_in: {($a0, None), ($a2, None), ($sp, None)}
//  reachdef_kill: {($a0, '10'), ($a0, '40'), ($a0, None), ($a2, '10'), ($a2, None), ($sp, '10'), ($sp, '40'), ($sp, None)}
//  reachdef_out: {($a0, '10'), ($a2, '10'), ($sp, '10')}
// BBlock props:
//  state_out: {$a0=5, $a2=*(u32*)($sp_0 - 0x10), $sp=$sp_0 - 0x10, *(u8*)*(u32*)($sp_0 - 0x10)=10}
10:
$sp = $sp_0
$sp = $sp_0 - 0x10
loc16_u32 = $a0
$a0 = 5
$a2 = loc16_u32
*(u8*)loc16_u32 = 10
if (*(u8*)loc16_u32 == 11) goto 40
Exits: [(COND(EXPR(==[*(u8*)CVAR(loc16_u32), 11])), '40')]

// Predecessors: ['10']
// Node props:
//  reachdef_gen: {($a0, '40'), ($sp, '40')}
//  reachdef_in: {($a0, '10'), ($a2, '10'), ($sp, '10')}
//  reachdef_kill: {($a0, '10'), ($a0, '40'), ($a0, None), ($sp, '10'), ($sp, '40'), ($sp, None)}
//  reachdef_out: {($a0, '40'), ($a2, '10'), ($sp, '40')}
// BBlock props:
//  state_in: {$a0=5, $a2=*(u32*)($sp_0 - 0x10), $sp=$sp_0 - 0x10}
//  state_out: {$a0=*(u32*)($sp_0 - 0x10), $a2=*(u32*)($sp_0 - 0x10), $sp=$sp_0 - 0x10 + 0x10}
40:
$a0 = loc16_u32
$sp = $sp_0 - 0x10 + 0x10
return
Exits: []
