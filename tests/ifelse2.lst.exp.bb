// Graph props:
//  name: None
//  trailing_jumps: True

// Predecessors: []
05:
$a4 = 100
Exits: [(None, '05.if')]

// Predecessors: ['05']
05.if:
if ($a1 != 0) {
  $a2 = 1
} else {
  $a2 = 2
}
Exits: [(None, '40')]

// Predecessors: ['05.if']
40:
$a3 = 0
Exits: []
