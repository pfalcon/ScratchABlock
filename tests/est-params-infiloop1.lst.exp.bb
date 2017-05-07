// Graph props:
//  addr: 10
//  estimated_params: {$r1}
//  name: start
//  trailing_jumps: True

// Predecessors: []
// Node props:
//  live_gen: set()
//  live_in: {$r1}
//  live_kill: set()
//  live_out: {$r1}
10:
if 0x0 goto single_exit
goto 10.real
Exits: [(0x0, 'single_exit'), (None, '10.real')]

// Predecessors: ['10']
// Node props:
//  live_gen: set()
//  live_in: {$r1}
//  live_kill: {$r0}
//  live_out: {$r1}
10.real:
$r0 = 1
Exits: [(None, '20')]

// Predecessors: ['10.real', '20']
// Node props:
//  live_gen: {$r1}
//  live_in: {$r1}
//  live_kill: set()
//  live_out: {$r1}
20:
func($r1)
goto 20
Exits: [(None, '20')]

// Predecessors: ['10']
// Node props:
//  live_gen: set()
//  live_in: set()
//  live_kill: set()
//  live_out: set()
single_exit:
return
Exits: []
