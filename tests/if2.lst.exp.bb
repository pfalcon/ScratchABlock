// Predecessors: []
05:
$a4 = 100
Exits: [(None, '05.if')]

// Predecessors: ['05']
05.if:
if ($a1 != 0) {
  $a2 = 1
}
Exits: [(None, '20')]

// Predecessors: ['05.if']
20:
$a3 = 3
Exits: []
