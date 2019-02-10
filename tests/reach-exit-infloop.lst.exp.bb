// Graph props:
//  has_infloops: True
//  name: None
//  reach_exit: {$a2, $a4}
//  trailing_jumps: True

// Predecessors: []
// Node props:
//  postno: 5
//  postno_exit: 1
//  reachdef_gen: set()
//  reachdef_in: {($a2, None), ($a3, None), ($a4, None)}
//  reachdef_kill: set()
//  reachdef_out: {($a2, None), ($a3, None), ($a4, None)}
10:
if ($a1 == 0) goto 30
Exits: [(COND(EXPR(==[$a1, 0])), '30'), (None, '20')]

// Predecessors: ['10']
// Node props:
//  postno: 4
//  postno_exit: 2
//  reachdef_gen: {($a2, '20')}
//  reachdef_in: {($a2, None), ($a3, None), ($a4, None)}
//  reachdef_kill: {($a2, '20'), ($a2, None)}
//  reachdef_out: {($a2, '20'), ($a3, None), ($a4, None)}
20:
$a2 = 1
goto 40
Exits: [(None, '40')]

// Predecessors: ['10', '30']
// Node props:
//  postno: 1
//  postno_exit: None
//  reachdef_gen: {($a3, '30')}
//  reachdef_in: {($a2, None), ($a3, '30'), ($a3, None), ($a4, None)}
//  reachdef_kill: {($a3, '30'), ($a3, None)}
//  reachdef_out: {($a2, None), ($a3, '30'), ($a4, None)}
30:
$a3 = 2
goto 30
Exits: [(0, '_DEADEND_'), (None, '30')]

// Predecessors: ['20']
// Node props:
//  postno: 3
//  postno_exit: 3
//  reachdef_gen: {($a4, '40')}
//  reachdef_in: {($a2, '20'), ($a3, None), ($a4, None)}
//  reachdef_kill: {($a4, '40'), ($a4, None)}
//  reachdef_out: {($a2, '20'), ($a3, None), ($a4, '40')}
40:
$a4 = 0
return
Exits: [(None, '_EXIT_')]

// Predecessors: ['30']
// Node props:
//  reachdef_gen: set()
//  reachdef_in: set()
//  reachdef_kill: set()
//  reachdef_out: set()
_DEADEND_:
Exits: [(0, '_EXIT_')]

// Predecessors: ['40', '_DEADEND_']
// Node props:
//  postno: 2
//  postno_exit: 4
//  reachdef_gen: set()
//  reachdef_in: {($a2, '20'), ($a3, None), ($a4, '40')}
//  reachdef_kill: set()
//  reachdef_out: {($a2, '20'), ($a3, None), ($a4, '40')}
_EXIT_:
return
Exits: []
