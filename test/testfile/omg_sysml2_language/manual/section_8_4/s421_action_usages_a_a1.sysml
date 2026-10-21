action a : A subsets Actions::actions {
    in ref x redefines A::x = x1;
    out ref y redefines A::y;
    inout ref z redefines A::z := z1 ;
}

action a1 : A1 subsets a {
    in ref x redefines A1::x, a::x;
    out ref y redefines A2::y, a::y;
}
