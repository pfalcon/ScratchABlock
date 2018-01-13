// Graph props:
//  name: None
//  trailing_jumps: True

// Predecessors: []
10:
$a2 = (u8)$a2
$a2 = (u16)$a2
$a2 = (u32)$a2
$a2 &= 0x1ff
$a2 = bitfield($a2, /*lsb*/1, /*sz*/8)
$a2 &= 0xffffff
$a3 = $a2 & 0x3
return
Exits: []
