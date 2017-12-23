// Graph props:
//  name: None
//  trailing_jumps: True

// Predecessors: []
// Node props:
//  live_gen: set()
//  live_in: set()
//  live_kill: {$a}
//  live_out: set()
10:
// $a = 1 (dead)
$a = 2
$a += 1
return $a
Exits: []
