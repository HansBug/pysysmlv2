action def A specializes Actions::Action {
    in ref x[0..*] subsets Base::things;
    out ref y[0..1] subsets Base::things;
    inout ref z subsets Base::things;
}
action def A1 specializes A {
    in ref x1[1] redefines x;
    out ref y1[1] redefines y;
    // z is inherited without redefinition
}
