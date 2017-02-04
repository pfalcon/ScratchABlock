// Predecessors: []
05:
$a4 = 100
Exits: [(None, '05.if')]

// Predecessors: ['05']
05.if:
if ($a1 == 1) {
  $a2 = 1
} else if ($a1 == 2) {
  $a2 = 2
} else {
  $a2 = 3
}
Exits: [(None, '40')]

// Predecessors: ['05.if']
40:
$a3 = 0
Exits: []
