// Graph props:
//  addr: 10
//  name: repeat
//  trailing_jumps: True

// Predecessors: []
10:
do {
  $a2 = 1
} while ($a1 != 0);
Exits: [(None, '40')]

// Predecessors: ['10']
40:
return
Exits: []
