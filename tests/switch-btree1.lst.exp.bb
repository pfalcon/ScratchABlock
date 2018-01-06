// Graph props:
//  name: None
//  trailing_jumps: True

// Predecessors: []
10:
$a1 = 0
if ($a2 > 700) goto 21
Exits: [(COND(EXPR(>[$a2, 700])), '21'), (None, '12')]

// Predecessors: ['10']
12:
if ($a2 == 700) goto 35
Exits: [(COND(EXPR(==[$a2, 700])), '35'), (None, '13')]

// Predecessors: ['12']
13:
if ($a2 > 250) goto 18
Exits: [(COND(EXPR(>[$a2, 250])), '18'), (None, '14')]

// Predecessors: ['13']
14:
if ($a2 == 250) goto 41
Exits: [(COND(EXPR(==[$a2, 250])), '41'), (None, '15')]

// Predecessors: ['14']
15:
if ($a2 == 100) goto 47
Exits: [(COND(EXPR(==[$a2, 100])), '47'), (None, '16')]

// Predecessors: ['15']
16:
if ($a2 == 200) goto 44
Exits: [(COND(EXPR(==[$a2, 200])), '44'), (None, '17')]

// Predecessors: ['16']
17:
goto 49
Exits: [(None, '49')]

// Predecessors: ['13']
18:
if ($a2 == 500) goto 38
Exits: [(COND(EXPR(==[$a2, 500])), '38'), (None, '20')]

// Predecessors: ['18']
20:
goto 49
Exits: [(None, '49')]

// Predecessors: ['10']
21:
if ($a2 == 750) goto 32
Exits: [(COND(EXPR(==[$a2, 750])), '32'), (None, '23')]

// Predecessors: ['21']
23:
if ($a2 == 800) goto 29
Exits: [(COND(EXPR(==[$a2, 800])), '29'), (None, '24')]

// Predecessors: ['23']
24:
if ($a2 == 900) goto 26
Exits: [(COND(EXPR(==[$a2, 900])), '26'), (None, '25')]

// Predecessors: ['24']
25:
goto 49
Exits: [(None, '49')]

// Predecessors: ['24']
26:
$a3 = 900
goto 49
Exits: [(None, '49')]

// Predecessors: ['23']
29:
$a3 = 800
goto 49
Exits: [(None, '49')]

// Predecessors: ['21']
32:
$a3 = 750
goto 49
Exits: [(None, '49')]

// Predecessors: ['12']
35:
$a3 = 700
goto 49
Exits: [(None, '49')]

// Predecessors: ['18']
38:
$a3 = 500
goto 49
Exits: [(None, '49')]

// Predecessors: ['14']
41:
$a3 = 250
goto 49
Exits: [(None, '49')]

// Predecessors: ['16']
44:
$a3 = 200
goto 49
Exits: [(None, '49')]

// Predecessors: ['15']
47:
$a3 = 100
Exits: [(None, '49')]

// Predecessors: ['17', '20', '25', '26', '29', '32', '35', '38', '41', '44', '47']
49:
$a4 = $a1 + $a3
return
Exits: []
