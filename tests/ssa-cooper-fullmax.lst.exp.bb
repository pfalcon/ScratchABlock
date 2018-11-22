// Graph props:
//  addr: 00
//  local_defines: {$a, $b, $c, $d, $i, $y, $z}
//  name: B0
//  trailing_jumps: True

// Predecessors: []
// Node props:
//  postno: 9
00:
$i_1 = 1
Exits: [(None, '10')]

// Predecessors: ['00', '30']
// Node props:
//  postno: 8
10:
$a_1 = phi($a_0, $a_9)
$b_1 = phi($b_0, $b_9)
$c_1 = phi($c_0, $c_10)
$d_1 = phi($d_0, $d_10)
$i_2 = phi($i_1, $i_9)
$y_1 = phi($y_0, $y_8)
$z_1 = phi($z_0, $z_8)
$a_2 = func()
$c_2 = func()
if (!($a_2 < $c_2)) goto 50
Exits: [(COND(EXPR(![EXPR(<[$a_2, $c_2])])), '50'), (None, '20')]

// Predecessors: ['10']
// Node props:
//  postno: 7
20:
$a_3 = phi($a_2)
$b_2 = phi($b_1)
$c_3 = phi($c_2)
$d_2 = phi($d_1)
$i_3 = phi($i_2)
$y_2 = phi($y_1)
$z_2 = phi($z_1)
$b_3 = func()
$c_4 = func()
$d_3 = func()
Exits: [(None, '30')]

// Predecessors: ['20', '70']
// Node props:
//  postno: 2
30:
$a_9 = phi($a_3, $a_8)
$b_9 = phi($b_3, $b_8)
$c_10 = phi($c_4, $c_9)
$d_10 = phi($d_3, $d_9)
$i_8 = phi($i_3, $i_7)
$y_7 = phi($y_2, $y_6)
$z_7 = phi($z_2, $z_6)
$y_8 = $a_9 + $b_9
$z_8 = $c_10 + $d_10
$i_9 = $i_8 + 1
if ($i_9 <= 100) goto 10
Exits: [(COND(EXPR(<=[$i_9, 100])), '10'), (None, '40')]

// Predecessors: ['30']
// Node props:
//  postno: 1
40:
$a_10 = phi($a_9)
$b_10 = phi($b_9)
$c_11 = phi($c_10)
$d_11 = phi($d_10)
$i_10 = phi($i_9)
$y_9 = phi($y_8)
$z_9 = phi($z_8)
return
Exits: []

// Predecessors: ['10']
// Node props:
//  postno: 6
50:
$a_4 = phi($a_2)
$b_4 = phi($b_1)
$c_5 = phi($c_2)
$d_4 = phi($d_1)
$i_4 = phi($i_2)
$y_3 = phi($y_1)
$z_3 = phi($z_1)
$a_5 = func()
$d_5 = func()
if (!($a_5 <= $d_5)) goto 80
Exits: [(COND(EXPR(![EXPR(<=[$a_5, $d_5])])), '80'), (None, '60')]

// Predecessors: ['50']
// Node props:
//  postno: 5
60:
$a_6 = phi($a_5)
$b_5 = phi($b_4)
$c_6 = phi($c_5)
$d_6 = phi($d_5)
$i_5 = phi($i_4)
$y_4 = phi($y_3)
$z_4 = phi($z_3)
$d_7 = func()
Exits: [(None, '70')]

// Predecessors: ['60', '80']
// Node props:
//  postno: 3
70:
$a_8 = phi($a_6, $a_7)
$b_7 = phi($b_5, $b_6)
$c_9 = phi($c_6, $c_8)
$d_9 = phi($d_7, $d_8)
$i_7 = phi($i_5, $i_6)
$y_6 = phi($y_4, $y_5)
$z_6 = phi($z_4, $z_5)
$b_8 = func()
goto 30
Exits: [(None, '30')]

// Predecessors: ['50']
// Node props:
//  postno: 4
80:
$a_7 = phi($a_5)
$b_6 = phi($b_4)
$c_7 = phi($c_5)
$d_8 = phi($d_5)
$i_6 = phi($i_4)
$y_5 = phi($y_3)
$z_5 = phi($z_3)
$c_8 = func()
goto 70
Exits: [(None, '70')]
