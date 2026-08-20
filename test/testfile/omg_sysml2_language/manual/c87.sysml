action def A { in a1; out a2; }
action def B { in b1; out b2; }
action def C specializes A, B {
  in c1 redefines a1 redefines b1;
  out c2 redefines a2 redefines b2;
}
