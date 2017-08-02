// Graph props:
//  name: None
//  trailing_jumps: True

// Predecessors: []
// BBlock props:
//  state_out: {$r0=0x10000010, $r1=*(u32*)0x10000020}
10:
$r0 = 0x10000010
$r1 = ((my_struct*)0x10000000)->field2
return
Exits: []
