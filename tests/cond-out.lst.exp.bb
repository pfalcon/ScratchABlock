// Graph props:
//  name: None
//  trailing_jumps: True

// Predecessors: []
// Node props:
//  reachdef_gen: set()
//  reachdef_in: {($a1, None)}
//  reachdef_kill: set()
//  reachdef_out: {($a1, None)}
10:
if ($a0 < 5) goto 30
Exits: [(COND(EXPR(<[$a0, 5])), '30'), (None, '20')]

// Predecessors: ['10']
// Node props:
//  reachdef_gen: {($a1, '20')}
//  reachdef_in: {($a1, None)}
//  reachdef_kill: {($a1, '20'), ($a1, None)}
//  reachdef_out: {($a1, '20')}
// BBlock props:
//  cond_in: {COND(EXPR(>=[$a0, 5]))}
//  cond_out: {COND(EXPR(>=[$a0, 5]))}
20:
$a1 = 3
Exits: [(None, '30')]

// Predecessors: ['10', '20']
// Node props:
//  reachdef_gen: set()
//  reachdef_in: {($a1, '20'), ($a1, None)}
//  reachdef_kill: set()
//  reachdef_out: {($a1, '20'), ($a1, None)}
30:
return
Exits: []
