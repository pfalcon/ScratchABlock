// Graph props:
//  addr: 40
//  name: 40
//  trailing_jumps: True

// Predecessors: []
// Node props:
//  reachdef_gen: {(REG(a), '10'), (REG(b), '10')}
//  reachdef_in: {(REG(a), None), (REG(b), None), (REG(c), None), (REG(d), None)}
//  reachdef_kill: {(REG(a), '10'), (REG(a), None), (REG(b), '10'), (REG(b), None)}
//  reachdef_out: {(REG(a), '10'), (REG(b), '10'), (REG(c), None), (REG(d), None)}
10:
/*10*/ $a = [VALUE(0x1)] # {'uses': ['20', '30', '40']}
/*20*/ $b = [REG(a)] # {'uses': []}
/*25*/ if([COND(REG(r0) == VALUE(0x5)), ADDR(40)])
Exits: [(COND(REG(r0) == VALUE(0x5)), '40'), (None, '30')]

// Predecessors: ['10']
// Node props:
//  reachdef_gen: {(REG(c), '30')}
//  reachdef_in: {(REG(a), '10'), (REG(b), '10'), (REG(c), None), (REG(d), None)}
//  reachdef_kill: {(REG(c), '30'), (REG(c), None)}
//  reachdef_out: {(REG(a), '10'), (REG(b), '10'), (REG(c), '30'), (REG(d), None)}
30:
/*30*/ $c = [EXPR(+[REG(a), VALUE(0x1)])] # {'uses': ['40']}
Exits: [(None, '40')]

// Predecessors: ['10', '30']
// Node props:
//  reachdef_gen: {(REG(d), '40')}
//  reachdef_in: {(REG(a), '10'), (REG(b), '10'), (REG(c), '30'), (REG(c), None), (REG(d), None)}
//  reachdef_kill: {(REG(d), '40'), (REG(d), None)}
//  reachdef_out: {(REG(a), '10'), (REG(b), '10'), (REG(c), '30'), (REG(c), None), (REG(d), '40')}
40:
/*40*/ $d = [EXPR(+[REG(c), REG(a)])] # {'uses': []}
Exits: []
