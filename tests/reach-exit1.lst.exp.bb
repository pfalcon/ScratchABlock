// Graph props:
//  addr: 30
//  name: 30
//  reach_exit: {$a2, $a3, $a4}
//  trailing_jumps: True

// Predecessors: []
// Node props:
//  reachdef_gen: set()
//  reachdef_in: {($a2, None), ($a3, None), ($a4, None)}
//  reachdef_kill: set()
//  reachdef_out: {($a2, None), ($a3, None), ($a4, None)}
10:
if ($a1 == 0) goto 30
Exits: [(COND($a1 == 0), '30'), (None, '20')]

// Predecessors: ['10']
// Node props:
//  reachdef_gen: {($a2, '20')}
//  reachdef_in: {($a2, None), ($a3, None), ($a4, None)}
//  reachdef_kill: {($a2, '20'), ($a2, None)}
//  reachdef_out: {($a2, '20'), ($a3, None), ($a4, None)}
20:
$a2 = 1
goto 40
Exits: [(None, '40')]

// Predecessors: ['10']
// Node props:
//  reachdef_gen: {($a3, '30')}
//  reachdef_in: {($a2, None), ($a3, None), ($a4, None)}
//  reachdef_kill: {($a3, '30'), ($a3, None)}
//  reachdef_out: {($a2, None), ($a3, '30'), ($a4, None)}
30:
$a3 = 2
Exits: [(None, '40')]

// Predecessors: ['20', '30']
// Node props:
//  reachdef_gen: {($a4, '40')}
//  reachdef_in: {($a2, '20'), ($a2, None), ($a3, '30'), ($a3, None), ($a4, None)}
//  reachdef_kill: {($a4, '40'), ($a4, None)}
//  reachdef_out: {($a2, '20'), ($a2, None), ($a3, '30'), ($a3, None), ($a4, '40')}
40:
$a4 = 0
return
Exits: []
