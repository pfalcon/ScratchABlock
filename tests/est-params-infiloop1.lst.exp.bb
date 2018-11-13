// Graph props:
//  addr: 10
//  estimated_params: {$r1}
//  name: start
//  noreturn: True
//  trailing_jumps: True

// Predecessors: []
// Node props:
//  live_gen: set()
//  live_in: {$r1}
//  live_kill: set()
//  live_out: {$r1}
//  postno: 3
//  postno_exit: None
.ENTRY:
Exits: [(None, '10')]

// Predecessors: ['.ENTRY']
// Node props:
//  live_gen: set()
//  live_in: {$r1}
//  live_kill: {$r0}
//  live_out: {$r1}
//  postno: 2
//  postno_exit: None
10:
$r0 = 1
Exits: [(None, '20')]

// Predecessors: ['10', '20']
// Node props:
//  live_gen: {$r1}
//  live_in: {$r1}
//  live_kill: set()
//  live_out: {$r1}
//  postno: 1
//  postno_exit: None
20:
func($r1)
goto 20
Exits: [(0, '_DEADEND_'), (None, '20')]

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
//  live_gen: set()
//  live_in: set()
//  live_kill: set()
//  live_out: set()
//  postno: None
//  postno_exit: 1
_EXIT_:
return
Exits: []
