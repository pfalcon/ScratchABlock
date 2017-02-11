// Predecessors: []
// Node props:
//  reachdef_gen: {(REG(a), '10'), (REG(b), '10'), (REG(c), '10'), (REG(d), '10'), (REG(e), '10')}
//  reachdef_in: {(REG(a), None), (REG(b), None), (REG(c), None), (REG(d), None), (REG(e), None)}
//  reachdef_kill: {(REG(a), '10'), (REG(a), None), (REG(b), '10'), (REG(b), None), (REG(c), '10'), (REG(c), None), (REG(d), '10'), (REG(d), None), (REG(e), '10'), (REG(e), None)}
//  reachdef_out: {(REG(a), '10'), (REG(b), '10'), (REG(c), '10'), (REG(d), '10'), (REG(e), '10')}
10:
/*10*/ $a = [VALUE(0x1)] # {'uses': ['20', '30', '40', '50', '60']}
/*20*/ $b = [REG(a)] # {'uses': []}
/*30*/ $c = [EXPR(+[REG(a), VALUE(0x1)])] # {'uses': ['40']}
/*40*/ $d = [EXPR(+[REG(c), REG(a)])] # {'uses': []}
/*50*/ $e = [*(u32*)REG(a)] # {'uses': []}
/*60*/ *(u32*)(EXPR(+[REG(a), VALUE(0x2)])) = [VALUE(0x5)] # {'uses': []}
Exits: []
