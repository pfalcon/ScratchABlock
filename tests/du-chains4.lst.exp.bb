// Graph props:
//  name: None
//  trailing_jumps: True

// Predecessors: []
// Node props:
//  reachdef_gen: {(REG(a), '10'), (REG(b), '10'), (REG(c), '10'), (REG(d), '10')}
//  reachdef_in: {(REG(a), None), (REG(b), None), (REG(c), None), (REG(d), None)}
//  reachdef_kill: {(REG(a), '10'), (REG(a), None), (REG(b), '10'), (REG(b), None), (REG(c), '10'), (REG(c), None), (REG(d), '10'), (REG(d), None)}
//  reachdef_out: {(REG(a), '10'), (REG(b), '10'), (REG(c), '10'), (REG(d), '10')}
10:
/*10*/ $a = [VALUE(0x1)] # {'uses': ['20', '30', '40']}
/*20*/ $b = [REG(a)] # {'uses': []}
/*30*/ $c = [EXPR(+[REG(a), VALUE(0x1)])] # {'uses': ['40']}
/*40*/ $d = [EXPR(+[REG(c), REG(a)])] # {'uses': []}
/*50*/ $a = [VALUE(0x2)] # {'uses': ['60', '70', '80']}
/*60*/ $b = [REG(a)] # {'uses': []}
/*70*/ $c = [EXPR(+[REG(a), VALUE(0x2)])] # {'uses': ['80']}
/*80*/ $d = [EXPR(+[REG(c), REG(a)])] # {'uses': []}
Exits: []
