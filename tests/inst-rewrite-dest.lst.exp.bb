// Graph props:
//  name: None
//  trailing_jumps: True

// Predecessors: []
10:
$r0 = 0
$r0 = 1
$r0 = 2
$ecx = ($ecx & 0xffff0000) | (3 & 0xffff)
$ecx = ($ecx & 0xffffff00) | (4 & 0xff)
$ecx = ($ecx & 0xffff00ff) | ((5 << 8) & 0xff00)
$r0 = ($r0 & 0x7fffffff) | ((1 << 31) & 0x80000000)
return
Exits: []
