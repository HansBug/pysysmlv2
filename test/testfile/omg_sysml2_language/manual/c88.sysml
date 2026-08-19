action def A1 :> A { in aa; } // aa redefines A::a1, A::a2 is inherited.
action def B1 :> B { in b1; out b2; inout b3; } // Redefinitions are implicit.
action def C1 :> A1, B1 { in c1; out c2; inout c3; }
