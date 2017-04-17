// Graph props:
//  name: None
//  trailing_jumps: True

// Predecessors: []
// BBlock props:
//  state_out: {$ebp=$esp0 - 4, $edx=*(u32*)($esp0 + 4), $esp=$esp0 - 24, $tmp1=$esp0 - 16, *(u32*)($esp0 - 12)=$ebx, *(u32*)($esp0 - 16)=$ecx, *(u32*)($esp0 - 8)=$esi}
0:
$esp = $esp0
$esp = $esp0 - 4
*(u32*)($esp0 - 4) = $ebp
$ebp = $esp0 - 4
$esp = $esp0 - 8
*(u32*)($esp0 - 8) = $esi
$esp = $esp0 - 12
*(u32*)($esp0 - 12) = $ebx
$esp = $esp0 - 16
*(u32*)($esp0 - 16) = $ecx
$tmp1 = $esp0 - 16
$esp = $esp0 - 24
$edx = *(u32*)($esp0 + 4)
Exits: []
