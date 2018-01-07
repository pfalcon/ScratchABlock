// Graph props:
//  name: None
//  trailing_jumps: True

// Predecessors: []
// BBlock props:
//  state_out: {$a1=0xfff, $a2=*(u32*)data_0x20F000 & 0xfff}
10:
$a1 = 0xfff
$a2 = data_0x20F000
$a2 = *(u32*)data_0x20F000 & 0xfff
if ((*(u32*)data_0x20F000 & 0xfff) == 0) goto 15
Exits: [(COND(EXPR(==[EXPR(&[*(u32*)ADDR(data_0x20F000), 0xfff]), 0])), '15'), (None, '14')]

// Predecessors: ['10']
// BBlock props:
//  state_out: {$a3=data_0x20F004, *(u32*)data_0x20F004=0}
14:
$a3 = data_0x20F004
*(u32*)data_0x20F004 = 0
Exits: [(None, '15')]

// Predecessors: ['10', '14']
// BBlock props:
//  state_out: {}
15:
return
Exits: []
