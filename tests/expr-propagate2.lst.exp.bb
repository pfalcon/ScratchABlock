// Graph props:
//  name: None
//  trailing_jumps: True

// Predecessors: []
10:
$a1 = 0xfff
$a2 = data_0x20F000
(u32)$a2 = *(u32*)$a2 & $a1
if ($a2 == 0) goto 15
Exits: [(COND(EXPR(==[$a2, 0])), '15'), (None, '14')]

// Predecessors: ['10']
14:
$a3 = data_0x20F004
*(u32*)$a3 = 0
Exits: [(None, '15')]

// Predecessors: ['10', '14']
15:
return
Exits: []
