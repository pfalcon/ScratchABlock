// Graph props:
//  addr: 10
//  estimated_params: {$r1}
//  name: start
//  noreturn: True
//  trailing_jumps: True

// Predecessors: []
// Node props:
//  dfsno: 3
//  dfsno_exit: None
//  live_gen: set()
//  live_in: {$r1}
//  live_kill: set()
//  live_out: {$r1}
0entry:
Exits: [(None, '10')]

// Predecessors: ['0entry']
// Node props:
//  dfsno: 2
//  dfsno_exit: None
//  live_gen: set()
//  live_in: {$r1}
//  live_kill: {$r0}
//  live_out: {$r1}
10:
$r0 = 1
Exits: [(None, '20')]

// Predecessors: ['10', '20']
// Node props:
//  dfsno: 1
//  dfsno_exit: None
//  live_gen: {$r1}
//  live_in: {$r1}
//  live_kill: set()
//  live_out: {$r1}
20:
func($r1)
goto 20
Exits: [(None, '20'), (0, '_DEADEND_')]

// Predecessors: ['20']
// Node props:
//  live_gen: set()
//  live_in: set()
//  live_kill: set()
//  live_out: set()
_DEADEND_:
Exits: [(0, '_EXIT_')]

// Predecessors: ['_DEADEND_']
// Node props:
//  dfsno: None
//  dfsno_exit: 1
//  live_gen: set()
//  live_in: set()
//  live_kill: set()
//  live_out: set()
_EXIT_:
return
Exits: []
